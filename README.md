# spanish-pvpc-holidays

Importable Python package for Spanish holidays that should count as all-day `P3/valle` in the PVPC 2.0TD tariff.

---

## Regulatory Context (Peaje 2.0 TD)

For the energy price component in 2.0 TD, a three-period time discrimination applies: `punta`, `llano` and `valle`.

For the power component (`potencia`) in 2.0 TD, only two periods apply: `punta-llano` and `valle`.

All hours on Saturdays, Sundays, 6 January, and national holidays are treated as period 3 (`valle`).

Reference: Circular 3/2020 (BOE reference: [BOE-A-2020-1066](https://www.boe.es/buscar/pdf/2020/BOE-A-2020-1066-consolidado.pdf)), Art. 7.3 and Art. 7.4.

Art. 7.3:

> "Se consideran como horas del periodo 3 (valle) todas las horas de los sábados,
> domingos, el 6 de enero y los días festivos de ámbito nacional, definidos como tales en el
> calendario oficial del año correspondiente, con exclusión tanto de los festivos sustituibles
> como de los que no tienen fecha fija."

Art. 7.4:

> "Discriminación horaria de dos periodos: La discriminación horaria de dos periodos
> será de aplicación al término de facturación de potencia y excesos de potencia de aplicación
> al peaje 2.0 TD. La discriminación horaria de dos periodos diferencia las horas del año en dos periodos
> horarios: punta-llano y valle. El periodo punta-llano de la discriminación horaria de dos
> periodos agrupa los periodos P1 (punta) y P2 (llano) de la discriminación horaria en tres
> periodos, mientras que el periodo valle de la discriminación horaria de dos periodos se
> corresponde con el periodo 3 de la discriminación horaria de tres periodos."

---

## Rules

1. Download CSV from Seguridad Social.
   - Source endpoint: `https://www.seg-social.es/wps/PA_POINCALAB/CalendarioServlet`
2. Optionally load national holidays from `python-holidays` (`holidays.country_holidays("ES", years=[...])`).
3. Normalize holiday names so CSV and `python-holidays` variants map to the same canonical names.
4. Exclude holidays that fall on Saturday/Sunday.
5. Exclude `Viernes Santo` (it does not have a fixed date, and Art. 7.3 excludes holidays without a fixed date).
6. Add fixed dates if they do not fall on a weekend:
   - `01.11` Todos los Santos
   - `06.12` Día de la Constitución
7. Add the first two fixed holidays for the next year if they do not fall on a weekend:
   - `01.01` Año Nuevo
   - `06.01` Epifanía del Señor
8. Log all steps, exclusion reasons, and the final list.

Name normalization examples:
- `Epifania del Señor` -> `Epifanía del Señor`
- `Fiesta del trabajo` -> `Fiesta del Trabajo`
- `Fiesta nacional de España` -> `Fiesta Nacional de España`
- `Día de la Constitución Española` -> `Día de la Constitución`

---

## Installation

### Option A (recommended): Poetry

Install dependencies and create/manage the virtual environment via Poetry:

```bash
poetry install
```

If you want to use `--source python-holidays`, install the optional extra:

```bash
poetry install -E holidays
```

Run the CLI:

```bash
poetry run pvpc-holidays --year 2026 --source csv --log-level DEBUG
```

Run the CLI with `python-holidays` as source:

```bash
poetry run pvpc-holidays --year 2026 --source python-holidays --log-level DEBUG
```

### Option B: `venv` + `pip` (editable install)

Create and activate a virtual environment, then install the package in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

If you want to use `--source python-holidays`, install the optional extra:

```bash
python -m pip install -e ".[holidays]"
```

Run the CLI:

```bash
pvpc-holidays --year 2026 --source csv --log-level DEBUG
```

Run the CLI with `python-holidays` as source:

```bash
pvpc-holidays --year 2026 --source python-holidays --log-level DEBUG
```

If the script is not found in your shell, use the module entry point:

```bash
python -m pvpc_holidays.cli --year 2026 --source csv --log-level DEBUG
```

---

## Usage in Python

Sync API:

```python
from pvpc_holidays import get_pvpc_holidays

holidays = get_pvpc_holidays(2026, source="csv")
for day, name in holidays.items():
    print(day, name)
```

The returned mapping includes selected holidays for the requested year plus
next-year `01.01` and `06.01` when those dates are not Saturday/Sunday.

Sync API with `python-holidays` as input source:

```python
from pvpc_holidays import get_pvpc_holidays

holidays = get_pvpc_holidays(2026, source="python-holidays")
for day, name in holidays.items():
    print(day, name)
```

Async-safe API (recommended for event-loop environments such as Home Assistant):

```python
from pvpc_holidays import async_get_pvpc_holidays

holidays = await async_get_pvpc_holidays(2026, source="python-holidays")
for day, name in holidays.items():
    print(day, name)
```

Home Assistant style usage (avoid first-use blocking on the event loop):

```python
from pvpc_holidays import async_get_pvpc_holidays, async_warmup_source

# optional: warm up once during setup to pre-load imports/metadata/datasets
await async_warmup_source(2026, source="python-holidays")

# regular fetch
holidays = await async_get_pvpc_holidays(2026, source="python-holidays")
```

Warmup helpers (useful to pre-load imports/metadata/data before first real fetch):

```python
from pvpc_holidays import warmup_source, async_warmup_source

# sync warmup
warmup_source(2026, source="python-holidays")

# async warmup
await async_warmup_source(2026, source="python-holidays")
```

---

## CLI

```bash
pvpc-holidays --year 2026 --source csv --log-level DEBUG
```

Optionally, `--csv-url` can include a `{year}` placeholder.
To use `python-holidays` as source, set `--source python-holidays`.

---

## Sample logs

CSV source (`--source csv`):

```text
INFO: Holiday source selected: csv | year=2026 | mode=full
DEBUG: Downloading holiday CSV: https://www.seg-social.es/wps/PA_POINCALAB/CalendarioServlet?exportacion=CSV&tipo=2
DEBUG: CSV downloaded (387 characters)
DEBUG: CSV holiday found: 2026-01-01 (Año Nuevo) | tipo=Nacional | province=- | locality=-
DEBUG: CSV holiday found: 2026-01-06 (Epifanía del Señor) | tipo=Nacional | province=- | locality=- | mapped_from=Epifania del Señor
DEBUG: CSV holiday found: 2026-04-03 (Viernes Santo) | tipo=Nacional | province=- | locality=-
DEBUG: CSV holiday found: 2026-05-01 (Fiesta del Trabajo) | tipo=Nacional | province=- | locality=- | mapped_from=Fiesta del trabajo
DEBUG: CSV holiday found: 2026-08-15 (Asunción de la Virgen) | tipo=Nacional | province=- | locality=-
DEBUG: CSV holiday found: 2026-10-12 (Fiesta Nacional de España) | tipo=Nacional | province=- | locality=- | mapped_from=Fiesta nacional de España
DEBUG: CSV holiday found: 2026-12-08 (Inmaculada Concepción) | tipo=Nacional | province=- | locality=-
DEBUG: CSV holiday found: 2026-12-25 (Natividad del Señor) | tipo=Nacional | province=- | locality=-
DEBUG: Loaded 8 records from source=csv for year=2026 | mode=full
DEBUG: INCLUDE 2026-01-01 (Año Nuevo)
DEBUG: INCLUDE 2026-01-06 (Epifanía del Señor)
DEBUG: EXCLUDE 2026-04-03 (Viernes Santo): Viernes Santo explicitly excluded (not a fixed date)
DEBUG: INCLUDE 2026-05-01 (Fiesta del Trabajo)
DEBUG: EXCLUDE 2026-08-15 (Asunción de la Virgen): weekend (SAT)
DEBUG: INCLUDE 2026-10-12 (Fiesta Nacional de España)
DEBUG: INCLUDE 2026-12-08 (Inmaculada Concepción)
DEBUG: INCLUDE 2026-12-25 (Natividad del Señor)
DEBUG: EXCLUDE 2026-11-01 (Todos los Santos): fixed date falls on weekend (SUN)
DEBUG: EXCLUDE 2026-12-06 (Día de la Constitución): fixed date falls on weekend (SUN)
DEBUG: INCLUDE 2027-01-01 (Año Nuevo): next-year fixed date added
DEBUG: INCLUDE 2027-01-06 (Epifanía del Señor): next-year fixed date added
DEBUG: Final PVPC holiday list for 2026/2027 (8 entries):
DEBUG:   2026-01-01 - Año Nuevo
DEBUG:   2026-01-06 - Epifanía del Señor
DEBUG:   2026-05-01 - Fiesta del Trabajo
DEBUG:   2026-10-12 - Fiesta Nacional de España
DEBUG:   2026-12-08 - Inmaculada Concepción
DEBUG:   2026-12-25 - Natividad del Señor
DEBUG:   2027-01-01 - Año Nuevo
DEBUG:   2027-01-06 - Epifanía del Señor
INFO: Computed PVPC holidays for 2026/2027 from source=csv | warmup=False | final_count=8
PVPC P3/valle holidays 2026/2027 (8 entries):
2026-01-01 - Año Nuevo
2026-01-06 - Epifanía del Señor
2026-05-01 - Fiesta del Trabajo
2026-10-12 - Fiesta Nacional de España
2026-12-08 - Inmaculada Concepción
2026-12-25 - Natividad del Señor
2027-01-01 - Año Nuevo
2027-01-06 - Epifanía del Señor
```

python-holidays source (`--source python-holidays`):

```text
INFO: Holiday source selected: python-holidays | year=2026 | mode=full
DEBUG: python-holidays holiday found: 2026-01-01 (Año Nuevo)
DEBUG: python-holidays holiday found: 2026-01-06 (Epifanía del Señor)
DEBUG: python-holidays holiday found: 2026-04-03 (Viernes Santo)
DEBUG: python-holidays holiday found: 2026-05-01 (Fiesta del Trabajo)
DEBUG: python-holidays holiday found: 2026-08-15 (Asunción de la Virgen)
DEBUG: python-holidays holiday found: 2026-10-12 (Fiesta Nacional de España)
DEBUG: python-holidays holiday found: 2026-11-01 (Todos los Santos)
DEBUG: python-holidays holiday found: 2026-12-06 (Día de la Constitución) | mapped_from=Día de la Constitución Española
DEBUG: python-holidays holiday found: 2026-12-08 (Inmaculada Concepción)
DEBUG: python-holidays holiday found: 2026-12-25 (Natividad del Señor)
DEBUG: Loaded 10 records from source=python-holidays for year=2026 | mode=full
DEBUG: INCLUDE 2026-01-01 (Año Nuevo)
DEBUG: INCLUDE 2026-01-06 (Epifanía del Señor)
DEBUG: EXCLUDE 2026-04-03 (Viernes Santo): Viernes Santo explicitly excluded (not a fixed date)
DEBUG: INCLUDE 2026-05-01 (Fiesta del Trabajo)
DEBUG: EXCLUDE 2026-08-15 (Asunción de la Virgen): weekend (SAT)
DEBUG: INCLUDE 2026-10-12 (Fiesta Nacional de España)
DEBUG: INCLUDE 2026-12-08 (Inmaculada Concepción)
DEBUG: INCLUDE 2026-12-25 (Natividad del Señor)
DEBUG: EXCLUDE 2026-11-01 (Todos los Santos): fixed date falls on weekend (SUN)
DEBUG: EXCLUDE 2026-12-06 (Día de la Constitución): fixed date falls on weekend (SUN)
DEBUG: INCLUDE 2027-01-01 (Año Nuevo): next-year fixed date added
DEBUG: INCLUDE 2027-01-06 (Epifanía del Señor): next-year fixed date added
DEBUG: Final PVPC holiday list for 2026/2027 (8 entries):
DEBUG:   2026-01-01 - Año Nuevo
DEBUG:   2026-01-06 - Epifanía del Señor
DEBUG:   2026-05-01 - Fiesta del Trabajo
DEBUG:   2026-10-12 - Fiesta Nacional de España
DEBUG:   2026-12-08 - Inmaculada Concepción
DEBUG:   2026-12-25 - Natividad del Señor
DEBUG:   2027-01-01 - Año Nuevo
DEBUG:   2027-01-06 - Epifanía del Señor
INFO: Computed PVPC holidays for 2026/2027 from source=python-holidays | warmup=False | final_count=8
PVPC P3/valle holidays 2026/2027 (8 entries):
2026-01-01 - Año Nuevo
2026-01-06 - Epifanía del Señor
2026-05-01 - Fiesta del Trabajo
2026-10-12 - Fiesta Nacional de España
2026-12-08 - Inmaculada Concepción
2026-12-25 - Natividad del Señor
2027-01-01 - Año Nuevo
2027-01-06 - Epifanía del Señor
```

---

## License

MIT License. See the [LICENSE](LICENSE) file.
