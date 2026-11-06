"""Create ZIP64 research snapshots, with per-file SHA256 and full read-back checks.

Usage: python script/package_research_transfer.py --output transfer-YYYY-MM-DD ROOT [ROOT ...]
Archives include source and ignored research files. Git metadata and Python bytecode
are excluded; the output directory is always excluded to prevent self-inclusion.
"""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import zipfile


BLOCK = 4 * 1024 * 1024


def digest_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(BLOCK), b''):
            digest.update(block)
    return digest.hexdigest()


def pack(root, output):
    root = root.resolve(strict=True)
    archive = output / (root.name + '.zip')
    if archive.exists():
        raise FileExistsError(archive)
    files, excluded = [], []
    for directory, folders, names in os.walk(root, followlinks=False):
        parent = Path(directory)
        for name in list(folders):
            child = parent / name
            if name in ('.git', '__pycache__') or child.resolve() == output or child.is_symlink():
                folders.remove(name)
                excluded.append(str(child.relative_to(root)) + '/')
        for name in names:
            path = parent / name
            if path.suffix in ('.pyc', '.pyo') or path.is_symlink():
                excluded.append(str(path.relative_to(root)))
            else:
                files.append(path)
    files.sort()
    records = []
    total = sum(path.stat().st_size for path in files)
    print(f'Packing {root}: {len(files)} files, {total / 1024**3:.3f} GiB', flush=True)
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=3, allowZip64=True) as zipped:
        for index, path in enumerate(files, 1):
            before = path.stat()
            member = root.name + '/' + path.relative_to(root).as_posix()
            info = zipfile.ZipInfo.from_file(path, arcname=member)
            info.compress_type = zipfile.ZIP_DEFLATED
            digest = hashlib.sha256()
            size = 0
            with path.open('rb') as source, zipped.open(info, 'w', force_zip64=True) as target:
                for block in iter(lambda: source.read(BLOCK), b''):
                    target.write(block)
                    digest.update(block)
                    size += len(block)
            after = path.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns) or size != before.st_size:
                raise RuntimeError(f'Source changed during backup: {path}')
            records.append(dict(path=member, bytes=size, sha256=digest.hexdigest()))
            if index % 2000 == 0:
                print(f'  Written {index}/{len(files)}', flush=True)
        manifest = io.StringIO(newline='')
        writer = csv.DictWriter(manifest, fieldnames=['path', 'bytes', 'sha256'])
        writer.writeheader()
        writer.writerows(records)
        zipped.writestr('_transfer_metadata/manifest.csv', manifest.getvalue().encode('utf-8-sig'))
        zipped.writestr('_transfer_metadata/exclusions.json', json.dumps(excluded, ensure_ascii=False, indent=2))
    print(f'Verifying every archived file: {archive.name}', flush=True)
    with zipfile.ZipFile(archive) as zipped:
        expected = {record['path'] for record in records}
        expected.update(('_transfer_metadata/manifest.csv', '_transfer_metadata/exclusions.json'))
        names = zipped.namelist()
        if len(names) != len(expected) or set(names) != expected:
            raise RuntimeError('Archive member list mismatch')
        # Reading to EOF verifies ZIP CRC as well as the independently recorded SHA256.
        for index, record in enumerate(records, 1):
            digest = hashlib.sha256()
            size = 0
            with zipped.open(record['path']) as source:
                for block in iter(lambda: source.read(BLOCK), b''):
                    digest.update(block)
                    size += len(block)
            if size != record['bytes'] or digest.hexdigest() != record['sha256']:
                raise RuntimeError(f'Archive verification failed: {record["path"]}')
            if index % 4000 == 0:
                print(f'  Verified {index}/{len(records)}', flush=True)
        for name in ('_transfer_metadata/manifest.csv', '_transfer_metadata/exclusions.json'):
            zipped.read(name)
    (output / (root.name + '.manifest.csv')).write_bytes(manifest.getvalue().encode('utf-8-sig'))
    result = dict(source=str(root), archive=archive.name, files=len(files),
                  source_bytes=total, archive_bytes=archive.stat().st_size,
                  sha256=digest_file(archive), verified=True, exclusions=excluded)
    print(json.dumps({key: value for key, value in result.items() if key != 'exclusions'}, ensure_ascii=False), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('roots', nargs='+', type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    roots = [root.resolve(strict=True) for root in args.roots]
    if len({root.name.casefold() for root in roots}) != len(roots):
        parser.error('Root folder names must be distinct')
    output.mkdir(parents=True, exist_ok=True)
    results = [pack(root, output) for root in roots]
    (output / 'transfer_summary.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    (output / 'SHA256SUMS.txt').write_text(''.join(f'{r["sha256"]}  {r["archive"]}\n' for r in results), encoding='utf-8')


if __name__ == '__main__':
    main()
