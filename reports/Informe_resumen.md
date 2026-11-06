# Nueva York en movimiento

## Resultados principales

Conjunto final: 576.606 filas y 44 columnas; 365 días UTC completos.

Duración mediana: 13,1 min. Tarifa base mediana: 14,2 USD.

## Asociaciones ajustadas con lluvia

- Volumen diario estimado: 2,58 %; IC95% [-0,36, 5,61]; p Holm = 0,258.

- Duracion media diaria: 0,90 %; IC95% [-0,42, 2,24]; p Holm = 0,364.

- Propina diaria sobre tarifa (tarjeta): 0,07 puntos porcentuales; IC95% [-0,04, 0,18]; p Holm = 0,364.

Ninguna de las tres pruebas alcanza el nivel 0,05 después de Holm. No se demuestra ausencia de efecto ni causalidad.

## Método

Muestra de 50.000 filas sin limpiar por mes. Ponderación N mensual / 50.000. Unión por fecha UTC tras conversión desde America/New_York. Regresiones diarias con controles de mes, día semanal, temperatura y nieve; HAC con 7 retardos. La duración incluye distancia media.

## Documentación completa

Consultar Memoria_Taxis_Clima_2024_v2.pdf, registros de calidad, resultados estadísticos y notebook.

## Ampliación y razonamiento

El modelo principal tiene fuerte dependencia residual. La variante dinámica estima +0,62% (IC95% -1,21% a +2,49%). Excluir cinco días influyentes da un p nominal de 0,036; se informa como sensibilidad exploratoria, no como confirmación.

La guía Guia_razonamiento.md y las hojas Calculos y Razonamiento de Excel explican para cada paso pregunta, método, motivo y límites. Hay ocho sensibilidades y diagnósticos explícitos.