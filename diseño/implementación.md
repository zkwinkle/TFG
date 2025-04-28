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
  - Si usar el set de datos completo o una versión reducida.
  - Archivo de progreso para reanudar (si no existe empieza uno nuevo y guarda
  ahí, por default si no se especifica empieza uno nuevo y lo guarda con un
  nombre default `.run`, si ya existe un `.run` lo guarda como `.run1`, `.run2`
  y así)
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

# VIEJO

# Plan

## Top-level script

OK quiero llamar un método que sea como:

```python
run_for_benchmarks(benchmark_names: List[string], output_csv: string)
```

Formato csv:

Benchmark | Método          | Métrica 1 | Métrica 2 | ...
----------|-----------------|-----------|-----------|----
Circuito1 | inout           |    5%     |     1     | ...
Circuito1 | glpsignificance |    5%     |     1     | ...
Circuito1 | ccarving        |    5%     |     1     | ...
Circuito1 | probrun         |    5%     |     1     | ...
Circuito1 | decision_tree   |    5%     |     1     | ...
Circuito2 | ...             |    6%     |     2     | ...
...
Circuito3 | ...             |    7%     |     3     | ...
...

Luego puedo manualmente concatenarles con una columna de número de corrida o algo por el estilo para facilitar el procesamiento de datos.

Puedo llamarlo en un loop para correr la suite varias veces.

Sería bueno que si falla algún método poder correr empezando por ese método.

Para eso puedo hacer algo como:

```python
for i in range(0,5):
    name = f"results_{i}.csv"
    if i == 0:
        errored_benchmark_index =
        benchmarks_from_checkpoint = benchmarks[n:]
        run_for_benchmarks(benchmarks_from_checkpoint, name)
    else:
        run_for_benchmarks(benchmarks, name)
```

Aunque sería nice tener una CLI que pudiese hacer esto solo con argumentos... pero no sé si valga la pena.

En parte cortesía de o3-mini:
(No está completo con todo lo que quiero incluir, ver parametrización)

```python
#!/usr/bin/env python3
import argparse
import sys

benchmarks = ["RCA_4b", ..., "max_128b", ...]

run_for_benchmarks(benchmark_names: List[string], output_csv: string):
    """
    Process the given list of benchmarks, and create a csv file containing the
    original circuit's area, the approximated circuit's area, and all the error
    metrics.

    Parameters:
      benchmark_names (list): The list of benchmarks to process.
      output_csv (string): The csv file to output to.
    """

    do_stuff()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a list of benchmarks multiple times.')
    parser.add_argument('--calls', type=int, default=1,
                        help='Number of times to call the function (default: 1)')
    parser.add_argument('--start-name', type=str, default=None,
                        help='Optional starting name from the list for the first iteration')
    parser.add_argument('--iteration-start', type=int, default=1,
                        help='Iteration number to start naming files (default: 1)')
    parser.add_argument('--base-filename', type=str, default="results",
                        help='Base name for the output files (default: results)')
    args = parser.parse_args()

    # Determine if a starting name was passed and exists in the list
    if args.start_name and args.start_name in benchmarks:
        # Create a modified list for the first iteration starting from the specified name
        start_index = benchmarks.index(args.start_name)
        first_iteration_list = benchmarks[start_index:]
        print(f"Starting from '{args.start_name}', the list is: {first_iteration_list}")
    elif args.start_name:
        # If the start-name is provided but not found, print an error and exit.
        print(f"Error: The start name '{args.start_name}' is not in the list of benchmarks.")
        sys.exit(1)
    else:
        # If no start name is provided, use the full list
        first_iteration_list = benchmarks

    # Call the function the specified number of times.
    file_iteration = args.file_start
    for i in range(args.calls):
        filename = f"{args.base_filename}_{file_iteration}.csv"
        print(f"Iteration {i+1}: saving in file {filename}")
        # For the first call, if optional start name was provided, use modified list.
        if i == 0:
            run_for_benchmarks(first_iteration_list, filename)
        else:
            run_for_benchmarks(benchmarks, filename)
        file_iteration += 1  # Increase the file iteration for the next call
```

## Control de parámetros

OK las cosas que quiero parametrizar / controlar / variar entre benchmarks:

- Cuántos datos utilizar
  - Varía por benchmar: Exhaustivo, o porcentaje variable
  - El `run_for_benchmarks` puede calcularlo automáticamente dependiendo de la
    cantidad de entradas del circuito. Probs lo más fácil sea definir thresholds
    de entradas donde cambia de exhaustivo -> 10% -> 5% -> ...
- Max depth del árbol
  - Debería hacer corridas para todos los benchmarks usando el mismo max depth: int
  - No, mejor debería basarme en el threshold de error, e ir incrementando el
    max depth hasta que el árbol esté dentro del threshold. Podría definir un
    max_depth máximo donde ya decido que mamó.
     - Basándome en el mismo threshold de error tendría un punto de comparación
       con los otros algoritmos.

- (Opcional) Si encuentro un método para usar un solo árbol para multi-output, podría ser un parámetro.
  - También debería de ser el mismo para todos los benchmarks: bool

- Resíntesis.
  - También debe ser consistente para todos los benchmarks: bool
  - Si se hace resíntesis se debería de especificar la cantidad de iteraciones
    para los métodos de ML, ya que sería un entrenamiento, resíntesis,
    entrenamiento, resíntesis, ....
      - Se podría controlar con threshold de error.

- Threshold de error:
  - Debería de especificar un threshold de error máximo para los algoritmos de
    pruning.


OK básicamente la función para correr los benchmarks puede tener lógica para
decidir cuántos samples usar. Puedo agregar el max depth del árbol, si usar
resíntesis y (opional) si usar un árbol o muchos como otros argumentos del
script.

## Concerns

- Concern principal: set de datos no reproducibles y no tengo manera de keep track of them o guardar su historial.

- Acabo de pensar que si uso una lista cortada para continuar una iteración que
  se interrumpió, tengo que poder guardar los datos de las ejecuciones antes del
  error (puede ser `try` `catch` o agregar líneas después de cada ejecución)
  para poder continuarlos luego.

  - Ir guardando línea por línea al final de cada benchmark ejecutado es la
    forma más fácil de concatenar los resultados nuevos a los viejos.

  - También podría usar pickle para guardar progreso más programáticamente y no
    tener que decirle en qué benchmark se quedó pegado.

## Pasos generales:

1. Ejecutar otros métodos.
2. Ejecutar método de árbol.

1. Crear `Circuit`:

```python
