"""Verificacion de la entrega: datos, modelos, notebook y estructura del Excel."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
a=pd.read_parquet(ROOT/'data/processed/taxi_clima_final.parquet')
v=json.loads((ROOT/'reports/validacion_final.json').read_text(encoding='utf-8'))
s=json.loads((ROOT/'reports/resumen_resultados.json').read_text(encoding='utf-8'))
daily=pd.read_csv(ROOT/'data/processed/resumen_diario.csv')
b=pd.read_csv(ROOT/'data/processed/base_dashboard.csv')
assert a.shape==(v['filas_finales'],v['columnas_finales'])
assert len(a)>=50000 and len(a.columns)>=20
assert len(daily)==365 and daily.fecha_utc.is_unique
assert not a.duplicated(['mes_archivo','fila_origen']).any()
assert a.estacion_meteo.notna().all()
assert np.isclose(a.peso_muestral.sum(),daily.viajes_estimados.sum())
assert np.isclose(a.peso_muestral.sum(),b.viajes_estimados.sum())
assert b.n_muestra.sum()==len(a)
assert np.isclose(a.peso_muestral.sum(),s['poblacion_viajes_validos_estimada'])
assert set(a.mes_archivo)==set(range(1,13))
nb_path=ROOT/'notebooks/EDA_Taxis_Clima_2024.ipynb'
nb=json.loads(nb_path.read_text(encoding='utf-8'))
for i,c in enumerate(nb['cells']):
    c.setdefault('id',f'celda-{i:03}')
    if c['cell_type']=='code':
        assert c['execution_count'] is not None
        assert all(o['output_type']!='error' for o in c['outputs'])
nb_path.write_text(json.dumps(nb,ensure_ascii=False,indent=1),encoding='utf-8')
X={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
book=ROOT/'dashboard/Dashboard_Taxis_Clima_2024.xlsx'
with zipfile.ZipFile(book) as z:
    charts=[x for x in z.namelist() if '/charts/chart' in x and x.endswith('.xml')]
    assert len(charts)==4
    sheet=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    assert len(sheet.findall('.//s:dataValidation',X))==3
    cache={c.attrib['r']:c.find('s:v',X).text if c.find('s:v',X) is not None else None for c in sheet.findall('.//s:c',X)}
    assert abs(float(cache['B11'])-s['poblacion_viajes_validos_estimada'])<.1
    assert abs(float(cache['B15'])-len(a))<.1
    assert abs(float(cache['F11'])-s['duracion_media_min'])<1e-8
    assert abs(float(cache['K15'])*100-s['propina_agregada_pct_tarifa_tarjeta'])<1e-8
    for chart in charts:
        xml=ET.fromstring(z.read(chart))
        assert xml.findall('.//c:f',X)
        if xml.find('.//c:barChart',X) is not None:
            assert any(m.attrib.get('val')=='0' for m in xml.findall('.//c:min',X)),chart
for rel in ['README.md','requirements.txt','reports/Memoria_Taxis_Clima_2024.pdf','reports/Guion_defensa.md','data/raw/taxi_2024_extracto_sin_limpiar.csv.gz','data/raw/noaa_lga_2024.csv']:
    assert (ROOT/rel).is_file(),rel
result={'estado':'Verificaciones superadas','filas_finales':len(a),'columnas_finales':len(a.columns),'dias':len(daily),'graficos_excel':4,'selectores_excel':3,'celdas_notebook_ejecutadas':sum(c['cell_type']=='code' for c in nb['cells']),'total_dashboard_conciliado':float(cache['B11']),'poblacion_estimada':True,'limite':'Prueba de formulas con motor de generacion y del XML exportado; no sesion nativa de Excel.'}
(ROOT/'reports/verificacion_entrega.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))

