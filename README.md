# De A Mentis

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

---

# Proyecto De A Mentis – Detector Educativo y Contextualizador de Noticias

## ¿Qué problema se plantea resolver?

En un entorno digital saturado de información, la desinformación circula rápidamente y con gran alcance. El problema no es solo identificar si una noticia es falsa, sino que gran parte de la población carece de herramientas para evaluar críticamente el contenido que consume.  

Este proyecto busca ofrecer una solución que vaya más allá de una simple etiqueta de *“verdadero”* o *“falso”*. Su propósito es **fomentar la alfabetización informacional (data literacy)** mediante un sistema que:

- Analiza señales de alerta en el texto (como cifras sin fuente, lenguaje exagerado, citas ambiguas, etc.).
- Advierte al usuario cuando ciertos elementos requieren atención o verificación adicional.
- Contextualiza la noticia con información verificada, utilizando un sistema de recuperación (RAG) basado en bases de datos de fact-checking.

## ¿Por qué es un problema importante?

Instituciones educativas, organizaciones civiles y medios de comunicación tienen un interés directo en combatir la desinformación, no solo por sus efectos inmediatos, sino por su impacto a largo plazo en la confianza pública, la participación ciudadana y la salud democrática.

Este proyecto puede integrarse en iniciativas de educación cívica y alfabetización digital, como ocurre actualmente en países líderes en este ámbito (ej. Finlandia), promoviendo un consumo de información más crítico, autónomo y responsable.

## ¿Qué tipo de problema de aprendizaje implica?

En esta fase del proyecto aún se está definiendo el esquema de clasificación más adecuado. Sin embargo, se contempla un enfoque más amplio que la típica clasificación binaria (*falsa* vs *verdadera*), con el objetivo de capturar matices como:

- Nivel de veracidad.
- Nivel de alarmismo.
- Ausencia de contexto o evidencia.

Además, el sistema incluye tareas auxiliares como:

- **Generación de alertas tempranas** (basadas en características lingüísticas y semánticas).
- **Recuperación de contexto verificable** mediante un sistema RAG conectado a fuentes de fact-checking confiables.

## ¿Qué métricas se utilizarán para evaluar el sistema?

Las métricas dependerán del enfoque final de clasificación y de los subcomponentes del sistema. De forma general, se consideran:

### Para el clasificador:
- **Accuracy** (precisión global).
- **F1-score macro y weighted**, especialmente si hay clases desbalanceadas.
- **Matriz de confusión**, para identificar confusiones comunes entre categorías.

### Para el sistema de alertas:
- **Precisión de alerta** (proporción de alertas útiles).
- **Recall de alerta** (proporción de señales relevantes detectadas).

### Para el sistema RAG:
- **Cobertura contextual** (proporción de noticias que encuentran contexto útil).
- **Relevancia de las fuentes sugeridas** (medida cualitativa a validar con usuarios o expertos).

## ¿Cómo se alinean estas métricas con los objetivos del proyecto?

Este proyecto no busca reemplazar el juicio humano con una clasificación automática, sino complementarlo. Las métricas del sistema están pensadas para garantizar:

- Que el modelo no simplifique en exceso un problema complejo.
- Que se priorice la claridad educativa sobre la precisión puramente técnica.
- Que cada salida del sistema (alerta o contextualización) sea una **oportunidad de aprendizaje** para el usuario.

---

### 🔄 Estado actual del proyecto

- 🔬 Exploración de datos y diseño de características en curso.
- 📊 Definición de categorías de clasificación (en desarrollo).
- 📚 Construcción del corpus de fact-checking para el sistema RAG.
- 🧠 Prototipo inicial de modelo binario (verdadera/falsa) en fase de validación.

---

¿Te gustaría que agregue una sección con los requisitos técnicos, instrucciones para ejecutar el prototipo, o cómo contribuir al repositorio?

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         de_a_mentis and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── de_a_mentis   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes de_a_mentis a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

--------

