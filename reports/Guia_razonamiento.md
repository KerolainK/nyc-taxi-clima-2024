# Por qué se hizo cada paso

Esta guía explica el razonamiento del proyecto y acompaña al notebook, los cálculos de Excel y la memoria.

## 1. Pregunta y unidad de análisis

**Pregunta:** ¿Qué queremos comprender?

**Qué se hizo:** Relacionar el contexto meteorológico con actividad registrada, duración y propinas. Cada fila final representa un viaje; no una persona ni una petición de transporte.

**Por qué:** Primero definimos la pregunta y la unidad. Así evitamos interpretar número de viajes como demanda total o usuarios únicos.

**Qué no permite concluir:** La actividad observada puede cambiar por oferta de taxis, calendario o composición de recorridos, además del clima.

## 2. Dos fuentes y una clave temporal

**Pregunta:** ¿Por qué unir TLC y NOAA?

**Qué se hizo:** TLC describe viajes y NOAA describe días meteorológicos. Los unimos por fecha UTC después de convertir la hora local de recogida. La tabla de zonas solo traduce códigos.

**Por qué:** Dos fuentes añaden dimensiones complementarias. No duplicamos archivos de una misma fuente para simular dos productores independientes.

**Qué no permite concluir:** Una estación y un resumen diario no miden la exposición exacta de cada recorrido.

## 3. Muestreo y pesos

**Pregunta:** ¿Por qué 50.000 filas por mes?

**Qué se hizo:** Una muestra antes de limpiar hace el proyecto manejable y conserva errores reales. Cada mes usa una semilla fija. El peso de una fila es N del archivo mensual / 50.000.

**Por qué:** Los meses tienen el mismo tamaño muestral y diferente volumen real. Sin pesos, un mes pequeño contaría tanto como uno grande.

**Qué no permite concluir:** Los totales son estimaciones de registros que superan los filtros, no recuentos exactos. El muestreo introduce incertidumbre.

## 4. Limpieza con criterio de negocio

**Pregunta:** ¿Por qué excluir determinados registros?

**Qué se hizo:** Se exige inicio dentro del mes, duración y distancia positivas y plausibles, tarifa e importe positivos y velocidad no extrema. Se registran incidencias y exclusiones adicionales.

**Por qué:** El alcance es actividad facturada positiva y plausible. Una tarifa negativa puede ser un ajuste legítimo; se excluye del alcance, no se declara automáticamente un dato falso.

**Qué no permite concluir:** Los umbrales pueden cambiar resultados. Por eso se conserva el extracto bruto y se prueba un límite alternativo de duración.

## 5. Ausencia frente a cero

**Pregunta:** ¿Qué hacemos cuando falta información?

**Qué se hizo:** No se inventan pasajeros ni precipitación. Los códigos NOAA de ausencia se convierten en nulos. La propina porcentual solo se calcula para tarjeta.

**Por qué:** Un cero es una observación; un nulo indica información no disponible o no aplicable. Confundirlos sesga medias y comparaciones.

**Qué no permite concluir:** Sin indicador de lluvia significa no indicado o no reportado. No prueba que el día fuese seco.

## 6. Tiempo, cambios de hora y límites

**Pregunta:** ¿Por qué no unir directamente las fechas?

**Qué se hizo:** Nueva York usa hora local con horario de verano y NOAA usa UTC. Se convierten horas; las ambiguas/inexistentes se excluyen y se retiran los días UTC parciales de los extremos.

**Por qué:** La conversión impide asignar el clima del día equivocado a parte de los viajes nocturnos. La comparación diaria requiere periodos completos.

**Qué no permite concluir:** El día UTC no coincide con el civil local. Los perfiles por hora usan hora local, pero la exposición meteorológica sigue siendo UTC.

## 7. Uniones sin multiplicar viajes

**Pregunta:** ¿Cómo sabemos que la combinación es correcta?

**Qué se hizo:** Se comprueba unicidad de la fecha en NOAA y del código en la tabla de zonas. Las uniones son muchos-a-uno y se exige que no aumente el número de viajes.

**Por qué:** Una unión muchos-a-muchos puede inflar el dataset y los totales sin añadir observaciones reales. El tamaño mínimo no justifica esa multiplicación.

**Qué no permite concluir:** Tener correspondencia no garantiza que una estación represente bien cada barrio.

## 8. Fórmulas y medias ponderadas

**Pregunta:** ¿Qué calcula Excel?

**Qué se hizo:** SUMIFS suma solo filas que cumplen filtros. Viajes estimados = suma de pesos. Media de duración = suma de peso × minutos / suma de pesos. El mismo criterio se aplica a distancia e importe.

**Por qué:** La base agregada conserva sumas suficientes; por ello Excel reproduce los indicadores del dataset completo sin cargar medio millón de filas en la vista.

**Qué no permite concluir:** No se promedian medias de grupos sin ponderarlas. Un grupo de diez viajes no debe contar igual que uno de diez mil.

## 9. Razón de sumas frente a media de razones

**Pregunta:** ¿Cómo interpretar el porcentaje de propina?

**Qué se hizo:** En tarjeta, se divide suma ponderada de propinas por suma ponderada de tarifas base. El resultado expresa dólares de propina por dólar de tarifa.

**Por qué:** La media de porcentajes individuales responde a otra pregunta: porcentaje de un viaje típico. Puede diferir de la razón agregada porque cada tarifa tiene distinto tamaño.

**Qué no permite concluir:** No es el porcentaje sobre importe total, ni incluye propinas en efectivo, ni equivale a ingreso neto del conductor.

## 10. Comparaciones justas

**Pregunta:** ¿Por qué normalizar los perfiles?

**Qué se hizo:** Los grupos de lluvia contienen distinto número de días. En perfiles diarios se divide por exposición. En la matriz semanal, cada columna se expresa como porcentaje de sus propios viajes y suma 100%.

**Por qué:** Comparar totales de categorías con distinta cantidad de días o viajes puede fabricar una diferencia mecánica. La normalización aclara qué patrón comparamos.

**Qué no permite concluir:** La comparación descriptiva no ajusta todos los factores. No se interpreta como efecto del clima.

## 11. Unidad estadística y modelos

**Pregunta:** ¿Por qué 365 observaciones y no 576.606?

**Qué se hizo:** Miles de viajes comparten el mismo clima diario. Los modelos usan una fila por día y ajustan calendario, temperatura y nieve; duración incluye distancia media.

**Por qué:** Tratar cada viaje como exposición meteorológica independiente exageraría la precisión. El tamaño para esa inferencia es el número de días.

**Qué no permite concluir:** Los modelos son agregados y observacionales. No identifican el efecto individual ni causal de la lluvia.

## 12. Diagnóstico y sensibilidad

**Pregunta:** ¿Cómo comprobamos que la conclusión no depende de una elección?

**Qué se hizo:** Se examinan residuos, autocorrelación, heterocedasticidad e influencia. Se informan HAC 3/7/14, festivos, exclusión de días influyentes, estacionalidad flexible y volumen del día anterior.

**Por qué:** HAC cambia la incertidumbre; no elimina la dependencia de los residuos ni corrige automáticamente una especificación incompleta. El modelo dinámico cambia la interpretación al condicionar a actividad previa.

**Qué no permite concluir:** Las sensibilidades son exploratorias. Excluir cinco días produce un p nominal inferior a 0,05; no se selecciona ese modelo como confirmación ni se esconden las otras especificaciones.

## 13. Resultado y decisión

**Pregunta:** ¿Qué permite recomendar el análisis?

**Qué se hizo:** El perfil anual alcanza su máximo a las 18:00. Manhattan concentra aproximadamente el 88,8% de las recogidas y las diez primeras zonas el 37,9%. Son prioridades para monitorizar actividad.

**Por qué:** Los patrones ayudan a decidir dónde y cuándo profundizar. Las asociaciones de lluvia son pequeñas e inestables entre especificaciones, por lo que no justifican prometer un incremento fijo.

**Qué no permite concluir:** La muestra se limita a taxis amarillos y un año. No representa toda la movilidad ni solicitudes no atendidas.

## 14. Qué cambia al usar los filtros

**Pregunta:** ¿Qué queda fijo y qué se recalcula?

**Qué se hizo:** Dashboard filtra mes, borough, lluvia y tipo de día. Patrones muestra la vista anual completa. Robustez conserva los modelos diarios del estudio; no recalcula regresiones al mover selectores.

**Por qué:** Separar exploración interactiva y modelos estimados evita presentar una comparación de dos medias como si fuera un coeficiente ajustado.

**Qué no permite concluir:** Lun-vie es una categoría de calendario; incluye festivos entre semana. Fin semana significa sábado y domingo, no comportamiento laboral real.

## Ejemplo didáctico de ponderación

Dos registros de ejemplo duran 10 y 20 minutos y representan 60 y 80 viajes, respectivamente. La media simple es 15 min; la ponderada es (60 × 10 + 80 × 20) / (60 + 80) = 15,71 min. Son números didácticos, no observaciones del dataset.

## Recorrido de trazabilidad

Registro TLC -> mes y fila de origen -> filtros -> peso -> fecha UTC -> unión meteorológica -> sumas agregadas -> fórmula de Excel -> interpretación y límite. Los modelos usan la tabla diaria, no las medias filtradas de la pantalla.

## Cómo leer los diagnósticos sin confundirlos con conclusiones

- **Residuo:** diferencia entre el resultado diario y el valor ajustado por el modelo. Un patrón visible sugiere estructura no explicada.
- **Durbin-Watson (DW):** cerca de 2 indica poca correlación residual de primer orden; valores muy bajos sugieren persistencia positiva. No evalúa toda la dependencia temporal.
- **Ljung-Box:** un p pequeño señala evidencia de autocorrelación conjunta hasta el retardo considerado. Se usa aquí como diagnóstico exploratorio, no como garantía de validez.
- **Breusch-Pagan:** un p pequeño sugiere que la varianza residual no es constante. Es una razón para no confiar en errores estándar OLS convencionales.
- **Distancia de Cook:** mide cuánto puede cambiar el ajuste al retirar una observación. Influencia no significa dato erróneo; los cinco días más influyentes se estudian como sensibilidad, no se borran del dataset final.
- **HAC:** modifica la covarianza estimada para contemplar heterocedasticidad y autocorrelación bajo sus supuestos. No elimina residuos correlacionados, confusión o errores de medición.
- **Intervalo del 95%:** expresa incertidumbre del coeficiente bajo el modelo; que incluya cero no demuestra que la asociación sea exactamente cero.
- **R² ajustado:** describe ajuste dentro de la muestra penalizando número de parámetros. No valida predicción futura ni identifica causalidad.
- **Número de condición:** depende de la escala y de la matriz de diseño. Un valor elevado orienta a revisar el diseño, pero no prueba por sí solo una causa concreta de inestabilidad.

La lectura conjunta es esencial: los modelos principales no alcanzan el umbral de Holm; la exclusión de cinco días cambia un intervalo nominal y el modelo dinámico reduce la asociación puntual. El resultado se comunica como exploratorio y sensible a especificación.
