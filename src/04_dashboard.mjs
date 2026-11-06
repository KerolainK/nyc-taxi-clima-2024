import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const modulePath=process.env.ARTIFACT_TOOL_MODULE;
const {Workbook,SpreadsheetFile}=modulePath?await import(pathToFileURL(path.resolve(modulePath)).href):await import('@oai/artifact-tool');
const root=path.resolve(process.env.PROJECT_ROOT??path.join(path.dirname(fileURLToPath(import.meta.url)),'..'));
const d=JSON.parse(await fs.readFile(root+'/dashboard/datos_dashboard.json','utf8'));
const wb=Workbook.create();
const dash=wb.worksheets.add('Dashboard');
const patterns=wb.worksheets.add('Patrones');
const robust=wb.worksheets.add('Robustez');
const calc=wb.worksheets.add('Calculos');
const reasoning=wb.worksheets.add('Razonamiento');
const data=wb.worksheets.add('Datos');
const info=wb.worksheets.add('Metodologia');
const navy='#20364A',gold='#EDB833',teal='#177E89';
for(const s of [dash,patterns,robust,calc,reasoning,data,info]){s.showGridLines=false;}
dash.tabColor=navy;
const n=d.rows.length+1;
data.getRange(`A1:O${n}`).values=[d.headers,...d.rows];
data.getRange(`A1:O${n}`).format.font={name:'Arial',size:10};
data.getRange('A1:O1').format={fill:navy,font:{name:'Arial',bold:true,color:'#FFFFFF'},wrapText:true};
data.getRange('A1:O1').format.rowHeight=36;
data.getRange(`A2:D${n}`).format.columnWidth=20;
data.getRange(`E2:N${n}`).format.columnWidth=17;
data.getRange(`F2:F${n}`).setNumberFormat('#,##0');
data.getRange(`G2:N${n}`).setNumberFormat('#,##0.00');
data.freezePanes.freezeRows(1);
const base=(col,extra='')=>`SUMIFS(Datos!$${col}$2:$${col}$${n},Datos!$A$2:$A$${n},IF(Dashboard!$B$6="Todos","*",Dashboard!$B$6),Datos!$C$2:$C$${n},IF(Dashboard!$F$6="Todos","*",Dashboard!$F$6),Datos!$D$2:$D$${n},IF(Dashboard!$K$6="Todos","*",Dashboard!$K$6),Datos!$O$2:$O$${n},IF(Dashboard!$N$6="Todos","*",Dashboard!$N$6)${extra})`;
dash.getRange('A1:P49').format.font={name:'Arial',size:10,color:navy};
dash.getRange('A1:P49').format.rowHeight=20;
dash.getRange('A1:P49').format.columnWidth=12;
dash.getRange('A1:A49').format.columnWidth=3;
dash.getRange('B2').values=[['Nueva York en movimiento']];
dash.getRange('B2').format.font={name:'Arial',size:16,bold:true,color:navy};
dash.getRange('B3').values=[['Taxis amarillos y clima · 2024 · estimaciones ponderadas del conjunto analítico']];
dash.getRange('B5').values=[['Mes']];dash.getRange('F5').values=[['Borough de origen']];dash.getRange('K5').values=[['Indicador de lluvia']];
for(const cell of ['B6','F6','K6','N6']){dash.getRange(cell).values=[['Todos']];dash.getRange(cell).format.fill='#FFF0BD';dash.getRange(cell).format.font={name:'Arial',size:10,bold:true,color:navy};}
const months=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
dash.getRange('B6').dataValidation={rule:{type:'list',values:['Todos',...months]}};
dash.getRange('F6').dataValidation={rule:{type:'list',values:['Todos',...d.boroughs]}};
dash.getRange('K6').dataValidation={rule:{type:'list',values:['Todos','Lluvia indicada','Sin indicador']}};
dash.getRange('N5').values=[['Tipo de día']];
dash.getRange('N6').dataValidation={rule:{type:'list',values:['Todos','Lun-vie','Fin semana']}};
dash.getRange('B8').values=[['Cambie las celdas amarillas para explorar los resultados.']];
for(const [cell,label] of [['B10','Viajes válidos estimados'],['F10','Duración media (min)'],['K10','Importe medio (USD)'],['B14','Filas de la muestra'],['F14','Distancia media (km)'],['K14','Propina / tarifa (tarjeta)']])dash.getRange(cell).values=[[label]];
dash.getRange('B11').formulas=[['='+base('G')]];
dash.getRange('F11').formulas=[['=IF(B11=0,"n.a.",'+base('H')+'/B11)']];
dash.getRange('K11').formulas=[['=IF(B11=0,"n.a.",'+base('K')+'/B11)']];
dash.getRange('B15').formulas=[['='+base('F')]];
dash.getRange('F15').formulas=[['=IF(B11=0,"n.a.",'+base('I')+'/B11)']];
dash.getRange('K15').formulas=[['=IF('+base('N')+'=0,"n.a.",'+base('M')+'/'+base('N')+')']];
for(const cell of ['B11','F11','K11','B15','F15','K15']){dash.getRange(cell).format.font={name:'Arial',size:16,bold:true,color:navy};dash.getRange(cell).setNumberFormat(cell==='B11'?'0.0,," M"':cell==='B15'?'#,##0':cell==='K15'?'0.0%':'0.0');}
calc.getRange('A1:B1').values=[['Hora local','Viajes estimados']];
for(let i=0;i<24;i++){const r=i+2;calc.getRange(`A${r}`).values=[[i]];calc.getRange(`B${r}`).formulas=[['='+base('G',`,Datos!$E$2:$E$${n},A${r}`)]];}
calc.getRange('D1:E1').values=[['Mes','Viajes estimados']];
for(let i=0;i<12;i++){const r=i+2;calc.getRange(`D${r}`).values=[[months[i]]];calc.getRange(`E${r}`).formulas=[['='+base('G',`,Datos!$A$2:$A$${n},D${r}`)]];}
calc.getRange('G1:H1').values=[['Borough de origen','Viajes estimados']];
for(let i=0;i<d.boroughs.length;i++){const r=i+2;calc.getRange(`G${r}`).values=[[d.boroughs[i]]];calc.getRange(`H${r}`).formulas=[['='+base('G',`,Datos!$C$2:$C$${n},G${r}`)]];}
const comparative=(col,extra='')=>`SUMIFS(Datos!$${col}$2:$${col}$${n},Datos!$A$2:$A$${n},IF(Dashboard!$B$6="Todos","*",Dashboard!$B$6),Datos!$C$2:$C$${n},IF(Dashboard!$F$6="Todos","*",Dashboard!$F$6),Datos!$O$2:$O$${n},IF(Dashboard!$N$6="Todos","*",Dashboard!$N$6)${extra})`;
calc.getRange('J1:K1').values=[['Indicador de lluvia','Duración media (min)']];
for(let i=0;i<2;i++){const r=i+2;calc.getRange(`J${r}`).values=[[['Lluvia indicada','Sin indicador'][i]]];const g=comparative('G',`,Datos!$D$2:$D$${n},J${r}`),h=comparative('H',`,Datos!$D$2:$D$${n},J${r}`);calc.getRange(`K${r}`).formulas=[[`=IF(${g}=0,NA(),${h}/${g})`]];}
calc.getRange('A1:K25').format.font={name:'Arial',size:10};calc.getRange('A1:K25').format.columnWidth=23;calc.getRange('B2:B25').setNumberFormat('#,##0');calc.getRange('E2:E13').setNumberFormat('#,##0');calc.getRange('H2:H9').setNumberFormat('#,##0');calc.getRange('K2:K3').setNumberFormat('0.0');
function chart(type,range,title,p1,p2,color,sheet=dash){const c=sheet.charts.add(type,range);c.title=title;c.titleTextStyle.fontSize=12;c.titleTextStyle.typeface='Arial';c.hasLegend=false;c.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:10}};c.yAxis={min:0,numberFormatCode:title.includes('Duración')?'0.0':'#,##0',numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};c.setPosition(p1,p2);for(const s of c.series.items){s.fill=color;if(type==='line')s.line={fill:color,style:'solid',width:2};}return c;}
chart('line',calc.getRange('A1:B25'),'Actividad por hora local','B18','I32',teal);
chart('bar',calc.getRange('D1:E13'),'Actividad por mes','J18','Q32',gold);
chart('bar',calc.getRange(`G1:H${d.boroughs.length+1}`),'Actividad por borough de origen','B34','I48',navy);
chart('bar',calc.getRange('J1:K3'),'Duración media según indicador (min)','J34','Q48',teal);
dash.getRange('B50').values=[['Volumen estimado mediante pesos muestrales. Las diferencias son descriptivas y no prueban causalidad.']];
dash.getRange('B52').values=[['Comparación de lluvia: conserva mes, borough y tipo de día; compara siempre ambas categorías.']];
dash.getRange('B51').values=[['Sin indicador = no se indicó lluvia; puede incluir ausencia de reporte. Propinas: únicamente pagos con tarjeta.']];
const notes=[
 ['Tema','Taxis amarillos de Nueva York y clima, 2024'],
 ['Periodo final','2 enero a 31 diciembre 2024, días UTC completos'],
 ['Muestra final',d.summary.n],
 ['Muestreo','50.000 filas aleatorias por mes antes de limpiar; peso = N mensual / 50.000'],
 ['Unidad de datos','Un viaje. Los datos de la hoja Datos agregan todos los viajes del conjunto final.'],
 ['Unidad para inferencia meteorológica','Un día UTC. Los modelos y sus intervalos están en la memoria, no en estas comparaciones descriptivas.'],
 ['Viajes estimados','Suma de los pesos de los viajes que superan los filtros de calidad. No son conteos exactos.'],
 ['Duración media','Suma ponderada de minutos / suma de pesos.'],
 ['Importe medio','Suma ponderada de total_amount / suma de pesos. No incluye propinas en efectivo.'],
 ['Propina / tarifa','Suma ponderada de propinas de tarjeta / suma ponderada de tarifa base de tarjeta.'],
 ['Meteorología','Una estación: LaGuardia. El indicador es diario y no describe la lluvia exacta de cada viaje.'],
 ['Fuente TLC','https://catalog.data.gov/dataset/2024-yellow-taxi-trip-data'],
 ['Fuente NOAA','https://catalog.data.gov/dataset/global-surface-summary-of-the-day-gsod'],
 ['Distribución TLC','https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page'],
 ['Uso','Cambiar Mes, Borough de origen o Indicador de lluvia en las celdas amarillas de Dashboard.'],
 ['Actualización','Regenerar la base con Python y reconstruir el libro; los selectores recalculan la base incluida.'],
 ['Límites','Datos observacionales, muestreo, festivos solo en sensibilidad y clima de una sola estación.']
];
info.getRange(`A1:B${notes.length}`).values=notes;info.getRange(`A1:B${notes.length}`).format.font={name:'Arial',size:10};info.getRange('A1:A17').format.columnWidth=31;info.getRange('B1:B17').format.columnWidth=100;info.getRange(`A1:B${notes.length}`).format.wrapText=true;info.getRange(`A1:B${notes.length}`).format.rowHeight=38;info.getRange('A1:A17').format.font.bold=true;
// Explicaciones junto a los calculos y una guia completa del razonamiento.
const explanations=JSON.parse(await fs.readFile(root+'/dashboard/razonamiento.json','utf8'));
calc.getRange('M1:N1').values=[['Bloque','Qué hace y por qué se calcula así']];
const explanationsByBlock=[
 ['A1:B25 · Horas','SUMIFS selecciona mes, borough, indicador de lluvia y tipo de día; añade una hora concreta. Suma pesos, no solo filas. Cada fila alimenta el gráfico horario.'],
 ['D1:E13 · Meses','Añade el mes del renglón a los filtros activos. Si se selecciona un solo mes, los otros meses tienen volumen cero en ese subconjunto.'],
 ['G1:H9 · Territorio','Repite el mismo criterio de selección por borough de origen. Describe recogidas de taxis amarillos; no toda la movilidad de un barrio.'],
 ['J1:K3 · Lluvia','Compara la duración media de ambas categorías manteniendo mes, borough y tipo de día. Ignora solo el selector de lluvia para que el contraste siga siendo visible.'],
 ['Viajes estimados','La suma de pesos estima cuántos registros válidos representa la muestra. La suma de n_muestra indica cuántas filas observamos realmente. Son cantidades distintas.'],
 ['Media de duración','Numerador: suma de peso × minutos. Denominador: suma de pesos. Dividir las sumas conserva el tamaño de cada grupo; promediar medias sin ponderar lo perdería.'],
 ['Propina en tarjeta','Se suman propinas y tarifas base ponderadas únicamente en tarjeta. Se divide la primera suma por la segunda. No se interpreta el efectivo como propina cero.'],
 ['Ejemplo didáctico','Dos registros duran 10 y 20 min y pesan 60 y 80. Media ponderada=(60×10+80×20)/(60+80)=15,71 min. Media simple=15 min. Estos valores son ilustrativos.'],
 ['Valores no disponibles','Cuando el denominador es cero se muestra n.a. o NA() para el gráfico. No se inventa una media cero que parecería un resultado observado.'],
 ['A31:H55 · Matriz anual','Cada columna contiene la distribución de horas de un día semanal. Patrones presenta la cuota de cada hora dentro de su propia columna: cada columna suma 100%.'],
 ['J31:L55 · Perfiles','Compara la forma de la distribución horaria entre lunes-viernes y fin de semana, expresada como porcentaje dentro de cada categoría. No compara totales con distinta exposición.'],
 ['Trazabilidad','Datos contiene sumas calculadas con Python sobre todas las filas finales. Las fórmulas de esta hoja filtran esas sumas; no vuelven a muestrear. Véase Razonamiento para las decisiones y límites.']
];
calc.getRange(`M2:N${explanationsByBlock.length+1}`).values=explanationsByBlock;
calc.getRange('M1:M13').format.columnWidth=32;calc.getRange('N1:N13').format.columnWidth=92;
calc.getRange('M1:N13').format.font={name:'Arial',size:10};calc.getRange('M1:N13').format.wrapText=true;
calc.getRange('M1:N13').format.rowHeight=65;calc.getRange('M1:N1').format.fill='#E7EDF1';
calc.getRange('A27').values=[['Explicaciones detalladas a la derecha (M:N) y en la hoja Razonamiento.']];
reasoning.getRange('B2').values=[['El razonamiento detrás del análisis']];
reasoning.getRange('B2').format.font={name:'Arial',size:16,bold:true,color:navy};
reasoning.getRange('B3').values=[['Pregunta, procedimiento, motivo y límite de cada decisión.']];
reasoning.getRange('B1:B110').format.columnWidth=31;reasoning.getRange('C1:C110').format.columnWidth=112;
let rr=5;
for(const e of explanations){
 reasoning.getRange(`B${rr}`).values=[[e.titulo]];reasoning.getRange(`B${rr}:C${rr}`).format.fill='#E7EDF1';reasoning.getRange(`B${rr}:C${rr}`).format.rowHeight=32;
 reasoning.getRange(`B${rr}:C${rr}`).format.font={name:'Arial',size:11,bold:true,color:navy};
 const rows=[['Pregunta',e.pregunta],['Qué se hizo',e.metodo],['Por qué',e.razon],['Qué no permite concluir',e.limite]];
 reasoning.getRange(`B${rr+1}:C${rr+4}`).values=rows;reasoning.getRange(`B${rr+1}:C${rr+4}`).format.font={name:'Arial',size:10,color:navy};reasoning.getRange(`B${rr+1}:C${rr+4}`).format.wrapText=true;reasoning.getRange(`B${rr+1}:C${rr+4}`).format.rowHeight=58;
 rr+=6;
}
reasoning.freezePanes.freezeRows(3);
// Vista anual: conserva su alcance, independiente de los filtros de Dashboard.
patterns.getRange('A1:Q40').format.font={name:'Arial',size:10,color:navy};patterns.getRange('A1:Q40').format.columnWidth=11;patterns.getRange('A1:Q40').format.rowHeight=23;
patterns.getRange('A1:A40').format.columnWidth=3;patterns.getRange('K1:K40').format.columnWidth=31;
patterns.getRange('B2').values=[['Cuándo y dónde se concentra la actividad']];patterns.getRange('B2').format.font={name:'Arial',size:16,bold:true,color:navy};
patterns.getRange('B3').values=[['Vista anual completa. Los selectores de Dashboard solo modifican esa hoja.']];
patterns.getRange('B5').values=[[d.extra.hora_maxima+':00']];patterns.getRange('F5').values=[[d.extra.cuota_manhattan_pct/100]];patterns.getRange('K5').values=[[d.extra.top10_zonas_pct/100]];
patterns.getRange('B6').values=[['Hora con más recogidas']];patterns.getRange('F6').values=[['Cuota de Manhattan']];patterns.getRange('K6').values=[['Cuota de las diez primeras zonas']];
for(const cell of ['B5','F5','K5'])patterns.getRange(cell).format.font={name:'Arial',size:16,bold:true,color:navy};
patterns.getRange('F5').setNumberFormat('0.0%');patterns.getRange('K5').setNumberFormat('0.0%');
const weekdays=['Lun','Mar','Mié','Jue','Vie','Sáb','Dom'];
patterns.getRange('B9:I9').values=[['Hora',...weekdays]];
calc.getRange('A31:H31').values=[['Hora',...weekdays]];
for(let h=0;h<24;h++){
 const pr=h+10,cr=h+32;patterns.getRange(`B${pr}`).values=[[h]];calc.getRange(`A${cr}`).values=[[h]];
 calc.getRange(`B${cr}:H${cr}`).values=[d.heatmap[h]];
 for(let j=0;j<7;j++){const col=String.fromCharCode(67+j),src=String.fromCharCode(66+j);patterns.getRange(`${col}${pr}`).formulas=[[`=Calculos!${src}${cr}/SUM(Calculos!${src}$32:${src}$55)`]];}
}
patterns.getRange('C10:I33').setNumberFormat('0.0%');patterns.getRange('C10:I33').conditionalFormats.add('colorScale',{colors:['#FFF6D5','#79B7BE','#20364A'],thresholds:['min',{type:'percentile',value:50},'max']});
patterns.getRange('C10:I33').format.font.color='#000000';
patterns.getRange('C10:I33').conditionalFormats.add('cellIs',{operator:'greaterThan',formula:0.062,format:{font:{color:'#FFFFFF'}}});
patterns.getRange('B35').values=[['Cada columna suma 100%: compara ritmos horarios, no el tamaño total de cada día.']];
patterns.getRange('K9:M9').values=[['Zona de origen','Cuota','Minutos medios']];
patterns.getRange('K10:M19').values=d.extra.top_zonas.map(z=>[z.zona_origen,z.cuota_pct/100,z.duracion_media]);
patterns.getRange('K10:K19').format.wrapText=true;patterns.getRange('K10:M19').format.rowHeight=31;patterns.getRange('L10:L19').setNumberFormat('0.0%');patterns.getRange('M10:M19').setNumberFormat('0.0');
calc.getRange('J31:L31').values=[['Hora','Lun-vie','Fin semana']];
for(let h=0;h<24;h++){const r=h+32;calc.getRange(`J${r}`).values=[[h]];for(let j=0;j<2;j++){const col=j===0?'K':'L',day=j===0?'Lun-vie':'Fin semana';calc.getRange(`${col}${r}`).formulas=[[`=SUMIFS(Datos!$G$2:$G$${n},Datos!$E$2:$E$${n},J${r},Datos!$O$2:$O$${n},"${day}")/SUMIFS(Datos!$G$2:$G$${n},Datos!$O$2:$O$${n},"${day}")`]];}}
calc.getRange('K32:L55').setNumberFormat('0.0%');
const profile=chart('line',calc.getRange('J31:L55'),'Perfil horario dentro de cada categoría','K22','R37',teal,patterns);profile.hasLegend=true;profile.legend={position:'top',textStyle:{typeface:'Arial',fontSize:10}};profile.yAxis={numberFormatCode:'0%',numberFormatSourceLinked:false};profile.series.items[1].line={fill:gold,style:'solid',width:2};
// Robustez: resultados de modelos previamente estimados; no se recalculan con filtros.
robust.getRange('B2').values=[['Qué tan estable es la conclusión sobre lluvia']];robust.getRange('B2').format.font={name:'Arial',size:16,bold:true,color:navy};
robust.getRange('B3').values=[['Sensibilidades exploratorias; no sustituyen las tres pruebas principales con ajuste de Holm.']];
robust.getRange('B5:G5').values=[['Especificación','Cambio (%)','IC95 inferior','IC95 superior','p exploratorio','Días']];
robust.getRange('B6:G13').values=d.extra.sensibilidad.map(r=>[r.especificacion,r.efecto_pct,r.ic95_inferior,r.ic95_superior,r.p_exploratorio,r.n_dias]);
robust.getRange('B1:B31').format.columnWidth=45;robust.getRange('C1:G31').format.columnWidth=15;robust.getRange('B5:G25').format.rowHeight=26;robust.getRange('B5:G25').format.font={name:'Arial',size:10};robust.getRange('C6:E13').setNumberFormat('0.00');robust.getRange('F6:F13').setNumberFormat('0.000');robust.getRange('G6:G13').setNumberFormat('0');
robust.getRange('B15').values=[['Excluir cinco días da un p nominal <0,05; no se selecciona esa especificación para declarar confirmación.']];
robust.getRange('B17').values=[['El modelo dinámico cambia la pregunta: asociación condicionada al volumen del día anterior.']];
robust.getRange('B20').values=[['Diagnósticos: HAC ajusta la incertidumbre, no elimina los patrones de los residuos.']];
robust.getRange('B21:G21').values=[['Modelo','DW','Ljung-Box p7','BP p','R² ajustado','Condición']];
robust.getRange('B22:G25').values=d.extra.diagnosticos.map(r=>[r.modelo,r.durbin_watson,r.ljung_box_p7,r.breusch_pagan_p,r.r2_ajustado,r.numero_condicion]);
robust.getRange('C22:C25').setNumberFormat('0.00');robust.getRange('D22:E25').setNumberFormat('0.00E+00');robust.getRange('F22:F25').setNumberFormat('0.000');robust.getRange('G22:G25').setNumberFormat('0');
robust.getRange('B28').values=[['p pequeño en Ljung-Box sugiere dependencia residual; en Breusch-Pagan, varianza no constante. Son diagnósticos exploratorios.']];
for(const [sheet,ranges] of [[patterns,['B9:I9','K9:M9']],[robust,['B5:G5','B21:G21']]])for(const range of ranges){sheet.getRange(range).format.fill='#E7EDF1';sheet.getRange(range).format.font={name:'Arial',size:10,bold:true,color:navy};}
info.getRange('A18:B20').values=[['Razonamiento','La hoja Razonamiento explica pregunta, método, motivo y límites de 14 decisiones; Calculos incluye explicaciones junto a las fórmulas.'],['Tipo de día','Lun-vie y Fin semana se determinan por día semanal local. Lun-vie puede incluir festivos.'],['Modelos adicionales','Sensibilidades con festivos, influencia, estacionalidad flexible y volumen anterior. Resultados exploratorios, no causales.']];
info.getRange('A18:A20').format.columnWidth=31;info.getRange('B18:B20').format.columnWidth=100;info.getRange('A18:B20').format.wrapText=true;info.getRange('A18:B20').format.rowHeight=45;
data.getRange(`O1:O${n}`).format.columnWidth=15;

wb.recalculate();
const all=Number(dash.getRange('B11').values[0][0]);
if(Math.abs(all-d.summary.poblacion_viajes_validos_estimada)>0.1)throw new Error('No concilia el total del dashboard: '+all);
const tests=[];
for(const [month,borough,rain] of [['Enero','Manhattan','Lluvia indicada'],['Julio','Todos','Todos'],['Todos','Queens','Sin indicador']]){
 dash.getRange('B6').values=[[month]];dash.getRange('F6').values=[[borough]];dash.getRange('K6').values=[[rain]];wb.recalculate();
 const expected=d.rows.filter(r=>(month==='Todos'||r[0]===month)&&(borough==='Todos'||r[2]===borough)&&(rain==='Todos'||r[3]===rain)).reduce((s,r)=>s+r[6],0);
 const actual=Number(dash.getRange('B11').values[0][0]);if(Math.abs(actual-expected)>.1)throw new Error('Fallo filtro '+[month,borough,rain,actual,expected]);
 tests.push({month,borough,rain,expected,actual});
}
for(const day of ['Lun-vie','Fin semana']){dash.getRange('B6').values=[['Todos']];dash.getRange('F6').values=[['Todos']];dash.getRange('K6').values=[['Todos']];dash.getRange('N6').values=[[day]];wb.recalculate();const expected=d.rows.filter(r=>r[14]===day).reduce((v,r)=>v+r[6],0);const actual=Number(dash.getRange('B11').values[0][0]);if(Math.abs(expected-actual)>.1)throw Error('Filtro tipo de dia incorrecto');tests.push({day,expected,actual});}
for(const cell of ['B6','F6','K6','N6'])dash.getRange(cell).values=[['Todos']];wb.recalculate();
const inspection=await wb.inspect({kind:'table',range:'Dashboard!B10:L15',include:'values,formulas',tableMaxRows:6,tableMaxCols:11,maxChars:3000});
await fs.writeFile(root+'/dashboard/verificacion_excel.json',JSON.stringify({total:all,rows:n-1,tests,inspection:inspection.ndjson},null,2));
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!',options:{useRegex:true,maxResults:20},maxChars:1000});
console.log(errors.ndjson);
const file=await SpreadsheetFile.exportXlsx(wb);await file.save(root+'/dashboard/Dashboard_Taxis_Clima_2024_v2.xlsx');
console.log('Excel exportado; filtros verificados. Filas agregadas: '+(n-1));
try{const preview=await wb.render({sheetName:'Dashboard',range:'A1:Q54',scale:1,format:'png'});await fs.writeFile(root+'/dashboard/vista_dashboard.png',new Uint8Array(await preview.arrayBuffer()));console.log('Vista guardada');}catch(e){console.log('RENDER_ERROR '+e.message);}

for(const [sheet,range,file] of [['Patrones','A1:R39','vista_patrones.png'],['Robustez','A1:H30','vista_robustez.png'],['Calculos','L1:O14','vista_calculos_explicados.png'],['Razonamiento','B1:C16','vista_razonamiento.png']]){const preview=await wb.render({sheetName:sheet,range,scale:1,format:'png'});await fs.writeFile(root+'/dashboard/'+file,new Uint8Array(await preview.arrayBuffer()));}
