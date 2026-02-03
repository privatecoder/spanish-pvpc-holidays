from datetime import date
import unittest

from pvpc_holidays.core import PVPCError, load_holiday_records, parse_holiday_csv, select_pvpc_holidays


CSV_SAMPLE = """PROVINCIA,LOCALIDAD,FECHA,TIPO,DESCRIPCION
,,01-01-2024,Nacional,Año Nuevo
,,29-03-2024,Nacional,Viernes Santo
,,01-05-2024,Nacional,Fiesta del trabajo
,,12-10-2024,Nacional,Fiesta nacional de España
"""


class SelectRulesTest(unittest.TestCase):
    def test_select_rules_and_fixed_dates(self) -> None:
        records = parse_holiday_csv(CSV_SAMPLE)
        result = select_pvpc_holidays(records, year=2024)

        self.assertEqual(result[date(2024, 1, 1)], "Año Nuevo")
        self.assertEqual(result[date(2024, 5, 1)], "Fiesta del Trabajo")

        self.assertNotIn(date(2024, 3, 29), result)  # Viernes Santo
        self.assertNotIn(date(2024, 10, 12), result)  # Saturday

        self.assertEqual(result[date(2024, 11, 1)], "Todos los Santos")
        self.assertEqual(result[date(2024, 12, 6)], "Día de la Constitución")
        self.assertEqual(result[date(2025, 1, 1)], "Año Nuevo")
        self.assertEqual(result[date(2025, 1, 6)], "Epifanía del Señor")
        self.assertEqual(len(result), 6)

    def test_parse_maps_name_variants_to_canonical(self) -> None:
        csv_sample = """PROVINCIA,LOCALIDAD,FECHA,TIPO,DESCRIPCION
,,06-12-2026,Nacional,Día de la Constitución Española
,,06-01-2026,Nacional,Epifania del Señor
"""
        records = parse_holiday_csv(csv_sample)
        by_day = {record.day: record.description for record in records}
        self.assertEqual(by_day[date(2026, 12, 6)], "Día de la Constitución")
        self.assertEqual(by_day[date(2026, 1, 6)], "Epifanía del Señor")

    def test_invalid_source_raises_error(self) -> None:
        with self.assertRaises(PVPCError):
            load_holiday_records(2026, source="invalid-source")  # type: ignore[arg-type]

    def test_next_year_fixed_days_exclude_weekend(self) -> None:
        result = select_pvpc_holidays([], year=2021)
        self.assertNotIn(date(2022, 1, 1), result)  # Saturday
        self.assertEqual(result[date(2022, 1, 6)], "Epifanía del Señor")


if __name__ == "__main__":
    unittest.main()
