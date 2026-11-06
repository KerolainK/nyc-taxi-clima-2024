import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const modulePath=process.env.ARTIFACT_TOOL_MODULE;
const {Workbook,SpreadsheetFile}=modulePath?await import(pathToFileURL(path.resolve(modulePath)).href):await import('@oai/artifact-tool');
const root=path.resolve(process.env.PROJECT_ROOT??path.join(path.dirname(fileURLToPath(import.meta.url)),'..'));
const d=JSON.parse(await fs.readFile(root+'/dashboard/datos_dashboard.json','utf8'));
const wb=Workbook.create();
const dash=wb.worksheets.add('Dashboard');
const calc=wb.worksheets.add('Calculos');
const data=wb.worksheets.add('Datos');
const info=wb.worksheets.add('Metodologia');
const navy='#20364A',gold='#EDB833',teal='#177E89';
for(const s of [dash,calc,data,info]){s.showGridLines=false;}
dash.tabColor=navy;
const n=d.rows.length+1;
data.getRange(`A1:N${n}`).values=[d.headers,...d.rows];
data.getRange(`A1:N${n}`).format.font={name:'Arial',size:10};
data.getRange('A1:N1').format={fill:navy,font:{name:'Arial',bold:true,color:'#FFFFFF'},wrapText:true};
data.getRange('A1:N1').format.rowHeight=36;
data.getRange(`A2:D${n}`).format.columnWidth=20;
data.getRange(`E2:N${n}`).format.columnWidth=17;
data.getRange(`F2:F${n}`).setNumberFormat('#,##0');
data.getRange(`G2:N${n}`).setNumberFormat('#,##0.00');
data.freezePanes.freezeRows(1);
const base=(col,extra='')=>`SUMIFS(Datos!$${col}$2:$${col}$${n},Datos!$A$2:$A$${n},IF(Dashboard!$B$6="Todos","*",Dashboard!$B$6),Datos!$C$2:$C$${n},IF(Dashboard!$F$6="Todos","*",Dashboard!$F$6),Datos!$D$2:$D$${n},IF(Dashboard!$K$6="Todos","*",Dashboard!$K$6)${extra})`;
dash.getRange('A1:P49').format.font={name:'Arial',size:10,color:navy};
dash.getRange('A1:P49').format.rowHeight=20;
dash.getRange('A1:P49').format.columnWidth=12;
dash.getRange('A1:A49').format.columnWidth=3;
dash.getRange('B2').values=[['Nueva York en movimiento']];
dash.getRange('B2').format.font={name:'Arial',size:16,bold:true,color:navy};
dash.getRange('B3').values=[['Taxis amarillos y clima · 2024 · estimaciones ponderadas del conjunto analítico']];
dash.getRange('B5').values=[['Mes']];dash.getRange('F5').values=[['Borough de origen']];dash.getRange('K5').values=[['Indicador de lluvia']];
for(const cell of ['B6','F6','K6']){dash.getRange(cell).values=[['Todos']];dash.getRange(cell).format.fill='#FFF0BD';dash.getRange(cell).format.font={name:'Arial',size:10,bold:true,color:navy};}
const months=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
dash.getRange('B6').dataValidation={rule:{type:'list',values:['Todos',...months]}};
dash.getRange('F6').dataValidation={rule:{type:'list',values:['Todos',...d.boroughs]}};
dash.getRange('K6').dataValidation={rule:{type:'list',values:['Todos','Lluvia indicada','Sin indicador']}};
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
calc.getRange('J1:K1').values=[['Indicador de lluvia','Duración media (min)']];
for(let i=0;i<2;i++){const r=i+2;calc.getRange(`J${r}`).values=[[['Lluvia indicada','Sin indicador'][i]]];const g=base('G',`,Datos!$D$2:$D$${n},J${r}`),h=base('H',`,Datos!$D$2:$D$${n},J${r}`);calc.getRange(`K${r}`).formulas=[[`=IF(${g}=0,NA(),${h}/${g})`]];}
calc.getRange('A1:K25').format.font={name:'Arial',size:10};calc.getRange('A1:K25').format.columnWidth=23;calc.getRange('B2:B25').setNumberFormat('#,##0');calc.getRange('E2:E13').setNumberFormat('#,##0');calc.getRange('H2:H9').setNumberFormat('#,##0');calc.getRange('K2:K3').setNumberFormat('0.0');
function chart(type,range,title,p1,p2,color){const c=dash.charts.add(type,range);c.title=title;c.titleTextStyle.fontSize=12;c.titleTextStyle.typeface='Arial';c.hasLegend=false;c.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:10}};c.yAxis={min:0,numberFormatCode:title.includes('Duración')?'0.0':'#,##0',numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};c.setPosition(p1,p2);for(const s of c.series.items){s.fill=color;if(type==='line')s.line={fill:color,style:'solid',width:2};}return c;}
chart('line',calc.getRange('A1:B25'),'Actividad por hora local','B18','I32',teal);
chart('bar',calc.getRange('D1:E13'),'Actividad por mes','J18','Q32',gold);
chart('bar',calc.getRange(`G1:H${d.boroughs.length+1}`),'Actividad por borough de origen','B34','I48',navy);
chart('bar',calc.getRange('J1:K3'),'Duración media según indicador (min)','J34','Q48',teal);
dash.getRange('B50').values=[['Volumen estimado mediante pesos muestrales. Las diferencias son descriptivas y no prueban causalidad.']];
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
 ['Límites','Datos observacionales, muestreo, días festivos no modelados y clima de una sola estación.']
];
info.getRange(`A1:B${notes.length}`).values=notes;info.getRange(`A1:B${notes.length}`).format.font={name:'Arial',size:10};info.getRange('A1:A17').format.columnWidth=31;info.getRange('B1:B17').format.columnWidth=100;info.getRange(`A1:B${notes.length}`).format.wrapText=true;info.getRange(`A1:B${notes.length}`).format.rowHeight=38;info.getRange('A1:A17').format.font.bold=true;
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
for(const cell of ['B6','F6','K6'])dash.getRange(cell).values=[['Todos']];wb.recalculate();
const inspection=await wb.inspect({kind:'table',range:'Dashboard!B10:L15',include:'values,formulas',tableMaxRows:6,tableMaxCols:11,maxChars:3000});
await fs.writeFile(root+'/dashboard/verificacion_excel.json',JSON.stringify({total:all,rows:n-1,tests,inspection:inspection.ndjson},null,2));
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!',options:{useRegex:true,maxResults:20},maxChars:1000});
console.log(errors.ndjson);
const file=await SpreadsheetFile.exportXlsx(wb);await file.save(root+'/dashboard/Dashboard_Taxis_Clima_2024.xlsx');
console.log('Excel exportado; filtros verificados. Filas agregadas: '+(n-1));
try{const preview=await wb.render({sheetName:'Dashboard',range:'A1:Q52',scale:1,format:'png'});await fs.writeFile(root+'/dashboard/vista_dashboard.png',new Uint8Array(await preview.arrayBuffer()));console.log('Vista guardada');}catch(e){console.log('RENDER_ERROR '+e.message);}
