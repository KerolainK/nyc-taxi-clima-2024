"""Descarga TLC 2024 y conserva un extracto sin limpiar, estratificado por mes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request, shutil, hashlib, json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'
ARCH=RAW/'originales'
ARCH.mkdir(exist_ok=True)
BASE='https://d37ci6vzurychx.cloudfront.net/trip-data/'
def download(month):
    name=f'yellow_tripdata_2024-{month:02}.parquet'
    dest=ARCH/name
    if not dest.exists():
        if month==1 and (RAW/name).exists(): shutil.copy2(RAW/name,dest)
        else:
            with urllib.request.urlopen(BASE+name,timeout=120) as response, open(dest.with_suffix('.part'),'wb') as target:
                shutil.copyfileobj(response,target)
            dest.with_suffix('.part').replace(dest)
    return month,dest
with ThreadPoolExecutor(max_workers=4) as pool:
    downloaded=list(pool.map(download,range(1,13)))
print('Descargados los doce meses',flush=True)
frames=[]; manifest=[]
for month,path in sorted(downloaded):
    df=pd.read_parquet(path)
    n=len(df)
    sampled=df.sample(n=min(50000,n),random_state=202400+month).copy()
    sampled.insert(0,'fila_origen',sampled.index)
    sampled.insert(0,'mes_archivo',month)
    frames.append(sampled)
    manifest.append({'mes':month,'url':BASE+path.name,'filas_originales':n,'filas_extraidas':len(sampled),'semilla':202400+month,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    print(f'Mes {month:02}: {n:,} filas, muestra {len(sampled):,}',flush=True)
raw_sample=pd.concat(frames,ignore_index=True)
raw_sample.to_csv(RAW/'taxi_2024_extracto_sin_limpiar.csv.gz',index=False,compression={'method':'gzip','compresslevel':1,'mtime':0})
(RAW/'manifiesto_tlc.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
for year in [2024,2025]:
    target=RAW/f'noaa_lga_{year}.csv'
    if not target.exists():
        urllib.request.urlretrieve(f'https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/{year}/72503014732.csv',target)
print('Extracto bruto guardado: '+str(raw_sample.shape),flush=True)
