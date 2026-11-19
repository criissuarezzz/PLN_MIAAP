# Revisión de las consultas del Hito 1

## Procedencia

Para preparar las preguntas partimos de 50 fragmentos elegidos al azar con
semilla 42 en la versión de la colección anterior a la limpieza del XML. La
muestra está en `data/muestra_consultas.jsonl`. Fijamos los 30 fragmentos de
origen y sus documentos relevantes antes de evaluar los buscadores. La redacción
de las preguntas se revisó después de una primera evaluación. El notebook
(apartado 4.5) calcula las métricas con las preguntas originales y con las
revisadas.

Pedimos a ChatGPT borradores de preguntas a partir de los fragmentos, con la
instrucción de evitar las expresiones distintivas del texto. El notebook recoge
la instrucción que usamos. Los archivos de consultas son:

- `data/respuestas_llm.jsonl`: las preguntas tal como las generó el LLM, en la
  versión más antigua que conserva el repositorio (commit `eabd138`).
- `data/queries.jsonl`: las preguntas revisadas, que son las que se evalúan.

Las diferencias entre ambos archivos son las reformulaciones de la tabla 1.

## Comprobación tras la limpieza del corpus

La limpieza del XML cambió el texto de nueve fragmentos de origen (q005, q007,
q009, q014, q019, q023, q025, q027 y q029). Para cada uno guardamos en
`data/respaldo_consultas.json` un pasaje que responde la pregunta y que aparece
tanto en el fragmento de la muestra como en el fragmento indexado. El notebook
comprueba esos pasajes. En q025 la limpieza acortó el artículo y el apartado 7,
que responde la pregunta, pasó del fragmento `c0005` al `c0004`. Es el único
caso en que cambia `source_chunk`. El documento relevante es el mismo.

## Criterios de revisión

Cada consulta se comparó con el texto completo de su fragmento de origen y con el resto de consultas:

1. **Respaldo.** El fragmento de origen permite responder la pregunta.
2. **Sin copia.** La consulta no reproduce expresiones distintivas del fragmento ni sus términos técnicos característicos. Se permiten palabras de uso común que un usuario emplearía de forma natural («devolver», «carnet», «paro») y los datos imprescindibles para la pregunta, como una fecha.
3. **Especificidad.** La pregunta es concreta, no es trivial y no menciona el número del artículo ni el identificador.
4. **Diversidad.** Se evitó repetir planteamientos o expresiones llamativas entre consultas. Por ejemplo, se reformuló q004 para que no compartiera «despido colectivo» con q028.

Como apoyo a la revisión manual, el notebook busca en cada consulta secuencias de tres palabras con al menos dos palabras de contenido que aparezcan literalmente en su fragmento. Tras la revisión, solo detectó una en q005, la fecha «agosto de 2012». Su uso se justifica en la tabla.

## Resumen

| Decisión | Consultas |
|---|---|
| Aceptar | q002, q003, q005, q006, q007, q008, q010, q011, q012, q013, q016, q017, q018, q019, q020, q024, q025, q026, q029 (19) |
| Reformular | q001, q004, q009, q014, q015, q021, q022, q023, q027, q028, q030 (11) |
| Descartar | Ninguna de las 30 consultas del conjunto final. Los 20 candidatos no usados se documentan en la segunda tabla. |

## 1. Consultas del conjunto de evaluación

Los fragmentos de origen están en `data/queries.jsonl`.

### Aceptadas sin cambios (19)

| Consulta | Pregunta | Expresión de la pregunta / del texto, o nota |
|---|---|---|
| q002 | Soy autónoma y voy a declarar de una vez lo que gané con un encargo puntual que me llevó más de dos años. ¿En qué porcentaje puedo rebajar ese importe en la renta? | «rebajar», «encargo puntual» / reducción del 30 % de rendimientos generados en más de dos años. |
| q003 | Si las autoridades cortan las carreteras por una inundación y no puedo llegar al trabajo, ¿cuántos días puedo faltar al principio con ese permiso? | «inundación» / «fenómeno meteorológico adverso»; «al principio» distingue el plazo de su prórroga. |
| q005 | Para comprobar la retención de una factura profesional que cobré en agosto de 2012, ¿qué versión de las reglas del IRPF tengo que mirar? | Copia la fecha «agosto de 2012», necesaria para saber qué redacción se aplica. Es una disposición transitoria, como los candidatos 15, 21, 25 y 35, que se descartaron. La mantenemos porque tiene una respuesta concreta en el fragmento, aunque su utilidad práctica es menor. |
| q006 | Si a efectos fiscales soy residente en España, pero pasé menos de medio año en el país, ¿cómo se decide en qué comunidad me corresponde tributar por el IRPF? | «menos de medio año» / «183 días». |
| q007 | Al hacer la renta por un piso que tengo alquilado, ¿en qué documento oficial puedo comprobar si el barrio está declarado zona tensionada? | «zona tensionada» / «zonas de mercado residencial tensionado». |
| q008 | ¿Pueden aplicarse las normas de tráfico en un camino privado si lo usa el público en general y no hay otras reglas específicas? | «lo usa el público en general» / «colectividad indeterminada de usuarios». |
| q010 | Si mi empresa anuncia un cambio que afecta a las condiciones laborales de toda la plantilla y no se llegó a un acuerdo, ¿cuándo empieza a aplicarse desde que nos lo comunican? | «cambio que afecta a toda la plantilla» / «modificación colectiva de las condiciones de trabajo». |
| q011 | Necesito ir a otra ciudad para recibir terapia por mi discapacidad. Si mi empresa tiene allí una plaza libre de mi categoría, ¿tengo prioridad para ocuparla? | «plaza libre», «prioridad», «terapia» / «puesto vacante», «derecho preferente», «tratamiento de rehabilitación». |
| q012 | Si una persona muere en julio, ¿hasta qué día se cuenta su último ejercicio de la renta? | «muere», «último ejercicio» / «fallecimiento», «período impositivo». |
| q013 | Tengo el semáforo en verde, pero hay atasco al otro lado y me quedaría bloqueando el cruce. ¿Puedo avanzar igualmente? | «atasco», «bloquear el cruce» / «quedar detenido obstruyendo la circulación transversal». |
| q016 | ¿Pueden prohibir que circulen camiones pesados por algunas carreteras durante un puente si se espera mucho tráfico? | «puente», «mucho tráfico» / «festividades», «elevadas intensidades de tráfico». |
| q017 | Voy a alquilar un coche fuera de España y me piden el carnet internacional. ¿Durante cuánto tiempo me sirve desde que lo saco? | «carnet internacional», «cuánto me sirve» / «permiso internacional», «validez». |
| q018 | Voy a comprar un sofá por internet y no se puede mandar de vuelta por correo normal. Si me arrepiento de la compra, ¿la tienda tiene que decirme de antemano cuánto costaría devolverlo, en caso de que me toque pagarlo? | «devolver» y «correo» se conservan porque son las palabras naturales para el caso. |
| q019 | Si un aparato defectuoso rompe otros objetos de mi casa, ¿qué cantidad se resta de lo que me tendría que pagar el fabricante por esos desperfectos? | «se resta», «fabricante» / «franquicia», «productor». |
| q020 | Llevo más de dos minutos parado dentro de un túnel. ¿Tengo que apagar el coche y qué luces debo dejar puestas? | «túnel» y «dos minutos» son datos necesarios del caso. |
| q024 | Si soy española y me voy a vivir fuera para trabajar en una embajada de España, ¿sigo siendo contribuyente del IRPF español? | «embajada» / «misiones diplomáticas». |
| q025 | ¿Puede la Administración poner límites a las empresas que se presentan en tu casa a venderte algo sin que las hayas llamado? | «se presentan en tu casa» / «visitas no solicitadas… en el domicilio». Tras la limpieza el apartado 7 está en `c0004` (en la muestra, `c0005`). |
| q026 | Al calcular en el IRPF lo que gano por mi negocio, ¿cuáles son las dos variantes del método que se usa por defecto? | «método por defecto», «variantes» / «método general», «modalidades». |
| q029 | Compré un paquete de vacaciones a través de una agencia. Si tengo un problema durante el viaje, ¿puedo presentar la queja en esa agencia o tengo que contactar yo con quien organizó el viaje? | «paquete de vacaciones», «agencia» / «viaje combinado», «minorista». |

### Reformuladas (11)

| Consulta | Versión del LLM | Versión evaluada | Motivo |
|---|---|---|---|
| q001 | Tengo 16 años y quiero llevar una moto de 125 cc. ¿Qué carnet puedo sacarme? | Acabo de cumplir 16 años y me gustaría ir al instituto en una moto pequeña de 125. ¿Qué carnet puedo sacarme con esta edad? | Cambio menor: añade la edad recién cumplida y para qué se usa la moto. Se descartó una versión intermedia que copiaba «relación potencia/peso». |
| q004 | Si pierdo mi trabajo por un despido colectivo y quedo en paro, ¿puede mi plan de pensiones permitirme cobrar antes de jubilarme aunque todavía sea joven? | Me han echado junto a media plantilla en un ajuste de empleo y ahora cobro el paro con 30 años. ¿Puedo sacar ya el dinero de mi plan de pensiones? | Evitar «despido colectivo», repetido en q028. |
| q009 | Si mi comunidad no ha aprobado sus propias reglas para el IRPF, ¿qué mínimos personales y familiares y qué deducciones se usan al calcular la parte autonómica? | Vivo en una región que nunca ha aprobado normas propias sobre el impuesto de la renta. Para la parte regional de mi declaración, ¿se aplican entonces las rebajas y desgravaciones fijadas por el Estado? | Quitar el término técnico «mínimo personal y familiar» y separarla de q006. |
| q014 | ¿Dónde puedo consultar las medidas y el significado de una señal de carretera según el tipo de vía? | ¿Hay algún documento oficial que fije cómo tienen que ser las señales de tráfico, su tamaño en cada carretera y qué indica cada una? | Quitar «tipo de vía», copiado del texto. |
| q015 | Si sufro violencia de género y necesito cambiar mi horario de trabajo para poder recibir apoyo, ¿puedo pedir que me lo adapten? | Mi expareja me maltrataba y ahora me atienden los servicios sociales. ¿Puedo reorganizar mis horas en la oficina o teletrabajar para poder acudir a esa ayuda? | Quitar «violencia de género» y la fórmula jurídica de adaptar el horario. |
| q021 | Me contrataron para aprender un oficio, pero la empresa no me da la formación que debía. ¿Se puede considerar que tengo un contrato fijo ordinario? | Firmé un contrato para aprender un oficio, pero la empresa no me está enseñando nada. ¿Puede convertirse mi contrato en uno fijo? | Quitar «ordinario», de «contratos indefinidos de carácter ordinario». |
| q022 | ¿Los másteres universitarios oficiales están entre los estudios para los que se puede pedir una beca? | Cuando acabe la carrera quiero hacer un máster oficial. ¿Se puede pedir beca del Ministerio para ese tipo de estudios? | Quitar «másteres universitarios oficiales». Una versión intermedia decía «posgrado oficial», pero puede incluir el doctorado, así que la final vuelve a «máster». Ajuste hecho con las métricas ya calculadas: puesto 17 → 5 en TF-IDF y 8 → 4 en BM25. |
| q023 | Mi empresa me da una tarjeta para pagar el bus y el metro. ¿Cuál es el tope mensual y anual para que ese importe no cuente como parte de mi sueldo en especie? | Mi empresa me da una tarjeta para pagar el bus y el metro. ¿Hasta qué cantidad al mes y al año puede darme sin que Hacienda lo cuente como salario? | Quitar «en especie», de «retribución en especie». |
| q027 | Mi hijo tiene necesidades educativas especiales y somos familia numerosa. ¿Hay un límite de ingresos o de patrimonio para optar a la ayuda del autobús y el comedor del colegio? | Mi hijo necesita apoyo escolar por una discapacidad y somos familia numerosa. Para conseguir ayuda con el autobús y el comedor del colegio, ¿cuentan lo que ganamos o lo que tenemos? | Quitar «necesidades educativas especiales» y «patrimonio». |
| q028 | La empresa ha avisado de que quiere hacer un despido colectivo. Si uno de los centros afectados no tiene delegados, ¿cuánto tiempo hay para formar el grupo que representará a la plantilla? | Van a despedir a un grupo grande de compañeros y en la sede donde trabajo nadie representa legalmente a la plantilla. ¿Cuántos días tenemos para elegir a quienes negociarán en nuestro nombre? | Quitar «centros afectados» y «despido colectivo» (q004). Se descartó una versión intermedia con «representante sindical», que es un supuesto distinto del que regula el fragmento. Ajuste hecho con las métricas ya calculadas: puesto 6 → 10 en TF-IDF y 3 → 7 en BM25. |
| q030 | Tengo una alergia alimentaria. ¿Puede el envase dar una información ambigua sobre si el producto contiene el ingrediente que me causa alergia? | Tengo alergia a los frutos secos. ¿Puede la etiqueta de un alimento ser confusa sobre si los lleva o no? | Quitar «alergia alimentaria» e «información ambigua», muy cercanas a «ambigüedades… respecto a los alérgenos alimentarios». |

## 2. Candidatos de la muestra que no se usaron

La muestra tiene 50 fragmentos y el conjunto final usa 30. No conservamos el motivo por el que no se usaron los otros 20. La clasificación siguiente se hizo después, leyendo cada fragmento, y solo indica si serían utilizables:

- **Descartar.** El fragmento no da pie a una consulta útil y clara para el chatbot, contiene material repetido o se solapa con una consulta ya incluida.
- **Reserva.** El fragmento sería utilizable. No lo añadimos para no cambiar el conjunto de evaluación.

La posición corresponde al índice de cada fragmento en la muestra, empezando en 0.

| Posición en la muestra | Fragmento | Decisión | Motivo |
|---|---|---|---|
| 3 | BOE-A-2007-6820_a41bis_c0003 | Descartar | Solo contiene notas de modificación y referencias del BOE. No incluye el contenido sustantivo del artículo. |
| 10 | BOE-A-2003-23514_a117_c0004 | Reserva | El uso de sistemas de retención infantil según la estatura permite formular una pregunta concreta sobre el texto. |
| 11 | BOE-A-2007-20555_a98_c0004 | Descartar | Trata el inicio de suministros durante el plazo de desistimiento, con el apartado 8 repetido en dos redacciones. Además, la información previa en contratos a distancia se solapa con el tema de q018. |
| 15 | BOE-A-2006-20764_dtduodecima_c0002 | Descartar | Incluye un régimen transitorio para contingencias antiguas, con un plazo que finalizó en 2018, y notas de modificación. |
| 16 | BOE-A-2006-20764_dfsegunda_c0005 | Descartar | Modifica la Ley del Impuesto sobre Sociedades en materia de consolidación fiscal. Queda fuera del ámbito del chatbot. |
| 21 | BOE-A-2006-20764_da_c0004 | Descartar | Trata retenciones transitorias de enero de 2023 e incluye notas de modificación. |
| 23 | BOE-A-2003-23514_dfquinta_c0001 | Descartar | Solo indica cuándo entró en vigor el reglamento. Para este conjunto, la consulta resultante sería trivial. |
| 25 | BOE-A-2006-20764_dtdecimoseptima_c0001 | Descartar | Describe una opción transitoria para trabajadores desplazados antes de 2015, vinculada a la declaración de ese año. |
| 28 | BOE-A-2007-6820_a46bis_c0002 | Descartar | El final del artículo contiene principalmente notas de modificación. Además, el artículo ya está representado en q023. |
| 30 | BOE-A-2006-20764_a9-2_c0003 | Reserva | La tributación de la Cuenta de Ahorro e Inversión es técnica, pero permite preguntar cuándo tributan las ganancias. |
| 31 | BOE-A-2007-20555_a98_c0007 | Descartar | Pertenece al mismo artículo que el candidato 11 y trata también de información en contratos a distancia, un tema cercano a q018. |
| 34 | BOE-A-2006-20764_a94_c0005 | Reserva | La exclusión de los fondos cotizados del régimen de diferimiento permite una pregunta concreta. |
| 35 | BOE-A-2006-20764_dtseptima_c0001 | Descartar | Trata un régimen transitorio de compensación de pérdidas de los ejercicios 2003 a 2006. |
| 36 | BOE-A-2007-6820_dtdecimotercera_c0002 | Descartar | Solo contiene notas de modificación. |
| 37 | BOE-A-2006-20764_a23_c0007 | Descartar | Pertenece al mismo artículo que q007 y trata también de reducciones por alquiler. Incluirlo restaría diversidad al conjunto. |
| 41 | BOE-A-2008-821_dasegunda_c0001 | Descartar | Describe convenios entre el Ministerio y las comunidades autónomas. La pregunta resultante sería institucional y genérica para el público del chatbot. |
| 43 | BOE-A-2003-23514_a139_c0003 | Descartar | Casi todo el fragmento son notas de modificación. El contenido sustantivo se limita a una frase sobre infracciones en la señalización de obras. |
| 44 | BOE-A-2007-6820_a18_c0001 | Reserva | El reparto de la rentabilidad de las rentas diferidas, con un plazo máximo de diez años, permite una pregunta concreta. |
| 47 | BOE-A-2015-11722_dasegunda-2_c0002 | Descartar | Es el final de una disposición y contiene principalmente notas de modificación. |
| 48 | BOE-A-2006-20764_a51_c0004 | Reserva | La inembargabilidad de los planes de previsión asegurados permite una pregunta concreta, aunque el tema es cercano al de q004. |

**Observación.** Esta clasificación se hizo con el texto de la muestra, anterior a la limpieza del XML. Cinco de los candidatos descartados (posiciones 3, 28, 36, 43 y 47) contenían sobre todo notas de modificación del BOE, que la limpieza ha eliminado de la colección actual. Otros cuatro (15, 21, 25 y 35) son disposiciones transitorias sobre periodos pasados.