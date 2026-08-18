# Reservation Testing Lab

Suite de pruebas unitarias con **Pytest** para la lógica de negocio de un sistema
de reservas (asesoría, soporte y demostración), construida como miniproyecto
evaluable del Módulo II del curso *Pruebas de Software*.

## Objetivo del miniproyecto

Diseñar e implementar, sin levantar un servidor FastAPI y sin usar una base de
datos real, una suite de pruebas unitarias que valide las reglas de negocio de
un componente de reservas: nombre del cliente, servicio, duración, fecha,
horario de atención, reservas duplicadas y generación del código de
confirmación. El proyecto aplica Arrange-Act-Assert, `pytest.raises`,
parametrización y fixtures, manteniendo cada prueba independiente.

## Requisitos previos

- Python 3.12 o superior
- `pip`
- Git (opcional, solo si se desea clonar/versionar el repositorio)

## Creación y activación del entorno virtual

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## Instalación de dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Verificar la instalación de Pytest:

```bash
python -m pytest --version
```

## Ejecutar la suite de pruebas

Suite completa:

```bash
python -m pytest -v
```

Solo los validadores:

```bash
python -m pytest tests/test_validators.py -v
```

Solo las pruebas relacionadas con duración:

```bash
python -m pytest -k duration -v
```

Detenerse en el primer fallo (útil durante depuración):

```bash
python -m pytest -x -v
```

## Reglas de negocio verificadas

| ID    | Regla |
|-------|-------|
| RN-01 | El nombre del cliente debe tener mínimo 3 caracteres después de eliminar espacios al inicio y al final. |
| RN-02 | Los servicios permitidos son: `asesoria`, `soporte` y `demostracion`. |
| RN-03 | La duración permitida es únicamente 30 o 60 minutos. |
| RN-04 | No se puede crear una reserva para una fecha anterior a la fecha actual recibida por el servicio. |
| RN-05 | Solo se permiten reservas de lunes a viernes. |
| RN-06 | El horario de atención inicia a las 08:00. |
| RN-07 | La reserva debe finalizar máximo a las 17:00. |
| RN-08 | No pueden existir dos reservas para la misma fecha y hora. |
| RN-09 | Toda reserva creada correctamente debe quedar con estado `confirmed`. |
| RN-10 | Toda reserva válida debe recibir un código de confirmación generado por una dependencia controlable desde las pruebas. |

La correspondencia detallada entre reglas y casos de prueba está en
[`MATRIZ_CASOS_PRUEBA.md`](./MATRIZ_CASOS_PRUEBA.md).

## Estructura principal del repositorio

```
reservation-testing-lab/
├── app/
│   ├── __init__.py
│   ├── exceptions.py          # Jerarquía de excepciones del dominio
│   ├── models.py               # Dataclass Reservation
│   ├── validators.py           # Un validador por regla de negocio
│   ├── repositories.py         # Repositorio de reservas en memoria
│   └── reservation_service.py  # Orquesta validadores + repositorio
├── tests/
│   ├── conftest.py             # Fixtures compartidas (fecha fija, datos válidos,
│   │                            #   repositorio, generador de código, servicio)
│   ├── test_validators.py      # Pruebas por regla de negocio (positivas,
│   │                            #   negativas y de frontera)
│   └── test_reservation_service.py  # Pruebas de la lógica coordinada del servicio
├── MATRIZ_CASOS_PRUEBA.md      # Matriz de trazabilidad regla → caso de prueba
├── .gitignore
├── pyproject.toml              # Configuración de Pytest (testpaths, addopts, etc.)
├── requirements-dev.txt
└── README.md
```

## Diseño y decisiones clave

- **Sin dependencias externas**: no se usa FastAPI, Uvicorn ni una base de
  datos real. `InMemoryReservationRepository` guarda las reservas en una
  lista interna por instancia (sin variables globales), y cada prueba recibe
  un repositorio nuevo mediante la fixture `repository`.
- **Fecha controlada por las pruebas**: `validate_reservation_date` recibe
  `current_date` como parámetro en lugar de usar `date.today()`, de modo que
  ninguna prueba depende del día real en que se ejecute la suite.
- **Código de confirmación inyectado**: `ReservationService` recibe un
  `confirmation_code_generator` (un *callable*) por constructor. En las
  pruebas se sustituye por una función determinista que siempre devuelve el
  mismo valor fijo, evitando aleatoriedad no controlada.
- **Excepciones específicas por regla**: todas heredan de `ReservationError`,
  lo que permite capturarlas de forma genérica más adelante (por ejemplo, en
  una futura API FastAPI) sin perder el detalle de cada caso.
- **Independencia de las pruebas**: no hay estado compartido entre pruebas;
  cada una recibe repositorio, servicio y datos nuevos por fixture. Esto se
  verificó ejecutando subconjuntos de la suite en distinto orden y varias
  veces consecutivas, con resultado estable.

## Próximo paso del curso

Esta capa de lógica de negocio, ya probada de forma aislada, es la base sobre
la que en el siguiente módulo se conectarán endpoints FastAPI con
`TestClient` para pruebas de integración de la API.
