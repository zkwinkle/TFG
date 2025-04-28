---
toc: yes
header-includes: no
geometry: "left=1.6cm,right=1.6cm,top=1.6cm,bottom=1.6cm"
gradient: no
underline: no
colorlinks: yes
titlepage: yes

title: Aplicación de Técnicas de Aprendizaje Automático para Generación de Circuitos Aproximados
title-english: Application of Machine Learning Techniques for the Generation of Approximate Circuits
subtitle: Informe del Anteproyecto para el Trabajo Final de Graduación
subtitle-english: Report of Pre-project for a Graduation Work in fulfillment of the requirements for the degree of Licentiate in Computer Engineering
logo: template/logo tec.png
author: Ignacio Vargas Campos
month: Febrero
year: 2025
---

# 1. Palabras clave

Computación aproximada, Aprendizaje automático, Reconocimiento de patrones, ASIC, ALS

# 2. Introducción

La computación aproximado es un paradigma que ha surgido ante la necesidad de
realizar cálculos de manera más rápida y eficiente en contextos donde no es
necesario ser 100% preciso. Específicamente, un circuito aproximado es aquel
que permite reducir el consumo de recursos a cambio de una degradació en la
precisión de los resultados. Dentro de este enfoque, los circuitos aproximados
han demostrado ser una solución viable para aplicaciones tolerantes a errores,
como el procesamiento de señales, visión por computadora e inteligencia
artificial, donde la exactitud absoluta no es crítica. Estos circuitos
modifican su lógica para reducir el área, el consumo energético o mejorar el
desempeño, sacrificando exactitud de manera controlada.

Existen múltiples técnicas para aproximar el diseño de circuitos y construir la
circuitería relacionada de manera manual. Sin embargo, este enfoque requiere un
profundo conocimiento sobre el comportamiento del circuito para realizar
aproximaciones y optimizaciones degradando la exactitud de los resultados de
manera controlada. Esto resulta en que el diseño manual sea muy difícil y
aplicable a solo los diseños de circuitos muy específicos para los que se tenga
el amplio conocimiento necesario sobre su topología y comportamiento.

Para abordar estas limitaciones, se ha incursionado en aplicar técnicas para
generar circuitos aproximados dentro del Electronic Design Automation (EDA),
termino que se refiere a utilizar herramientas para automatizar partes de el
diseño de circuitos electrónicos, típicamente automatizan tareas como la
síntesis lógica, la optimización y la verificación de circuitos. Relevante para
el tema del diseño de circuitos aproximados, se cuenta con la Approximate Logic
Synthesis (ALS), término el cual se refiere a una gama de técnicas para mejorar
la eficiencia de un circuito modificando sistemáticamente la funcionalidad sin
exceder un umbral de error definido. Un gran beneficio del ALS es que no hay
necesidad de conocer los detalles de implementación del circuito específico que
se sintetice con estas técnicas.

Se puede ver el ALS como un conjunto de técnicas que realizan una exploración
del espacio de diseño de un circuito. Este espacio está acotado por el umbral
de error permitido en el comportamiento del circuito, dentro de este espacio
buscamos el diseño de circuito que nos lleve a la máxima eficiencia ojalá con
el mínimo error posible. Estas técnicas incluyen heurísticas, algoritmos
evolutivos como los genéticos y, más recientemente, enfoques basados en
aprendizaje automático. Bajo este marco, el aprendizaje automático es
simplemente una técnica más eficiente para encontrar soluciones óptimas dentro
de este espacio de soluciones a través del descenso de gradiente.

AxLS es una plataforma específica para ALS de fuente abierta que aplica
transformaciones en netlists. Al implementar tanto técnicas existentes como
nuevas dentro de esta plataforma, es posible utilizar los mismos métodos para
calcular umbrales de error y métricas de calidad, lo que permite una
comparación más precisa entre diferentes enfoques de ALS. Este trabajo de
investigación buscará implementar técnicas de aprendizaje automático dentro de
esta plataforma, tanto para poder comparar resultados con otras investigaciones
que las han implementado en su ALS, como para comparar los resultados de las
técnicas de aprendizaje automático con otras técnicas diferentes implementadas
en esta plataforma.

# 3. Contexto y antecedentes

El proyecto se realizará en como un proyecto de investigación en el Instituto Tecnológico de Costa Rica. Una de las universidades públicas de Costa Rica, con su sede original en Cartago creada en 1971. Se realizará en colaboración con el departamento de Ingeniería Electrónica.

Este proyecto se encuentra en la intersección de múltiples áreas de
conocimiento relacionadas a la ingeniería en computadores. La computación
aproximada tiene aplicaciones en el campo de la computación de alto desempeño.
Se utilizarán técnicas de aprendizaje automático. También entra en el área de
diseño de circuitos computacionales.

# 4. Descripción del proyecto

## 4.1. Justificación y definición del problema.

Los investigadores del Instituto Tecnológico de Costa Rica no tienen la capacidad de utilizar técnicas de ALS basadas en aprendizaje automático debido a que la herramienta a la que tienen acceso, AxLS, no tiene la capacidad técnica para llevarlas a cabo.

Se desea tener esta capacidad para verificar y comparar los resultados obtenidos por otros investigadores, así como poder proponer y desarrollar sus propias técnicas novedosas de ALS basadas en aprendizaje automático.

## 4.2. Objetivo general

Formular una técnica del estado del arte de aprendizaje automático para ALS en la herramienta AxLS, de manera que permita ser comparada con otras técnicas implementadas dentro de la herramienta así como con otras implementaciones diferentes de las técnicas seleccionadas.

## 4.3. Objetivos específicos

1. Evaluar al menos 3 técnicas de ALS basadas en aprendizaje automático
   determinando cuál es la más apropiada para ser integrada en la herramienta
   AxLS.
2. Adaptar la herramienta AxLS para que sea posible la implementación de la
   técnica escogida, con la consideración de que permita más fácilmente la
   implementación de futuras técnicas de aprendizaje automático.
3. Evaluar los resultados de la técnica de aprendizaje automático implementada
   en AxLS con respecto a resultados obtenidos mediante las técnicas ya
   existentes en la herramienta.

## 4.4. Resultados esperados

#### Técnico

El proyecto mejorará la capacidad de AxLS al adecuarla para la integración de técnicas de aprendizaje automático, lo que permitirá explorar métodos más avanzados de ALS. Esto facilitará la experimentación con nuevos enfoques y la comparación con técnicas preexistentes dentro de la herramienta.

#### Académico y organizacional

Para el Instituto Tecnológico de Costa Rica, el proyecto representa una mejora
en su capacidad de investigación en computación aproximada. Los investigadores
podrán acceder a una plataforma con soporte para aprendizaje automático, lo que
permitirá estudios comparativos y el desarrollo de nuevas técnicas dentro del
campo de ALS.

#### Económico

Aunque el proyecto es de naturaleza académica, la optimización de circuitos mediante ALS tiene aplicaciones en la industria de semiconductores, donde la reducción de consumo energético y área de circuitos puede traducirse en menores costos de fabricación y operación.

#### Ambiental

Si bien el proyecto no tiene un impacto ambiental directo, la optimización de circuitos puede ayudar a reducir el consumo energético en aplicaciones que utilizan hardware especializado, promoviendo un uso más eficiente de los recursos electrónicos.

## 4.5. Supuestos y limitaciones

#### Supuestos

- Se tendrá acceso a información académica relevante, como artículos científicos y publicaciones sobre ALS y aprendizaje automático, para fundamentar la selección de técnicas a implementar.
- Se dispone de un entorno de desarrollo adecuado, incluyendo hardware y software compatibles con la implementación requerida.
- Se presupuestan 12 semanas para la implementación técnica dentro de AxLS, asumiendo que no habrá retrasos significativos por imprevistos.

#### Limitaciones

- La implementación estará restringida a las capacidades actuales de AxLS, lo que podría requerir modificaciones adicionales en su arquitectura para soportar aprendizaje automático.
- El desempeño de la técnica implementada dependerá de la calidad y disponibilidad de los datos utilizados para el entrenamiento y evaluación.

## 4.6. Análisis de riesgos

A continuación, se identifican los principales riesgos que podrían afectar el desarrollo del proyecto y las acciones para mitigar su impacto:

| **Escenario de riesgo** | **Acciones de mitigación** |
|-------------------------|---------------------------|
| **Falta de familiaridad con tecnologías:** La implementación en AxLS requiere conocimientos en herramientas como Yosys, Python e Icarus Verilog, los cuales pueden tener una curva de aprendizaje. | Se planificará una fase inicial de aprendizaje y experimentación con las herramientas antes de iniciar la implementación formal. Se documentará el proceso para facilitar la resolución de dudas. |
| **Cambios en los requisitos del proyecto:** Pueden surgir nuevas necesidades o modificaciones en los objetivos conforme avance el desarrollo. | Mantener comunicación constante con los responsables del proyecto y definir hitos claros para evitar cambios drásticos en fases avanzadas. Priorizar modularidad en la implementación. |
| **Problemas con las herramientas y ambiente de desarrollo:** Pueden surgir conflictos de dependencias, fallos en versiones de software o incompatibilidades con el entorno de trabajo. | Utilizar entornos virtuales y gestionar dependencias con herramientas como `venv` o `conda`. Documentar configuraciones para reproducibilidad y buscar alternativas en caso de fallos críticos. |

# 5. Propuesta metodológica

## 5.1. Tipificación del trabajo a realizar

El trabajo a realiza es una investigación teórico-práctica ya que se realizará
una revisión y análisis de la literatura sobre técnicas de aprendizaje
automático en ALS para escoger cuál será una técnica apropiada y comparar sus
resultados, así como también tendrá la parte práctica de implementar dicha
técnica en la herramienta AxLS.

## 5.2. Descripción general del proceso por realizar

El proceso para alcanzar los objetivos del proyecto se estructura en tres etapas principales.

### 5.2.1 Estudio del estado del arte

Se realizará una investigación de las técnicas existentes en el ámbito de ALS con aprendizaje automático, analizando papers, artículos y trabajos previos para identificar la metodología más adecuada a implementar en AxLS.

### 5.2.2 Adecuación de la herramienta

Se modificarán y extenderán las funcionalidades de AxLS para permitir la integración de la técnica seleccionada. Esto puede incluir ajustes en la arquitectura del software, implementación de nuevos módulos y adaptación de los flujos de procesamiento.

### 5.2.3 Comparación de resultados

Se ejecutarán pruebas con la nueva técnica y se compararán sus resultados con los obtenidos mediante los métodos ya existentes en AxLS. Se analizarán métricas clave para evaluar mejoras en precisión, rendimiento o eficiencia.

## 5.3. Entregables y actividades

### 5.3.1 Entregables

Los entregables del proyecto y su relación con cada objetivo específico se
muestran en la siguiente tabla.

| Identificador | Entregable    | Técnicas / Herramientas | Estrategias de verificación | Objetivo Específico |
| ------- | ---------------------- | ------------ | ---------------- | -------- |
| 100           | Documento de diseño que justifique la escogencia de la técnica de aprendizaje automático a implementar en AxLS, junto con un plan para su entrenamiento. Si hubiesen múltiples técnicas que se están considerando este documento puede mencionarlas y compararlas para llegar a una conclusión de cuál se utilizará. | Zotero para manejo de referencias, procesador de texto de preferencia.            | Documento detalla una técnica en específico, da razones de por qué se escogió tomando en cuenta la factibilidad y relevancia en el estado del arte.                                                            | 1                   |
| 200           | Documento de diseño que explique las adaptaciones necesarias que se harán a AxLS, el módulo que se integrará para aplicar técnicas de ML y cómo usarlo. Así como específicamente cómo lo usará la técnica de aprendizaje automático a implementar.                                                                   | AxLS, Python, Yosys, Icarus Verilog, procesador de texto.                         | Documento detalla la técnica general que se usará para agregar el módulo así como los cambios necesarios a nivel de API.                                                                                     | 2                   |
| 201           | Código adaptado de herramienta AxLS con técnica de AA integrada.                                                                                                                                                                                                                                                     | AxLS, Python, Yosys, Icarus Verilog, git, Github, Pytorch u otra biblioteca de AA | La herramienta AxLS sigue funcionando con todas sus técnicas pasadas y además se puede escoger utilizar la técnica AA y se ejecuta correctamente. La ejecución correcta se validará con un plan de pruebas.  | 2                   |
| 300           | Informe final sobre el proyecto realizado y los resultados encontrados al comparar la técnica de AA con las ya existentes en la herramienta AxLS                                                                                                                                                                     | LaTeX, IEEE, AxLS                                                                 | El informe describe cómo se llevó a cabo el proyecto, la técnica de AA empleada y presenta los resultados de esta técnica comparados con los de las otras técnicas ya existentes en la máquina con gráficos. | 3                   |

### 5.3.2 Actividades

La siguiente tabla presenta las actividades a realizar y su relación con los
entregables.

| Identificador | Actividad        | Horas estimadas | Entregables Relacionados |
| ---------- | ----------------------------------------- | -------- | --------- |
| 100           | Experimentar y familiarizar con AxLS                                                                                                                    | 25              | 100, 200               |
| 200           | Recopilación de literatura de los últimos años sobre aplicación de técnicas de ML en ALS                                                                | 10              | 100                    |
| 300           | Lectura de literatura sobre técnicas de ALS con enfoque en ML                                                                                           | 30              | 100                    |
| 400           | Redactar documento de diseño que justifique la escogencia de la técnica de ML a utilizar                                                                | 15              | 100                    |
| 500           | Redactar documento de diseño qué expliqué cómo se adptará AxLS para integrarse con la técnica de ML y cómo se llevará a cabo la implementación de esta. | 40              | 200                    |
| 700           | Hacer adaptaciones a AxLS necesarias para permitir integrar el módulo diseñado                                                                          | 30              | 201                    |
| 800           | Agregar el módulo planteado para aplicar técnicas de ML                                                                                                 | 30              | 201                    |
| 900           | Crear programas necesarios para el entrenamiento del modelo a emplear.                                                                                  | 30              | 201                    |
| 1100          | Llevar a cabo el entrenamiento y monitoreo del modelo                                                                                                   | 60              | 201                    |
| 1200          | Integración del modelo entrenado con el módulo creado de AxLS                                                                                           | 15              | 201                    |
| 1300          | Comparación y análisis de resultados de AxLS con técnica de ML con otras técnicas.                                                                      | 20              | 300                    |
| 1400          | Redacción de informe final detallando las técnicas empleadas y comparándolas con otras técnicas de la herramienta AxLS.                                 | 20              | 300                    |

## 5.4. Cronograma

A continuación se proporciona el cronograma de actividades que se van a realizar
en cada semana y el estimado de horas a trabajar por semana.

| Semana | Actividades a realizar | Horas estimadas de trabajo por semana |
| ------ | ---------------------- | ------------------------------------- |
| 1      | 100                    | 25                                    |
| 2      | 200, 300               | 20                                    |
| 3      | 300                    | 20                                    |
| 4      | 400, 500               | 25                                    |
| 5      | 500                    | 30                                    |
| 6      | 700                    | 20                                    |
| 7      | 700                    | 20                                    |
| 8      | 800                    | 30                                    |
| 9      | 900                    | 30                                    |
| 10     | 1100                   | 30                                    |
| 11     | 1100                   | 30                                    |
| 12     | 1200                   | 15                                    |
| 13     | 1300                   | 20                                    |
| 14     | 1400                   | 20                                    |

Nota: El cronograma deja al propio las últimas 2 semanas libres para considerar
un colchón por cualquier atraso.

# Apéndice

## Ficha de contactos del proyecto

### Datos del estudiante

| | |
|------------------|----------------------------------------------------|
| Nombre | Ignacio Vargas Campos |
| Correo electrónico | ignacio.vargas@estudiantec.cr |
| Teléfono | +506 88116820 |

### Datos del proyecto

| | |
|------------------|----------------------------------------------------|
| Nombre | Aplicación de Técnicas de Aprendizaje Automático para Generación de Circuitos Aproximados |
| Breve descripción | Implementación de técnicas de aprendizaje automático en AxLS para mejorar la síntesis de circuitos aproximados y comparar su desempeño con métodos existentes. |
| Fecha de inicio | 17 de febrero del 2025 |

### Datos de la empresa u organización

| | |
|------------------|----------------------------------------------------|
| Nombre | Instituto Tecnológico de Costa Rica |
| Nombre contacto | Jorge Castro Godínez |
| Correo electrónico | jocastro@itcr.ac.cr |
| Teléfono | +506 70460449 |
