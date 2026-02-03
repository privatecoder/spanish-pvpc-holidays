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
7. Log all steps, exclusion reasons, and the final list.

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
poetry run pvpc-holidays --year 2026 --source csv --log-level INFO
```

Run the CLI with `python-holidays` as source:

```bash
poetry run pvpc-holidays --year 2026 --source python-holidays --log-level INFO
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
pvpc-holidays --year 2026 --source csv --log-level INFO
```

Run the CLI with `python-holidays` as source:

```bash
pvpc-holidays --year 2026 --source python-holidays --log-level INFO
```

If the script is not found in your shell, use the module entry point:

```bash
python -m pvpc_holidays.cli --year 2026 --source csv --log-level INFO
```

---

## Usage in Python

```python
from pvpc_holidays import get_pvpc_holidays

holidays = get_pvpc_holidays(2026, source="csv")
for day, name in holidays.items():
    print(day, name)
```

Using `python-holidays` as input source:

```python
from pvpc_holidays import get_pvpc_holidays

holidays = get_pvpc_holidays(2026, source="python-holidays")
for day, name in holidays.items():
    print(day, name)
```

---

## CLI

```bash
pvpc-holidays --year 2026 --source csv --log-level INFO
```

Optionally, `--csv-url` can include a `{year}` placeholder.
To use `python-holidays` as source, set `--source python-holidays`.

---

## Sample logs

CSV source (`--source csv`):

```text
INFO: Holiday source selected: csv
INFO: Downloading holiday CSV: https://www.seg-social.es/wps/PA_POINCALAB/CalendarioServlet?exportacion=CSV&tipo=2
INFO: CSV downloaded (387 characters)
INFO: CSV holiday found: 2026-01-01 (Año Nuevo) | tipo=Nacional | province=- | locality=-
INFO: CSV holiday found: 2026-01-06 (Epifanía del Señor) | tipo=Nacional | province=- | locality=- | mapped_from=Epifania del Señor
INFO: CSV holiday found: 2026-04-03 (Viernes Santo) | tipo=Nacional | province=- | locality=-
INFO: CSV holiday found: 2026-05-01 (Fiesta del Trabajo) | tipo=Nacional | province=- | locality=- | mapped_from=Fiesta del trabajo
INFO: CSV holiday found: 2026-08-15 (Asunción de la Virgen) | tipo=Nacional | province=- | locality=-
INFO: CSV holiday found: 2026-10-12 (Fiesta Nacional de España) | tipo=Nacional | province=- | locality=- | mapped_from=Fiesta nacional de España
INFO: CSV holiday found: 2026-12-08 (Inmaculada Concepción) | tipo=Nacional | province=- | locality=-
INFO: CSV holiday found: 2026-12-25 (Natividad del Señor) | tipo=Nacional | province=- | locality=-
INFO: INCLUDE 2026-01-01 (Año Nuevo)
INFO: INCLUDE 2026-01-06 (Epifanía del Señor)
INFO: EXCLUDE 2026-04-03 (Viernes Santo): Viernes Santo explicitly excluded (not a fixed date)
INFO: INCLUDE 2026-05-01 (Fiesta del Trabajo)
INFO: EXCLUDE 2026-08-15 (Asunción de la Virgen): weekend (SAT)
INFO: INCLUDE 2026-10-12 (Fiesta Nacional de España)
INFO: INCLUDE 2026-12-08 (Inmaculada Concepción)
INFO: INCLUDE 2026-12-25 (Natividad del Señor)
INFO: EXCLUDE 2026-11-01 (Todos los Santos): fixed date falls on weekend (SUN)
INFO: EXCLUDE 2026-12-06 (Día de la Constitución): fixed date falls on weekend (SUN)
INFO: Final PVPC holiday list (6 entries):
INFO:   2026-01-01 - Año Nuevo
INFO:   2026-01-06 - Epifanía del Señor
INFO:   2026-05-01 - Fiesta del Trabajo
INFO:   2026-10-12 - Fiesta Nacional de España
INFO:   2026-12-08 - Inmaculada Concepción
INFO:   2026-12-25 - Natividad del Señor
PVPC P3/valle holidays 2026 (6 entries):
2026-01-01 - Año Nuevo
2026-01-06 - Epifanía del Señor
2026-05-01 - Fiesta del Trabajo
2026-10-12 - Fiesta Nacional de España
2026-12-08 - Inmaculada Concepción
2026-12-25 - Natividad del Señor
```

python-holidays source (`--source python-holidays`):

```text
INFO: Holiday source selected: python-holidays
INFO: python-holidays holiday found: 2026-01-01 (Año Nuevo)
INFO: python-holidays holiday found: 2026-01-06 (Epifanía del Señor)
INFO: python-holidays holiday found: 2026-04-03 (Viernes Santo)
INFO: python-holidays holiday found: 2026-05-01 (Fiesta del Trabajo)
INFO: python-holidays holiday found: 2026-08-15 (Asunción de la Virgen)
INFO: python-holidays holiday found: 2026-10-12 (Fiesta Nacional de España)
INFO: python-holidays holiday found: 2026-12-08 (Inmaculada Concepción)
INFO: python-holidays holiday found: 2026-12-25 (Natividad del Señor)
INFO: INCLUDE 2026-01-01 (Año Nuevo)
INFO: INCLUDE 2026-01-06 (Epifanía del Señor)
INFO: EXCLUDE 2026-04-03 (Viernes Santo): Viernes Santo explicitly excluded (not a fixed date)
INFO: INCLUDE 2026-05-01 (Fiesta del Trabajo)
INFO: EXCLUDE 2026-08-15 (Asunción de la Virgen): weekend (SAT)
INFO: INCLUDE 2026-10-12 (Fiesta Nacional de España)
INFO: INCLUDE 2026-12-08 (Inmaculada Concepción)
INFO: INCLUDE 2026-12-25 (Natividad del Señor)
INFO: EXCLUDE 2026-11-01 (Todos los Santos): fixed date falls on weekend (SUN)
INFO: EXCLUDE 2026-12-06 (Día de la Constitución): fixed date falls on weekend (SUN)
INFO: Final PVPC holiday list (6 entries):
INFO:   2026-01-01 - Año Nuevo
INFO:   2026-01-06 - Epifanía del Señor
INFO:   2026-05-01 - Fiesta del Trabajo
INFO:   2026-10-12 - Fiesta Nacional de España
INFO:   2026-12-08 - Inmaculada Concepción
INFO:   2026-12-25 - Natividad del Señor
PVPC P3/valle holidays 2026 (6 entries):
2026-01-01 - Año Nuevo
2026-01-06 - Epifanía del Señor
2026-05-01 - Fiesta del Trabajo
2026-10-12 - Fiesta Nacional de España
2026-12-08 - Inmaculada Concepción
2026-12-25 - Natividad del Señor
```

---

## License

MIT License. See the [LICENSE](LICENSE) file.
