"""EDA ponderado, modelos diarios con HAC y salidas para Excel y memoria."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'reports'; FIG=REPORT/'figuras'; FIG.mkdir(exist_ok=True)

def analizar():
    a=pd.read_parquet(ROOT/'data/processed/taxi_clima_final.parquet')
    w=a.peso_muestral
    def mean(col,frame=a):
        q=frame[[col,'peso_muestral']].dropna()
        return float(np.average(q[col],weights=q.peso_muestral))
    def quant(col,p,frame=a):
        q=frame[[col,'peso_muestral']].dropna().sort_values(col)
        c=q.peso_muestral.cumsum(); return float(np.interp(p*c.iloc[-1],c,q[col]))
    cards=a[a.payment_type.eq(1)]
    summary={'n':len(a),'poblacion_viajes_validos_estimada':float(w.sum()),
       'duracion_media_min':mean('duracion_min'),'duracion_mediana_min':quant('duracion_min',.5),
       'distancia_media_km':mean('distancia_km'),'tarifa_mediana_usd':quant('fare_amount',.5),
       'importe_medio_usd':mean('total_amount'),'tarjeta_porcentaje':float(100*a.loc[a.payment_type.eq(1),'peso_muestral'].sum()/w.sum()),
       'propina_agregada_pct_tarifa_tarjeta':float(100*(cards.tip_amount*cards.peso_muestral).sum()/(cards.fare_amount*cards.peso_muestral).sum())}
    for col in ['duracion_min','distancia_km','fare_amount','total_amount','velocidad_kmh','propina_pct_tarifa']:
        summary[col]={'media':mean(col),'p01':quant(col,.01),'p25':quant(col,.25),'mediana':quant(col,.5),'p75':quant(col,.75),'p99':quant(col,.99)}
    a['w_duracion']=a.duracion_min*w; a['w_distancia']=a.distancia_km*w
    a['w_tarifa']=a.fare_amount*w; a['w_importe']=a.total_amount*w
    a['w_tarjeta']=np.where(a.payment_type.eq(1),w,0)
    a['w_propina_tarjeta']=np.where(a.payment_type.eq(1),a.tip_amount*w,0)
    a['w_tarifa_tarjeta']=np.where(a.payment_type.eq(1),a.fare_amount*w,0)
    daily=a.groupby('fecha_utc',as_index=False).agg(viajes_estimados=('peso_muestral','sum'),n_muestra=('fila_origen','size'),duracion_suma=('w_duracion','sum'),distancia_suma=('w_distancia','sum'),tarifa_suma=('w_tarifa','sum'),importe_suma=('w_importe','sum'),tarjeta_suma=('w_tarjeta','sum'),propina_suma=('w_propina_tarjeta','sum'),tarifa_tarjeta_suma=('w_tarifa_tarjeta','sum'),temperatura_c=('temperatura_c','first'),viento_kmh=('viento_kmh','first'),lluvia_indicada=('lluvia_indicada','first'),nieve_indicada=('nieve_indicada','first'),precipitacion_mm=('precipitacion_mm','first'))
    daily['duracion_media']=daily.duracion_suma/daily.viajes_estimados
    daily['distancia_media']=daily.distancia_suma/daily.viajes_estimados
    daily['propina_pct']=100*daily.propina_suma/daily.tarifa_tarjeta_suma
    daily['fecha']=pd.to_datetime(daily.fecha_utc)
    daily['mes']=daily.fecha.dt.month; daily['dia_semana']=daily.fecha.dt.dayofweek
    daily['lluvia_num']=daily.lluvia_indicada.astype(int)
    daily['nieve_num']=daily.nieve_indicada.astype(int)
    daily.to_csv(ROOT/'data/processed/resumen_diario.csv',index=False)
    formulas={
      'Volumen diario estimado':'np.log(viajes_estimados) ~ lluvia_num + temperatura_c + nieve_num + C(mes) + C(dia_semana)',
      'Duracion media diaria':'np.log(duracion_media) ~ lluvia_num + temperatura_c + nieve_num + np.log(distancia_media) + C(mes) + C(dia_semana)',
      'Propina diaria sobre tarifa (tarjeta)':'propina_pct ~ lluvia_num + temperatura_c + nieve_num + C(mes) + C(dia_semana)'}
    results=[]
    for label,formula in formulas.items():
        model=smf.ols(formula,data=daily).fit(cov_type='HAC',cov_kwds={'maxlags':7})
        beta=float(model.params['lluvia_num']); low,high=model.conf_int().loc['lluvia_num']
        logarithmic=label!='Propina diaria sobre tarifa (tarjeta)'
        conv=lambda x: float(100*np.expm1(x)) if logarithmic else float(x)
        results.append({'modelo':label,'beta':beta,'efecto':conv(beta),'ic95_inferior':conv(low),'ic95_superior':conv(high),'unidad':'%' if logarithmic else 'puntos porcentuales','p_sin_ajustar':float(model.pvalues['lluvia_num']),'n_dias':int(model.nobs),'r2':float(model.rsquared),'formula':formula})
        (REPORT/('modelo_'+str(len(results))+'.txt')).write_text(model.summary().as_text(),encoding='utf-8')
    adjusted=multipletests([r['p_sin_ajustar'] for r in results],method='holm')[1]
    for r,p in zip(results,adjusted): r['p_holm']=float(p)
    pd.DataFrame(results).to_csv(REPORT/'resultados_estadisticos.csv',index=False)
    summary['modelos']=results
    summary['dias_lluvia']=int(daily.lluvia_num.sum());summary['dias_sin_lluvia']=int((daily.lluvia_num==0).sum())
    summary['sensibilidad']={}
    # Sensibilidad descriptiva al limite de duracion: se repite el modelo de volumen.
    for limit in [120,240]:
        if limit==240: continue # no se recuperan observaciones fuera del filtro original.
        subset=a[a.duracion_min.le(limit)]
        alternative=subset.groupby('fecha_utc').peso_muestral.sum()
        temp=daily.copy();temp['viajes_estimados']=temp.fecha_utc.map(alternative)
        fit=smf.ols(formulas['Volumen diario estimado'],data=temp).fit(cov_type='HAC',cov_kwds={'maxlags':7})
        summary['sensibilidad'][f'duracion_max_{limit}min']={'n':len(subset),'efecto_lluvia_pct':float(100*np.expm1(fit.params['lluvia_num']))}
    summary['dias_extremos']=daily.nlargest(5,'viajes_estimados')[['fecha_utc','viajes_estimados']].to_dict('records')
    # Datos de dashboard: agregacion exhaustiva del conjunto final, sin redondear pesos.
    agg=a.groupby(['mes_archivo','borough_origen','lluvia','hora_local'],as_index=False).agg(n_muestra=('fila_origen','size'),viajes_estimados=('peso_muestral','sum'),duracion_suma=('w_duracion','sum'),distancia_suma=('w_distancia','sum'),tarifa_suma=('w_tarifa','sum'),importe_suma=('w_importe','sum'),tarjeta_suma=('w_tarjeta','sum'),propina_suma=('w_propina_tarjeta','sum'),tarifa_tarjeta_suma=('w_tarifa_tarjeta','sum'))
    def serial(date): return (pd.Timestamp(date)-pd.Timestamp('1899-12-30')).days
    meses=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
    agg.insert(0,'mes',agg.mes_archivo.map(dict(enumerate(meses,1))))
    agg.to_csv(ROOT/'data/processed/base_dashboard.csv',index=False)
    dashboard={'headers':agg.columns.tolist(),'rows':json.loads(agg.to_json(orient='values')),'summary':summary,'boroughs':sorted(a.borough_origen.unique().tolist())}
    (ROOT/'dashboard/datos_dashboard.json').write_text(json.dumps(dashboard,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    # Figuras: cada una responde a una pregunta y explicita unidades.
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold'})
    navy='#20364a'; yellow='#edb833'; teal='#177e89'
    def save(fig,name):
        fig.savefig(FIG/name,dpi=170,bbox_inches='tight');plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,4))
    monthly=a.groupby('mes_archivo').peso_muestral.sum()
    ax.bar(monthly.index,monthly.values/1e6,color=yellow)
    ax.set(title='Actividad mensual estimada de taxis amarillos',xlabel='Mes de origen del archivo (2024)',ylabel='Millones de viajes válidos estimados',xticks=range(1,13));ax.grid(axis='y',alpha=.15)
    save(fig,'01_actividad_mensual.png')
    fig,axs=plt.subplots(1,2,figsize=(11,4))
    axs[0].hist(a.duracion_min,bins=np.arange(0,91,2),weights=w,color=navy)
    axs[0].set(title='Duración de los viajes',xlabel='Minutos (se muestra hasta 90)',ylabel='Frecuencia ponderada')
    axs[1].hist(a.fare_amount,bins=np.arange(0,161,4),weights=w,color=yellow)
    axs[1].set(title='Tarifa base solicitada',xlabel='USD (se muestra hasta 160)',ylabel='Frecuencia ponderada')
    fig.tight_layout();save(fig,'02_distribuciones.png')
    fig,axs=plt.subplots(2,1,figsize=(11,6),sharex=True)
    axs[0].plot(daily.fecha,daily.viajes_estimados/1000,color=navy,lw=.8)
    rain=daily[daily.lluvia_indicada]
    axs[0].scatter(rain.fecha,rain.viajes_estimados/1000,s=8,color=teal,label='Día con lluvia indicada')
    axs[0].set(title='Actividad diaria y contexto meteorológico',ylabel='Miles de viajes estimados');axs[0].legend(fontsize=8)
    axs[1].plot(daily.fecha,daily.temperatura_c,color=teal,lw=1)
    axs[1].set(ylabel='Temperatura media (°C)',xlabel='Día UTC completo, 2024')
    fig.tight_layout();save(fig,'03_serie_diaria.png')
    fig,ax=plt.subplots(figsize=(10,4))
    hourly=a.groupby(['lluvia','hora_local']).peso_muestral.sum().unstack(0)
    # Se divide por dias de cada categoria: comparar totales sin esta division seria incorrecto.
    for label,color,n in [('Lluvia indicada',teal,summary['dias_lluvia']),('Sin indicador',yellow,summary['dias_sin_lluvia'])]:
        ax.plot(hourly.index,hourly[label]/n,marker='o',markersize=3,color=color,label=f'{label} ({n} días)')
    ax.set(title='Viajes medios por día y hora local',xlabel='Hora local de Nueva York',ylabel='Viajes estimados / día UTC de la categoría',xticks=range(0,24,2));ax.legend();ax.grid(alpha=.12)
    save(fig,'04_perfil_horario.png')
    fig,ax=plt.subplots(figsize=(9,4))
    borough=a.groupby('borough_origen').peso_muestral.sum().sort_values()
    ax.barh(borough.index,100*borough/w.sum(),color=navy)
    ax.set(title='Distribución de los viajes según borough de origen',xlabel='Porcentaje ponderado de viajes válidos')
    save(fig,'05_boroughs.png')
    fig,axs=plt.subplots(1,3,figsize=(12,3.7))
    for ax,r in zip(axs,results):
        ax.axvline(0,color='#aaaaaa',lw=1)
        ax.errorbar([r['efecto']],[0],xerr=[[r['efecto']-r['ic95_inferior']],[r['ic95_superior']-r['efecto']]],fmt='o',color=teal,capsize=5)
        ax.set(title=r['modelo'].replace(' diario estimado','').replace(' diaria','').replace(' (tarjeta)',''),xlabel=f'Diferencia ajustada por lluvia ({r["unidad"]})',yticks=[],ylim=(-1,1))
    fig.suptitle('Asociaciones ajustadas: estimación e IC del 95% (HAC, 7 días)',fontsize=12)
    fig.tight_layout();save(fig,'06_modelos.png')
    # Correlacion descriptiva ponderada entre variables de viaje. Sin p-valores ingenuos.
    cols=['duracion_min','distancia_km','fare_amount','total_amount','velocidad_kmh']
    cov=np.cov(a[cols].to_numpy().T,aweights=w);corr=cov/np.sqrt(np.outer(np.diag(cov),np.diag(cov)))
    pd.DataFrame(corr,index=cols,columns=cols).to_csv(REPORT/'correlaciones_ponderadas.csv')
    fig,ax=plt.subplots(figsize=(7,5))
    im=ax.imshow(corr,cmap='RdBu_r',vmin=-1,vmax=1)
    labels=['Duración','Distancia','Tarifa','Importe total','Velocidad']
    ax.set(xticks=range(5),xticklabels=labels,yticks=range(5),yticklabels=labels,title='Correlaciones de Pearson ponderadas')
    for i in range(5):
        for j in range(5):ax.text(j,i,f'{corr[i,j]:.2f}',ha='center',va='center',color='white' if abs(corr[i,j])>.6 else 'black')
    fig.colorbar(im,ax=ax);fig.tight_layout();save(fig,'07_correlaciones.png')
    (REPORT/'resumen_resultados.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k in ['n','poblacion_viajes_validos_estimada','dias_lluvia','dias_sin_lluvia','modelos','sensibilidad']},indent=2,ensure_ascii=False),flush=True)
    return summary,daily
if __name__=='__main__':analizar()


