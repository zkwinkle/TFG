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
  - (Para DT): Si usar un solo árbol multi-salida o un árbol por salida.

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

- [x] Revisar si un solo árbol multi-salida se puede.
- [x] Agregar método DT a AxLS formalmente y genérico para circuitos.
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

### Pasos

1. Leer sets de datos inputs / outputs. `read_values`
2. Convertir sets de datos a representación binaria correcta.
3. Llamar `DecisionTreeClassifier.fit()`
  - Varias veces si muchos trees. Una si single tree multi-output.
4. Convertir árbol a verilog. `tree_circuit.v`
5. Instanciar `Circuit` aproximado.
6. Crear testbench con dataset `tree_circuit.write_tb()`.
7. Calcular error `tree_circuit.simulate_and_compute_error()`.
8. Calcular área `tree_circuit.get_area()`.

- Paso 1 puede ser opcional para que alguien pueda importar datos de donde sea.
  - Puedo proveer método de utilidad para la clase.
- Paso 2 debería ser parte de la clase:
  - Requiere saber las cantidades y orden de los bits.
  - Se pueden pedir los inputs outputs del circuito en formato verilog en orden
  de MSB -> LSB. Que ahora debería ser el default de circuit.inputs y
  circuit.outputs.
- Pasos 3-4 también parte de la clase.
- Pasos 5-8 se pueden hacer independientes de la clase.

### Métodos de la clase

- Creación con config: `__init__(parámetros_míos, input_bits, output_bits, **kwargs_para_scikit)`
- Entrenamiento: `train(X, y)`.
- Conversión a verilog. `to_verilog_file(filename)`
  - Mensaje de error si no ha sido entrenado. Ver ejemplo de scikit:

```
Traceback (most recent call last):
  File "/home/igna/Documents/U/Semestre 13/TFG/AxLS/supervised_learning.py", li
ne 79, in <module>
    print("Prediction:", clf.predict(inputs[0]))
                         ~~~~~~~~~~~^^^^^^^^^^^
  File "/home/igna/Documents/U/Semestre 13/TFG/AxLS/venv/lib/python3.13/site-pa
ckages/sklearn/tree/_classes.py", line 529, in predict
    check_is_fitted(self)
    ~~~~~~~~~~~~~~~^^^^^^
  File "/home/igna/Documents/U/Semestre 13/TFG/AxLS/venv/lib/python3.13/site-pa
ckages/sklearn/utils/validation.py", line 1757, in check_is_fitted
    raise NotFittedError(msg % {"name": type(estimator).__name__})
sklearn.exceptions.NotFittedError: This DecisionTreeClassifier instance is not
fitted yet. Call 'fit' with appropriate arguments before using this estimator.
```
