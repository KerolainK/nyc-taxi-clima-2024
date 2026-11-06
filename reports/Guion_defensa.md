# Guion de defensa: Nueva York en movimiento

## Presentación de 7-8 minutos

### 1. Pregunta y motivación (45 segundos)

He analizado cómo se relaciona el clima con los viajes de los taxis amarillos de Nueva York. No quería limitarme a mostrar que dos curvas se parecen: quería comprobar si las diferencias asociadas a la lluvia permanecían después de considerar calendario y temperatura.

### 2. Fuentes y alcance (1 minuto)

He combinado dos fuentes independientes catalogadas en data.gov: los registros de viajes de NYC TLC y las observaciones meteorológicas diarias de NOAA para LaGuardia. Los doce archivos mensuales contienen 41.169.720 registros. Para trabajar con un conjunto manejable, seleccioné 50.000 filas sin limpiar por mes. El extracto bruto conserva errores y ausencias y permite repetir el proceso.

Como los meses tienen el mismo tamaño muestral pero distinto número de registros fuente, asigné a cada fila un peso igual al total de su mes dividido por 50.000. Esto evita dar el mismo peso real a meses de diferente volumen.

### 3. Limpieza e integración (1 minuto y 15 segundos)

Documenté fechas fuera del periodo, duraciones y distancias no plausibles, importes no positivos y velocidades extremas. Registré las incidencias y las exclusiones adicionales para no contarlas dos veces. Conservé las ausencias que no necesitaba imputar.

El reto principal de la unión fue temporal. Los taxis usan la hora local de Nueva York y el resumen meteorológico usa UTC. Convertí la hora local a UTC antes de unir por fecha. Excluí horas ambiguas del cambio de horario y los extremos que no cubrían días UTC completos. La unión es muchos-a-uno: no multiplica viajes. El resultado tiene 576.606 filas, 44 columnas y 365 días completos, sin correspondencias meteorológicas ausentes.

### 4. Hallazgos descriptivos (1 minuto)

La duración mediana ponderada es de 13,1 minutos y la media es de 16,9. La diferencia muestra una distribución asimétrica con viajes más largos que elevan el promedio. La tarifa base mediana es 14,2 dólares. Las propinas se estudian únicamente en pagos con tarjeta porque TLC no registra las de efectivo. La razón agregada de propina sobre tarifa base es del 22,1%.

En los gráficos comparo horas, meses y boroughs. Para comparar perfiles horarios según lluvia divido por el número de días de cada categoría: hay 138 días con lluvia indicada y 227 sin indicador.

### 5. Estadística y resultado central (1 minuto y 30 segundos)

Para la meteorología, mi unidad estadística es el día, no cada viaje. Muchos viajes comparten una misma observación del clima: tratarlos como independientes exageraría el tamaño muestral.

Ajusté tres modelos diarios para volumen, duración y propinas, con controles de mes, día de la semana, temperatura y nieve. En duración añadí distancia media. Utilicé errores HAC con siete retardos para considerar dependencia temporal y heterocedasticidad. Corregí las tres pruebas de lluvia mediante Holm.

La asociación ajustada con volumen es de +2,58%, con un intervalo entre -0,36% y +5,61%. Para duración es de +0,90% y para propinas de +0,070 puntos porcentuales. Ninguna de las tres pruebas alcanza significación al 5% tras Holm.

Mi conclusión no es que la lluvia no importe. Es que con este indicador diario, estos datos y estos controles no tengo evidencia suficiente para afirmar una asociación distinta de cero. Los datos no permiten una conclusión causal.

### 6. Demostración del dashboard (1 minuto)

Abrir el Excel y mostrar los tres selectores amarillos: mes, borough e indicador de lluvia. Seleccionar Enero, Manhattan y Lluvia indicada. Explicar cómo cambian volumen estimado, duración, distancia, importe y propinas. Volver a Todos.

Los gráficos son descriptivos; no son los coeficientes ajustados del modelo. El volumen es una estimación ponderada, no un conteo exacto. La base del dashboard agrega todas las filas del conjunto final sin volver a muestrear.

### 7. Límites y cierre (45 segundos)

Una estación y un indicador diario no describen la lluvia exacta de cada viaje. No incluyo festivos, eventos o disponibilidad de taxis. El volumen registrado tampoco mide solicitudes no atendidas. Mi propuesta de mejora es usar datos horarios, varias estaciones y otro año para validar estabilidad.

El valor del proyecto está en un proceso trazable, una unión temporal correcta, estadística interpretada con prudencia y una herramienta operativa para explorar los resultados.

## Preguntas previsibles

**¿Por qué dos fuentes si ambas aparecen en data.gov?**
Data.gov es el catálogo. Los productores son distintos: NYC TLC y NOAA/NCEI. La tabla de zonas es de TLC y solo es auxiliar.

**¿Por qué no analizar directamente 41 millones de filas?**
La muestra estratificada reduce tamaño y tiempo de trabajo, permite compartir datos brutos y conserva trazabilidad. El tamaño final supera ampliamente el mínimo. La ponderación corrige la distinta probabilidad de selección entre meses; sigue existiendo incertidumbre de muestreo.

**¿Las filas brutas son realmente brutas?**
Son un extracto muestral antes de limpiar, con los valores originales de TLC y dos columnas de trazabilidad. No afirmo que el extracto sea la descarga completa. El manifiesto y las semillas permiten reconstruirlo desde los originales.

**¿Por qué 365 días si 2024 fue bisiesto?**
2024 tiene 366 días, pero el 1 de enero UTC no está cubierto completamente por los archivos definidos en hora local. Se conserva del 2 de enero al 31 de diciembre UTC: 365 días completos. También se elimina la fracción del 1 de enero de 2025 UTC que procede del final del 31 de diciembre local.

**¿Qué significa un peso de 70?**
Esa fila representa aproximadamente 70 registros del archivo de su mes. Para estimar totales sumo pesos; para medias ponderadas sumo valor por peso y divido por pesos.

**¿Por qué HAC?**
Las observaciones diarias pueden tener varianzas diferentes y correlación temporal. HAC con siete retardos permite una inferencia robusta a ese tipo de dependencia bajo sus supuestos. No elimina confusión ni convierte el modelo en causal.

**¿Por qué Holm?**
Se hacen tres pruebas del indicador de lluvia. Holm controla el error familiar de esas pruebas; evita tratar cada p-valor aisladamente como si solo se hubiera hecho una prueba.

**¿Un p-valor alto demuestra que no hay efecto?**
No. Indica que no se rechaza la hipótesis nula con este análisis. El intervalo muestra qué tamaños de asociación siguen siendo compatibles con el modelo. No se ha realizado una prueba de equivalencia.

**¿Por qué no analizar propinas en efectivo?**
No están registradas de la misma forma en estos datos. Un cero no permite concluir que una persona no dejó propina en efectivo.

**¿Por qué media y mediana son distintas?**
La distribución es asimétrica. Algunos viajes largos elevan la media. Por eso presento cuantiles y gráficos, no solo promedios.

**¿Qué quiere decir Sin indicador?**
NOAA define 0 como no o no reportado. No es prueba de que no llovió. Por eso uso una etiqueta que no convierte ausencia de reporte en ausencia segura de lluvia.

**¿Qué cambiaría en una segunda versión?**
Meteorología horaria, varias estaciones, festivos, disponibilidad de taxis y validación en otro año. También contrastaría otros criterios de limpieza y una inferencia que modele explícitamente el diseño muestral.

**¿Se puede usar para predecir el tiempo de un viaje?**
No se ha validado como predictor individual. Los modelos son diarios y exploratorios. Presentarlos como una aplicación de predicción sería ir más allá de la evidencia.

## Preparación mínima antes de presentar

- Saber explicar la pregunta, las dos fuentes y qué representa una fila.
- Practicar los filtros del Excel y volver a Todos al terminar.
- Recordar 600.000 filas brutas, 576.606 finales, 44 columnas y 365 días.
- Distinguir volumen estimado, muestra e información original completa.
- Comprender por qué no significativo no significa sin efecto y por qué asociación no significa causalidad.
