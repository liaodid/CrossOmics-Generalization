"""Download public primary sources and validate paper PDFs (standard library + pypdf)."""
import concurrent.futures as cf
import hashlib
import http.cookiejar
import io
import json
import re
import time
import urllib.parse as up
import urllib.request as ur
import xml.etree.ElementTree as ET
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'tmp/literature'
OUT = ROOT / 'pdf'
PAPERS = [
 ('transpro','10.1016/j.crmeth.2023.100452'),
 ('multipert','10.1371/journal.pcbi.1014054'),
 ('proteintalks','10.1038/s41586-026-11001-9'),
 ('unipert-g2cp','10.1016/j.cell.2026.06.005'),
 ('state','10.1016/j.cell.2026.07.052'),
 ('tahoe-100m','10.1016/j.cell.2026.08.035'),
 ('robotic-proteomics','10.64898/2026.05.04.722718'),
 ('degrader-proteomics','10.1038/s41589-026-02347-2'),
 ('linear-baselines','10.1038/s41592-025-02772-6'),
 ('xpert','10.1038/s42256-025-01165-w'),
 ('perturbnet','10.1038/s44320-025-00131-3'),
 ('chemcpa',''),
 ('cpa','10.15252/msb.202211517'),
 ('gears','10.1038/s41587-023-01905-6'),
 ('biolord','10.1038/s41587-023-02079-x'),
 ('totalvi','10.1038/s41592-020-01050-x'),
 ('multivi','10.1038/s41592-023-01909-9'),
 ('l1000','10.1016/j.cell.2017.10.049'),
]
EXTRA = {
 'chemcpa':['https://proceedings.nips.cc/paper_files/paper/2022/file/aa933b5abc1be30baece1d230ec575a7-Paper-Conference.pdf'],
 'gears':['https://www-cs.stanford.edu/~jure/pubs/gears-natbio23.pdf'],
 'cpa':['https://mediatum.ub.tum.de/doc/1725023/1725023.pdf'],
 'totalvi':['https://escholarship.org/content/qt24f8f9g4/qt24f8f9g4_noSplash_7b2fe617b4553bd0034b54840b3f5222.pdf'],
}

def get(url):
    req = ur.Request(url, headers={'User-Agent':'Mozilla/5.0 (academic literature collection)'})
    opener=ur.build_opener(ur.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    with opener.open(req, timeout=25) as r:
        return r.read(), r.geturl()

def collect(item):
    key, doi = item
    cached=CACHE/(key+'.json')
    if (OUT/(key+'.pdf')).exists() and cached.exists():
        return json.loads(cached.read_text(encoding='utf-8'))
    row = {'key':key,'doi':doi,'attempts':[],'pdf_status':'unavailable'}
    urls = list(EXTRA.get(key, []))
    if doi:
        try:
            meta=json.loads(get('https://api.crossref.org/works/'+up.quote(doi,safe=''))[0])['message']
            row['crossref']=meta
            urls += [v['URL'] for v in meta.get('link',[]) if v.get('content-type')=='application/pdf']
        except Exception as e: row['attempts'].append({'crossref':str(e)})
        try:
            data=json.loads(get('https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&query='+up.quote('DOI:"'+doi+'"'))[0])
            hits=data['resultList']['result']
            if hits:
                row['europepmc']=hits[0]
                pmc=hits[0].get('pmcid')
                if pmc:
                    try:
                        xml=get('https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmc+'/fullTextXML')[0]
                        (CACHE/(key+'.xml')).write_bytes(xml)
                        root=ET.fromstring(xml)
                        (CACHE/(key+'.source.txt')).write_text('\n'.join(' '.join(e.itertext()) for e in root.findall('.//article-title')+root.findall('.//abstract')+root.findall('.//body')),encoding='utf-8')
                        urls += ['https://europepmc.org/articles/'+pmc+'?pdf=render','https://pmc.ncbi.nlm.nih.gov/articles/'+pmc+'/pdf/']
                    except Exception as e: row['attempts'].append({'xml':str(e)})
        except Exception as e: row['attempts'].append({'epmc':str(e)})
        if doi.startswith('10.1038/'):
            urls.insert(0,'https://www.nature.com/articles/'+doi.split('/')[1]+'.pdf')
        if doi.startswith('10.1371/'):
            urls.insert(0,'https://journals.plos.org/ploscompbiol/article/file?id='+doi+'&type=printable')
    for url in dict.fromkeys(urls):
        try:
            data, final=get(url)
            if not data.startswith(b'%PDF-'): raise ValueError('response is not PDF')
            reader=PdfReader(io.BytesIO(data))
            texts=[p.extract_text() or '' for p in reader.pages]
            if not texts or len(''.join(texts))<200: raise ValueError('PDF lacks readable article text')
            path=OUT/(key+'.pdf')
            if path.exists(): raise ValueError('refusing overwrite of existing file')
            path.write_bytes(data)
            (CACHE/(key+'.pdf.txt')).write_text('\n\n'.join(texts),encoding='utf-8')
            row.update(pdf_status='downloaded',pdf_file=path.name,pdf_url=final,pages=len(texts),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
            break
        except Exception as e: row['attempts'].append({'url':url,'error':str(e)})
    (CACHE/(key+'.json')).write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8')
    print(key,row['pdf_status'],row.get('pages',''),flush=True)
    return row

def main():
    CACHE.mkdir(parents=True,exist_ok=True)
    OUT.mkdir(exist_ok=True)
    try:
        data,_=get('https://raw.githubusercontent.com/liaodid/CrossOmics-Generalization/6464fb0aac7084a5df2ff01e4709b3430c00d772/README.md')
        (CACHE/'remote-README.md').write_bytes(data)
        print('remote README retrieved',flush=True)
    except Exception as e: print('remote README:',e,flush=True)
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(collect,PAPERS))
    (OUT/'download_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__': main()
