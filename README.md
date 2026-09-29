# Simulador inteligente de mantenimiento

Proyecto académico de simulación de una línea de producción con fallas y mantenimiento.

## ¿Qué hace?

El usuario puede:

1. Definir las variables iniciales del sistema.
2. Seleccionar qué variables quiere explorar.
3. Definir mínimos, máximos y pasos.
4. Definir restricciones.
5. Elegir un objetivo de decisión.
6. Ejecutar múltiples escenarios.
7. Filtrar los escenarios que no cumplen las restricciones.
8. Seleccionar automáticamente un escenario factible según el objetivo.
9. Visualizar resultados.
10. Descargar los resultados en CSV.

## Arquitectura

- `simulation.py`: motor de simulación.
- `decision.py`: generación de escenarios, restricciones y selección.
- `app.py`: interfaz web con Streamlit.
- `requirements.txt`: dependencias.
- `README.md`: instrucciones.

## Ejecutar en una computadora

Abre una terminal dentro de esta carpeta y ejecuta:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Después se abrirá la aplicación en el navegador.

## Publicarlo para compartir

Una opción sencilla es subir estos archivos a un repositorio de GitHub y desplegar el proyecto en un servicio compatible con Streamlit.

El archivo de entrada es:

```text
app.py
```

El servicio instalará las dependencias indicadas en:

```text
requirements.txt
```

## Lógica de decisión

La aplicación no inventa los resultados de los escenarios.

El flujo es:

Usuario → variables/rangos → generación de escenarios → simulación → restricciones → escenarios factibles → objetivo → selección → explicación.

La selección significa "mejor dentro de los escenarios simulados y según el objetivo configurado", no una garantía de que el escenario sea universalmente óptimo fuera del modelo.

## Relación con la metodología de siete pasos

1. Contexto: paros de línea por fallas y mantenimiento.
2. Variables: tiempo entre fallas, mantenimiento, producción, máquinas y variables de estado/salida.
3. Unidades: minutos, piezas/minuto, piezas, porcentaje, número de máquinas.
4. Máximos y mínimos: configurados por el usuario.
5. Prototipo: interfaz web con entradas, restricciones, resultados, alertas y gráficas.
6. Simulación: ejecución repetida de escenarios.
7. Conciencia/IA: módulo de decisión e interpretación basado en resultados calculados.

Para convertir el módulo de interpretación en una IA generativa real se puede añadir posteriormente una API de un modelo de lenguaje, manteniendo el motor de simulación como fuente de resultados.
