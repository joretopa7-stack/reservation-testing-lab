# Preguntas de sustentación

**1. ¿Por qué este miniproyecto se clasifica principalmente como pruebas
unitarias y no como pruebas de integración HTTP?**

Porque cada prueba ejercita una sola unidad de código (una función
validadora o un método del servicio) de forma aislada, sin levantar un
servidor, sin sockets, sin base de datos y sin atravesar capas de
serialización HTTP. Las dependencias externas (repositorio, generador de
código, fecha actual) se sustituyen por objetos controlados desde la propia
prueba mediante fixtures, en vez de usar un cliente HTTP real como haría
una prueba de integración.

**2. ¿Qué regla fue más difícil de convertir en casos de prueba y por qué?**

RN-07 (la reserva debe finalizar máximo a las 17:00) fue la más delicada,
porque no depende solo de la hora de inicio sino de la combinación
hora + duración. Fue necesario diseñar casos de frontera donde la reserva
"casi" cabe (termina exactamente a las 17:00, se acepta) y donde se pasa
por un minuto (termina a las 17:01, se rechaza), variando también la
duración (30 vs. 60 minutos) para confirmar que el cálculo del fin de la
reserva es correcto en ambos casos.

**3. ¿Qué diferencia existe entre una prueba negativa y una prueba de
frontera?**

Una prueba negativa usa un dato claramente inválido, alejado del límite
(por ejemplo, una duración de 90 minutos), para confirmar que el sistema
rechaza entradas incorrectas. Una prueba de frontera usa un dato ubicado
justo en el límite entre lo válido y lo inválido (por ejemplo, la hora
exacta de apertura, 08:00, o el nombre con exactamente 3 caracteres), para
confirmar que la comparación (`<`, `<=`, etc.) está bien construida. Una
prueba de frontera puede ser positiva (el límite se acepta) o negativa (el
límite justo fuera se rechaza).

**4. ¿Por qué se inyecta el generador del código de confirmación?**

Porque si el código se generara internamente con UUID, timestamps o
números aleatorios, las pruebas no podrían predecir ni verificar su valor,
y la suite dejaría de ser determinista. Al inyectarlo como una dependencia
(un *callable* que recibe el servicio por constructor), la prueba puede
sustituirlo por una función fija que siempre devuelve el mismo valor
conocido, y así comprobar exactamente que ese valor llegó a la reserva
creada.

**5. ¿Qué problema podría aparecer si todas las pruebas compartieran el
mismo repositorio en memoria?**

Aparecería contaminación de estado entre pruebas: una reserva creada en una
prueba seguiría existiendo cuando se ejecutara la siguiente, lo que podría
disparar falsos `DuplicateReservationError`, alterar los conteos esperados
de `repository.list()`, y hacer que el resultado de una prueba dependiera
del orden de ejecución de las demás — justo lo que la independencia de
pruebas busca evitar.

**6. ¿Qué ventajas obtuvo al parametrizar escenarios?**

Se redujo la duplicación de código: en vez de escribir una función de
prueba casi idéntica por cada valor de duración inválida o por cada regla
de negocio violada, una sola función parametrizada cubre varios casos. Además,
al usar `pytest.param(..., id=...)`, cada caso aparece identificado por su
nombre en el reporte de ejecución, lo que facilita ubicar exactamente cuál
escenario falló sin tener que leer el cuerpo de la prueba.

**7. ¿Qué fixture considera más útil en su suite y por qué?**

`current_date`. Al fijar la fecha "de hoy" como parámetro inyectado en
lugar de usar `date.today()`, toda la suite queda desacoplada del día real
en que se ejecuta: las pruebas de fechas pasadas, futuras y de fin de
semana producen siempre el mismo resultado sin importar cuándo se corra
`pytest`, lo cual es indispensable para que la suite sea reproducible.

**8. ¿Cómo comprobó que una validación fallida no modifica el
repositorio?**

Con pruebas que, tras capturar la excepción esperada con `pytest.raises`,
verifican inmediatamente que `repository.list()` sigue vacío
(`test_invalid_reservation_is_not_saved_in_repository` y la versión
parametrizada `test_create_rejects_invalid_data_for_each_business_rule`).
Como el repositorio es una instancia nueva por prueba (fixture), cualquier
elemento que aparezca ahí solo pudo haber sido agregado por la llamada que
se está probando.

**9. ¿Qué cambiaría cuando esta lógica se conecte posteriormente con
FastAPI?**

`ReservationService` y los validadores no cambiarían: seguirían siendo
lógica de dominio pura. Lo que se añadiría es una capa superior — endpoints
FastAPI que reciban el `dict` de entrada (por ejemplo, vía un modelo
Pydantic), lo pasen a `ReservationService.create()`, y traduzcan las
excepciones del dominio (`InvalidCustomerNameError`,
`DuplicateReservationError`, etc.) a códigos de estado HTTP apropiados
(400, 409, etc.). Las pruebas de esa capa ya no serían unitarias sino de
integración, usando `TestClient` de FastAPI, y se sumarían a esta suite sin
reemplazarla.
