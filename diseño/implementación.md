# Resultados a generar

Quiero generar los próximos resultados que pueden presentarse como tablas
gigantes (para el apéndice). Luego

- Comparación de DT con diferentes `max_depths`. (Repetir todo 5 veces y poner mejor)

- Luego tomamos el `max_depth` mínimo que está por debajo de un threshold de
  error y le aplicamos iteraciones resíntesis. Con un máximo de iteraciones (5?
  10?) o hasta que llegue al threshold. (Repetir 5 veces y poner mejor)

- Comparación de todos los métodos sin resíntesis.
  - Entre los diferentes resultados de DT (que dependen de `max_depth`), se
  escoge el que tenga menor área por encima de un threshold de error. Si ninguno
  está por encima del umbral entonces el que tenga el mejor error.
  - Para los demás métodos podemos aplicar iteraciones hasta que lleguen al
  umbral de error. (Repetir 5 veces y poner mejor)

- Comparación de todos los métodos con resíntesis.
  - Solo hay 1 resultado de DT por escoger.
  - Para los demás métodos se hace el mismo proceso que sin resíntesis pero
    aplicando resynth entre cada eliminación. (Repetir 5 veces y poner mejor)

Para todo debería de keep track de cuánto tiempo tomó el procesamiento.
Para todo debería de generar todas las métricas de error. Cuando presente y
analice los datos decido cuál es más relevante dependiendo del tipo de circuito
o simplemente las que sean más fáciles de interpretar.

Poner una tabla para la cantidad de entradas y salidas de cada prueba.

Para la presentación y análisis de datos puedo seguir estrategias como las de
"Circuit Learning: From Decision Trees to Decision Graphs". Presentar tablas
reducidas con solo los casos donde hay mejoras, hablar de los trends generales,
separar casos aritméticos vs lógicos.

# Requerimientos

- Poder ejecutar cualquiera de los métodos dentro de AxLS.

- Tomar los parámetros de configuración necesarios y que sean especificables
  programáticamente o con un CLI a través de banderas.

- Se deben de tomar en cuenta las siguientes opciones:
  - Umbral de error. Será necesario en los siguientes casos:
    - DT con resíntesis.
    - Cualquier ejecución de un método de poda.
  - Si ejecutar con o sin resíntesis.
  - Si usar el set de datos completo o una versión reducida (aceptar un %).
    - Puede ser diferente para cada benchmark, esto podría ser solo programático
      si se complica.
  - Archivo de progreso para guardar progreso.
    - Si no se especifica no guarda nada.
    - Si se especifica, va a requerir otro parámetro para determinar si se
    continúa o sobreescribe.
    - Si no está el parámetro de continuar, da un warning (como el de ffmpeg) de
    si se quiere sobreescribir.
```
File 'Anteproyecto-IgnacioVargasCampos.mp4' already exists. Overwrite? [y/N]
```
  - (Para DT): Requerir `max_depth`, que puede ser especificado para cada
  benchmark (Lo de un `max_depth` diferente para cada benchmark podría ser solo
  programático si se complica por CLI).
  - (Para DT con resíntesis): Máximo de iteraciones de resíntesis y el umbral
  de error (dado con la configuración normal de umbral de error).
  - Si mostrar progreso de testbenches o no (Ver TODO abajo sobre probar
  hipótesis).

- Cronometrar la ejecución de cada método completo (desde tener el circuito
original hasta evaluar el error final del circuito final aproximado).

- Calcular todas las métricas de error para cualquier método.

- Capacidad de reanudar ejecuciones interrumpidas. Tendrá que guardar:
    - Configuración de la ejecución.
    - Progreso actual de la ejecución.

- Mostrar datos de ejecución (cronómetro y output normal) mientras suceden para

- Poder obtener un set de datos exhaustivos para circuitos de pocas entradas (16 o menos).
- Poder obtener un set de datos representativo (1-10% de datos) sin sustitucion para circuitos mayores.

- Poder validar el circuito contra la tabla de verdad entera para circuitos de pocas entradas (16 o menos)
- Poder validar el circuito con un set de datos representativo (1-10% de datos) sin sustitución diferente al set de entrenamiento para circuitos mayores.
  - El set de validación debería ser lo más grande posible.
  - Debe usar los mismos sets de entrenamiento y validación para todas las
  pruebas y métodos.
  - Poder usar versiones disminuidas de los sets para trabajar más rápido.
  - Poder controlar si usar testbenches que usan progreso o que no, para
  ejecutar más rápido maybe (**TODO: Probar esta hipótesis**).

- Poder convertir los datos recolectados a CSV al final de la ejecución.
  - Posiblemente esto lo puede hacer otro script?

- Tiempo máximo de ejecución de un benchmark: 5mins. Esto nos da un peor caso de
  ejecución de la suite completa de 2h30min.

## Concerns

- Concern principal: set de datos de validación no reproducibles? Podría
generar un set de validación para cada circuito y usar el mismo siempre y
subirlo a algún lado?

# TODO

## ML

- [ ] Revisar si un solo árbol multi-salida se puede.
- [ ] Generar sets de datos a utilizar en todos los experimentos.
  - [ ] Adaptar AxLS para poder crear sets de datos exhaustivos.
  - [ ] Adaptar sets de datos aleatorios para que no haya repetición.
  - [ ] Hacer pruebas con benchmarks de 128 bits para determinar cuántos datos
        para un tiempo de ~5 mins.

## Herramienta

- [ ] Hacer una función que valide la configuración.
- [ ] Hacer un __main__ que acepte la configuración a través de CLI.
- [ ] Hacer que la función de ejecución principal itere los benchmarks y guarde
      el progreso.
- [ ] Hacer que la función de ejecución principal cronometre las ejecuciones
    - [ ] Muestre cronómetro usando un thread secundario (creo que así se
    tendría que hacer)
    - [ ] Guarde tiempo en objeto (o dict) de resultados.
- [ ] Agregar DTs como un método formal de la herramienta.
- [ ] Crear funciones para la ejecución de cada método dentro de la herramienta.
  - [ ] InOuts In
  - [ ] InOuts Out
  - [ ] ccarving
  - [ ] glpsignificance
  - [ ] Probrun
  - [ ] DT

## Implementación DT

Voy a usar la biblioteca de scikit-learn para la implementación de DT.

## OK tengo que reescribir esto con los detalles nuevos que noté en supervised_kelearning.py y también lo quiero reescribir como sin usar constantes y así

1. Leer set de datos

```python
def read_values(filename, base, max_lines):
    with open(filename, "r") as f:
        return [
            [int(x, base) for x in line.split()] for _, line in zip(range(max_lines), f)
        ]

DATASET = f"../ALS-benchmark-circuits/{NAME}/dataset"
OUTPUT = f"../ALS-benchmark-circuits/{NAME}/output0.txt"


# inputs = [[1, 2, 2], [1, 6, 9], ...]
inputs = read_values(DATASET, 16, 100)
# ouputs = [ [5], [16], ... ]
outputs = read_values(OUTPUT, 10, 100)
```

2. Para que el árbol se entrene como un árbol de decisión booleano hay que pasar los datos a binario:

```python
# TODO: Este procedimiento se tiene que adaptar para funcionar entradas y
# salidas arbitrarias

# inputs = [ [1, 0, 0, 1, 0, 0, 0, 1, 0], [1, 0, 1, 1, 0, 1, 0, 0, 1], ... ]
[ [0, 0, 1, 0, 0, 0, 0, 1, 1, 1], [0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1],
inputs = [
    [int(b) for num in ([f"{x[0]:01b}"] + [f"{x:04b}" for x in x[1:]]) for b in num]
    for x in inputs
]

# outputs = [[0, 0, 1, 0, 1], [1, 0, 0, 0, 0]]
outputs = [[int(b) for b in f"{y[0]:05b}"] for y in outputs]
````
