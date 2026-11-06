"""Limpieza, transformacion y union de TLC y NOAA. Ejecutar tras 00_descargar.py."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'; OUT=ROOT/'data/processed'; REPORT=ROOT/'reports'

def preparar():
    a=pd.read_csv(RAW/'taxi_2024_extracto_sin_limpiar.csv.gz',low_memory=False)
    manifest=json.loads((RAW/'manifiesto_tlc.json').read_text())
    factors={r['mes']:r['filas_originales']/r['filas_extraidas'] for r in manifest}
    a['peso_muestral']=a.mes_archivo.map(factors)
    for col in ['tpep_pickup_datetime','tpep_dropoff_datetime']:
        a[col]=pd.to_datetime(a[col],errors='coerce')
    a['duracion_min']=(a.tpep_dropoff_datetime-a.tpep_pickup_datetime).dt.total_seconds()/60
    a['velocidad_kmh']=a.trip_distance*1.609344/(a.duracion_min/60)
    rules={
      'Fecha fuera del mes y ano de origen':~(a.tpep_pickup_datetime.dt.year.eq(2024)&a.tpep_pickup_datetime.dt.month.eq(a.mes_archivo)),
      'Duracion no positiva, ausente o superior a 180 min':~a.duracion_min.between(0,180,inclusive='right'),
      'Distancia no positiva, ausente o superior a 100 millas':~a.trip_distance.between(0,100,inclusive='right'),
      'Tarifa o importe no positivo':~(a.fare_amount.gt(0)&a.total_amount.gt(0)),
      'Propina negativa o ausente':~a.tip_amount.ge(0),
      'Velocidad superior a 100 mph':a.velocidad_kmh.gt(160.9344),
    }
    keep=pd.Series(True,index=a.index); audit=[]
    for name,bad in rules.items():
        audit.append({'regla':name,'incidencias':int(bad.sum()),'exclusiones_adicionales':int((keep&bad).sum())})
        keep &= ~bad
    b=a.loc[keep].copy()
    # No se inventan pasajeros ausentes. Los duplicados de contenido no se borran sin ID.
    duplicates=int(b.duplicated(subset=[c for c in a.columns if c not in ['fila_origen','mes_archivo']]).sum())
    localized=b.tpep_pickup_datetime.dt.tz_localize('America/New_York',ambiguous='NaT',nonexistent='NaT')
    ambiguous=int(localized.isna().sum())
    b=b.loc[localized.notna()].copy(); localized=localized.loc[localized.notna()]
    b['fecha_utc']=localized.dt.tz_convert('UTC').dt.strftime('%Y-%m-%d')
    b['fecha_local']=b.tpep_pickup_datetime.dt.strftime('%Y-%m-%d')
    b['hora_local']=b.tpep_pickup_datetime.dt.hour
    b['dia_semana_local']=b.tpep_pickup_datetime.dt.dayofweek
    b['distancia_km']=b.trip_distance*1.609344
    b['tarifa_por_km']=b.fare_amount/b.distancia_km
    b['propina_pct_tarifa']=np.where(b.payment_type.eq(1),100*b.tip_amount/b.fare_amount,np.nan)
    z=pd.read_csv(RAW/'taxi_zone_lookup.csv')
    assert z.LocationID.is_unique
    for side,key in [('origen','PULocationID'),('destino','DOLocationID')]:
        ref=z[['LocationID','Borough','Zone']].rename(columns={'LocationID':key,'Borough':f'borough_{side}','Zone':f'zona_{side}'})
        b=b.merge(ref,on=key,how='left',validate='many_to_one')
        for c in [f'borough_{side}',f'zona_{side}']: b[c]=b[c].fillna('Desconocido')
    w=pd.concat([pd.read_csv(RAW/f'noaa_lga_{y}.csv',dtype={'STATION':str,'FRSHTT':str}) for y in [2024,2025]],ignore_index=True)
    w=w.loc[w.DATE.between('2024-01-01','2025-01-01')].copy()
    assert w.DATE.is_unique
    for col,sentinel in {'TEMP':9999.9,'DEWP':9999.9,'VISIB':999.9,'WDSP':999.9,'PRCP':99.99}.items():
        w[col]=pd.to_numeric(w[col],errors='coerce').replace(sentinel,np.nan)
    weather=pd.DataFrame({'fecha_utc':w.DATE,'estacion_meteo':w.STATION,
       'temperatura_c':(w.TEMP-32)*5/9,'viento_kmh':w.WDSP*1.852,'visibilidad_km':w.VISIB*1.609344,
       'precipitacion_mm':w.PRCP*25.4,'atributo_precipitacion':w.PRCP_ATTRIBUTES,
       'lluvia_indicada':w.FRSHTT.str.zfill(6).str[1].eq('1'),
       'nieve_indicada':w.FRSHTT.str.zfill(6).str[2].eq('1')})
    weather.loc[weather.atributo_precipitacion.eq('I'),'precipitacion_mm']=np.nan
    before=len(b)
    b=b.merge(weather,on='fecha_utc',how='left',validate='many_to_one',indicator=True)
    assert len(b)==before
    unmatched=int(b._merge.ne('both').sum()); assert unmatched==0
    b=b.drop(columns='_merge')
    # Se excluyen de la tabla final los dos dias UTC parciales del periodo local.
    partial=~b.fecha_utc.between('2024-01-02','2024-12-31')
    partial_n=int(partial.sum()); b=b.loc[~partial].copy()
    b['lluvia']=np.where(b.lluvia_indicada,'Lluvia indicada','Sin indicador')
    assert len(b)>=50000 and len(b.columns)>=20
    assert not b.duplicated(['mes_archivo','fila_origen']).any()
    b=b.sort_values(['mes_archivo','tpep_pickup_datetime','fila_origen'])
    b.to_csv(OUT/'taxi_clima_final.csv.xz',index=False,compression={'method':'xz','preset':6})
    b.to_parquet(OUT/'taxi_clima_final.parquet',index=False,compression='zstd',compression_level=12)
    missing=pd.DataFrame({'variable':b.columns,'ausentes':b.isna().sum().values,'porcentaje':b.isna().mean().values*100})
    missing.to_csv(REPORT/'calidad_datos.csv',index=False)
    pd.DataFrame(audit).to_csv(REPORT/'registro_limpieza.csv',index=False)
    validation={'filas_brutas':len(a),'filas_finales':len(b),'columnas_finales':len(b.columns),'dias_utc_completos':int(b.fecha_utc.nunique()),'meses_archivo':int(b.mes_archivo.nunique()),'sin_correspondencia_meteo':unmatched,'horas_DST_ambiguas_o_inexistentes_excluidas':ambiguous,'filas_dias_UTC_parciales_excluidas':partial_n,'coincidencias_exactas_conservadas':duplicates,'registros_fuente_TLC':sum(r['filas_originales'] for r in manifest),'reglas':audit,'muestreo':'50.000 filas aleatorias de cada mes, sin reemplazo, semilla 202400+mes; pesos N_mes/50.000','fecha_inicio_utc':b.fecha_utc.min(),'fecha_fin_utc':b.fecha_utc.max()}
    (REPORT/'validacion_final.json').write_text(json.dumps(validation,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({k:v for k,v in validation.items() if k!='reglas'},indent=2,ensure_ascii=False),flush=True)
    return b

if __name__=='__main__': preparar()

