"""Retry author/repository PDF links without replacing existing papers."""
import concurrent.futures as cf
import hashlib
import io
import json
import re
import urllib.parse as up
from collect_literature import ROOT,CACHE,OUT,get
from pypdf import PdfReader

LINKS={
 'transpro':['https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC10163019','https://pmc.ncbi.nlm.nih.gov/articles/PMC10163019/','https://www.cell.com/cell-reports-methods/pdf/S2667-2375(23)00071-1.pdf'],
 'proteintalks':['https://www.nature.com/articles/s41586-026-11001-9.pdf?download=1','https://link.springer.com/content/pdf/10.1038/s41586-026-11001-9.pdf','https://www.biorxiv.org/content/10.1101/2025.02.07.637070v1.full.pdf'],
 'unipert-g2cp':['https://www.cell.com/cell/pdf/S0092-8674(26)00654-9.pdf','https://www.biorxiv.org/content/10.1101/2025.02.02.635055v2.full.pdf'],
 'state':['https://www.cell.com/cell/pdf/S0092-8674(26)00921-9.pdf','https://www.biorxiv.org/content/10.1101/2025.06.26.661135v1.full.pdf'],
 'tahoe-100m':['https://www.cell.com/cell/pdf/S0092-8674(26)01008-1.pdf','https://www.biorxiv.org/content/10.1101/2025.02.20.639398v2.full.pdf'],
 'robotic-proteomics':['https://pmc.ncbi.nlm.nih.gov/articles/PMC13174343/','https://www.biorxiv.org/content/10.64898/2026.05.04.722718v1.full.pdf'],
 'degrader-proteomics':['https://link.springer.com/content/pdf/10.1038/s41589-026-02347-2.pdf'],
 'linear-baselines':['https://d-nb.info/1378241509/34','https://link.springer.com/content/pdf/10.1038/s41592-025-02772-6.pdf'],
 'xpert':['https://link.springer.com/content/pdf/10.1038/s42256-025-01165-w.pdf'],
 'perturbnet':['https://pmc.ncbi.nlm.nih.gov/articles/PMC12322087/','https://link.springer.com/content/pdf/10.1038/s44320-025-00131-3.pdf'],
 'chemcpa':['https://arxiv.org/pdf/2204.13545'],
 'cpa':['https://pmc.ncbi.nlm.nih.gov/articles/PMC10258562/'],
 'gears':['https://www-cs.stanford.edu/~jure/pubs/gears-natbio23.pdf'],
 'biolord':['https://link.springer.com/content/pdf/10.1038/s41587-023-02079-x.pdf'],
 'totalvi':['https://pmc.ncbi.nlm.nih.gov/articles/PMC7954949/'],
 'multivi':['https://pmc.ncbi.nlm.nih.gov/articles/PMC10406609/','https://link.springer.com/content/pdf/10.1038/s41592-023-01909-9.pdf'],
 'l1000':['https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC5990023','https://pmc.ncbi.nlm.nih.gov/articles/PMC5990023/','https://www.cell.com/cell/pdf/S0092-8674(17)31309-0.pdf'],
}

def run(item):
    key,urls=item
    jf=CACHE/(key+'.json')
    row=json.loads(jf.read_text(encoding='utf-8')) if jf.exists() else {'key':key,'attempts':[],'pdf_status':'unavailable'}
    if (OUT/(key+'.pdf')).exists(): return row
    queue=list(urls)
    while queue:
        url=queue.pop(0)
        try:
            data,final=get(url)
            if b'<OA>' in data or b'<OA ' in data:
                import tarfile
                packages=re.findall(rb'href="(ftp://[^\"]+\.tar\.gz)"',data)
                if packages:
                    package,download_url=get(packages[0].decode().replace('ftp://','https://'))
                    with tarfile.open(fileobj=io.BytesIO(package),mode='r:gz') as archive:
                        member=next(m for m in archive.getmembers() if m.name.endswith('.pdf'))
                        data=archive.extractfile(member).read()
                        final=download_url+'#'+member.name
            if not data.startswith(b'%PDF-'):
                html=data.decode('utf-8',errors='replace')
                (CACHE/(key+'.html')).write_text(html,encoding='utf-8')
                matches=re.findall(r'href=[\"\x27]([^\"\x27]*?/pdf/[^\"\x27]*|[^\"\x27]*\.pdf(?:\?[^\"\x27]*)?)[\"\x27]',html)
                if '/articles/PMC' in url and matches:
                    queue[0:0]=[up.urljoin(final,m.replace('&amp;','&')) for m in matches[:3]]
                    continue
                raise ValueError('HTML returned instead of PDF')
            reader=PdfReader(io.BytesIO(data))
            texts=[p.extract_text() or '' for p in reader.pages]
            if len(''.join(texts))<200: raise ValueError('no readable article text')
            (OUT/(key+'.pdf')).write_bytes(data)
            (CACHE/(key+'.pdf.txt')).write_text('\n\n'.join(texts),encoding='utf-8')
            row.update(pdf_status='downloaded',pdf_file=key+'.pdf',pdf_url=final,pages=len(texts),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
            break
        except Exception as e: row['attempts'].append({'url':url,'error':str(e)})
    jf.write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8')
    print(key,row['pdf_status'],row.get('pages',''),flush=True)
    return row

if __name__=='__main__':
    with cf.ThreadPoolExecutor(max_workers=6) as pool: list(pool.map(run,LINKS.items()))
    rows=[json.loads(p.read_text(encoding='utf-8')) for p in CACHE.glob('*.json')]
    (OUT/'download_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
