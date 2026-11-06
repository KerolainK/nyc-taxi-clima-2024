"""Ampliacion analitica: calendario, diagnosticos, sensibilidad y patrones operativos."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import acorr_ljungbox,het_breuschpagan
from statsmodels.stats.stattools import durbin_watson
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'reports';F=R/'figuras'

def profundizar():
    a=pd.read_parquet(ROOT/'data/processed/taxi_clima_final.parquet')
    d=pd.read_csv(ROOT/'data/processed/resumen_diario.csv')
    d['fecha']=pd.to_datetime(d.fecha_utc)
    dates=['2024-01-01','2024-01-15','2024-02-19','2024-05-27','2024-06-19','2024-07-04','2024-09-02','2024-10-14','2024-11-11','2024-11-28','2024-12-25']
    names=['Ano Nuevo','Martin Luther King Jr.','Washington','Memorial Day','Juneteenth','Independencia','Labor Day','Columbus Day','Veteranos','Accion de Gracias','Navidad']
    pd.DataFrame({'fecha':dates,'festivo':names,'fuente':'https://content.govdelivery.com/accounts/USDHSCBP/bulletins/38366be'}).to_csv(ROOT/'data/raw/festivos_federales_2024.csv',index=False)
    d['festivo']=d.fecha_utc.isin(dates).astype(int)
    d['dia_ano']=d.fecha.dt.dayofyear
    d['log_volumen_lag1']=np.log(d.viajes_estimados).shift(1)
    formula='np.log(viajes_estimados) ~ lluvia_num + temperatura_c + nieve_num + C(mes) + C(dia_semana)'
    plain=smf.ols(formula,data=d).fit(); influence=plain.get_influence()
    cooks=influence.cooks_distance[0]
    infl=pd.DataFrame({'fecha_utc':d.fecha_utc,'distancia_cook':cooks,'residuo_estandarizado':influence.resid_studentized_internal,'festivo':d.festivo})
    top=infl.nlargest(5,'distancia_cook')
    top.to_csv(R/'dias_influyentes.csv',index=False)
    models=[]
    for k in [3,7,14]:models.append((f'HAC {k} dias',smf.ols(formula,data=d).fit(cov_type='HAC',cov_kwds={'maxlags':k})))
    models.append(('Con festivos federales',smf.ols(formula+' + festivo',data=d).fit(cov_type='HAC',cov_kwds={'maxlags':7})))
    near=set()
    for date in pd.to_datetime(dates):
        for delta in [-1,0,1]:near.add((date+pd.Timedelta(days=delta)).strftime('%Y-%m-%d'))
    models.append(('Sin festivos ni dias adyacentes',smf.ols(formula,data=d[~d.fecha_utc.isin(near)]).fit(cov_type='HAC',cov_kwds={'maxlags':7})))
    models.append(('Sin cinco dias mas influyentes',smf.ols(formula,data=d[~d.fecha_utc.isin(top.fecha_utc)]).fit(cov_type='HAC',cov_kwds={'maxlags':7})))
    models.append(('Tendencia estacional flexible',smf.ols('np.log(viajes_estimados) ~ lluvia_num + temperatura_c + nieve_num + bs(dia_ano, df=8) + C(dia_semana) + festivo',data=d).fit(cov_type='HAC',cov_kwds={'maxlags':7})))
    models.append(('Con volumen del dia anterior',smf.ols(formula+' + log_volumen_lag1 + festivo',data=d).fit(cov_type='HAC',cov_kwds={'maxlags':7})))
    results=[]
    for label,m in models:
        lo,hi=m.conf_int().loc['lluvia_num'];beta=m.params['lluvia_num']
        results.append({'especificacion':label,'efecto_pct':100*np.expm1(beta),'ic95_inferior':100*np.expm1(lo),'ic95_superior':100*np.expm1(hi),'p_exploratorio':m.pvalues['lluvia_num'],'n_dias':int(m.nobs)})
    sensitivity=pd.DataFrame(results);sensitivity.to_csv(R/'sensibilidad_ampliada.csv',index=False)
    diagnostics=[]
    specs={
       'Volumen':formula,
       'Duracion':'np.log(duracion_media) ~ lluvia_num + temperatura_c + nieve_num + np.log(distancia_media) + C(mes) + C(dia_semana)',
       'Volumen dinamico':formula+' + log_volumen_lag1 + festivo',
       'Propina':'propina_pct ~ lluvia_num + temperatura_c + nieve_num + C(mes) + C(dia_semana)'}
    for name,f in specs.items():
        m=smf.ols(f,data=d).fit();lb=acorr_ljungbox(m.resid,lags=[7,14],return_df=True)
        bp=het_breuschpagan(m.resid,m.model.exog)
        diagnostics.append({'modelo':name,'durbin_watson':durbin_watson(m.resid),'ljung_box_p7':lb.loc[7,'lb_pvalue'],'ljung_box_p14':lb.loc[14,'lb_pvalue'],'breusch_pagan_p':bp[1],'max_cook':m.get_influence().cooks_distance[0].max(),'r2_ajustado':m.rsquared_adj,'numero_condicion':m.condition_number})
    pd.DataFrame(diagnostics).to_csv(R/'diagnosticos_modelos.csv',index=False)
    a['tipo_dia']=np.where(a.dia_semana_local.ge(5),'Fin semana','Lun-vie')
    w=a.peso_muestral
    for dest,col in [('w_duracion','duracion_min'),('w_distancia','distancia_km'),('w_tarifa','fare_amount'),('w_importe','total_amount')]:a[dest]=a[col]*w
    a['w_tarjeta']=np.where(a.payment_type.eq(1),w,0)
    a['w_propina_tarjeta']=np.where(a.payment_type.eq(1),a.tip_amount*w,0)
    a['w_tarifa_tarjeta']=np.where(a.payment_type.eq(1),a.fare_amount*w,0)
    aggregation={'n_muestra':('fila_origen','size'),'viajes_estimados':('peso_muestral','sum'),'duracion_suma':('w_duracion','sum'),'distancia_suma':('w_distancia','sum'),'tarifa_suma':('w_tarifa','sum'),'importe_suma':('w_importe','sum'),'tarjeta_suma':('w_tarjeta','sum'),'propina_suma':('w_propina_tarjeta','sum'),'tarifa_tarjeta_suma':('w_tarifa_tarjeta','sum')}
    grouped=a.groupby(['mes_archivo','borough_origen','lluvia','hora_local','tipo_dia'],as_index=False).agg(**aggregation)
    months=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
    grouped.insert(0,'mes',grouped.mes_archivo.map(dict(enumerate(months,1))))
    columns=['mes','mes_archivo','borough_origen','lluvia','hora_local',*aggregation.keys(),'tipo_dia']
    grouped=grouped[columns]
    grouped.to_csv(ROOT/'data/processed/base_dashboard.csv',index=False)
    heat=a.groupby(['hora_local','dia_semana_local']).peso_muestral.sum().unstack().reindex(index=range(24),columns=range(7),fill_value=0)
    heat_share=heat.div(heat.sum(axis=0),axis=1)
    zone=a.groupby('zona_origen',as_index=False).agg(viajes_estimados=('peso_muestral','sum'),duracion_suma=('w_duracion','sum'))
    zone['duracion_media']=zone.duracion_suma/zone.viajes_estimados
    zone=zone.nlargest(10,'viajes_estimados');zone['cuota_pct']=100*zone.viajes_estimados/w.sum()
    zone.to_csv(R/'top_zonas.csv',index=False)
    hour=a.groupby('hora_local').peso_muestral.sum();top_hour=int(hour.idxmax());night=int(hour.idxmin())
    borough=a.groupby('borough_origen').peso_muestral.sum()
    extra={'sensibilidad':results,'diagnosticos':diagnostics,'dias_influyentes':top.to_dict('records'),'top_zonas':zone.to_dict('records'),'hora_maxima':top_hour,'hora_minima':night,'ratio_pico_valle':float(hour.max()/hour.min()),'cuota_manhattan_pct':float(100*borough.get('Manhattan',0)/w.sum()),'top10_zonas_pct':float(zone.cuota_pct.sum()),'festivos_dias_utc':int(d.festivo.sum()),'sensibilidad_exploratoria':True}
    (R/'resumen_ampliado.json').write_text(json.dumps(extra,ensure_ascii=False,indent=2),encoding='utf-8')
    old=json.loads((ROOT/'dashboard/datos_dashboard.json').read_text(encoding='utf-8'))
    old.update({'headers':grouped.columns.tolist(),'rows':json.loads(grouped.to_json(orient='values')),'extra':extra,'heatmap':heat.values.tolist()})
    (ROOT/'dashboard/datos_dashboard.json').write_text(json.dumps(old,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    navy='#20364a';teal='#177e89';gold='#edb833'
    fig,ax=plt.subplots(figsize=(10,6))
    im=ax.imshow(heat_share*100,aspect='auto',cmap='YlGnBu',origin='lower')
    ax.set(xticks=range(7),xticklabels=['Lun','Mar','Mié','Jue','Vie','Sáb','Dom'],yticks=range(0,24,2),yticklabels=range(0,24,2),xlabel='Día de la semana local',ylabel='Hora local',title='Ritmo semanal: distribución horaria dentro de cada día')
    fig.colorbar(im,ax=ax,label='% de viajes de cada día de la semana');fig.tight_layout();fig.savefig(F/'08_ritmo_semanal.png',dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,5))
    z=zone.sort_values('cuota_pct');ax.barh(z.zona_origen,z.cuota_pct,color=teal)
    ax.set(title='Diez zonas que concentran más recogidas',xlabel='Porcentaje ponderado del conjunto analítico')
    for i,value in enumerate(z.cuota_pct):ax.text(value+.06,i,f'{value:.1f}%',va='center',fontsize=9)
    ax.set_xlim(0,z.cuota_pct.max()*1.17);fig.tight_layout();fig.savefig(F/'09_top_zonas.png',dpi=170);plt.close(fig)
    fig,axs=plt.subplots(2,2,figsize=(11,7))
    axs[0,0].scatter(plain.fittedvalues,plain.resid,s=10,color=teal,alpha=.65);axs[0,0].axhline(0,color='grey',lw=.7);axs[0,0].set(title='Residuos frente a valores ajustados',xlabel='Log volumen ajustado',ylabel='Residuo')
    sm.graphics.tsa.plot_acf(plain.resid,lags=21,ax=axs[0,1],zero=False,title='Autocorrelación de residuos')
    sm.qqplot(plain.resid,line='s',ax=axs[1,0]);axs[1,0].set_title('Cuantiles de residuos frente a normal')
    axs[1,1].plot(d.fecha,cooks,color=navy,lw=.8);axs[1,1].axhline(4/len(d),color=gold,ls='--',label='Referencia 4/n');axs[1,1].set(title='Influencia por día: distancia de Cook',ylabel='Cook');axs[1,1].legend(fontsize=8)
    fig.autofmt_xdate();fig.tight_layout();fig.savefig(F/'10_diagnosticos.png',dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,4.5))
    y=np.arange(len(sensitivity));ax.axvline(0,color='grey',lw=.8)
    ax.errorbar(sensitivity.efecto_pct,y,xerr=[sensitivity.efecto_pct-sensitivity.ic95_inferior,sensitivity.ic95_superior-sensitivity.efecto_pct],fmt='o',capsize=4,color=teal)
    ax.set(yticks=y,yticklabels=sensitivity.especificacion,xlabel='Asociación ajustada de lluvia con volumen (%)',title='Sensibilidad de la estimación: especificaciones declaradas')
    ax.invert_yaxis();fig.tight_layout();fig.savefig(F/'11_sensibilidad.png',dpi=170);plt.close(fig)
    fig=plt.figure(figsize=(14,3.2),facecolor='#20364a')
    fig.text(.045,.76,'NUEVA YORK EN MOVIMIENTO',fontsize=25,fontweight='bold',color='white')
    fig.text(.045,.58,'Taxis amarillos y contexto meteorológico · 2024',fontsize=15,color='#e5edf2')
    for x,value,label in [(.045,'576.606','viajes analizados'),(.37,'365','días UTC completos'),(.65,'2','productores de datos independientes')]:
        fig.text(x,.27,value,fontsize=30,fontweight='bold',color=gold);fig.text(x,.12,label,fontsize=12,color='white')
    fig.savefig(F/'00_portada_visual.png',dpi=150,bbox_inches='tight',facecolor=fig.get_facecolor());plt.close(fig)
    print(json.dumps({k:extra[k] for k in ['hora_maxima','ratio_pico_valle','cuota_manhattan_pct','top10_zonas_pct','sensibilidad','diagnosticos']},ensure_ascii=False,indent=2))
    return extra
if __name__=='__main__':profundizar()
