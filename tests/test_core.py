from datetime import date
import unittest
from unittest.mock import patch

from pvpc_holidays.core import (
    HolidayRecord,
    PVPCError,
    async_get_pvpc_holidays,
    async_load_holiday_records,
    async_warmup_source,
    get_pvpc_holidays,
    load_holiday_records,
    parse_holiday_csv,
    select_pvpc_holidays,
    warmup_source,
)


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


class AsyncAndWarmupTest(unittest.IsolatedAsyncioTestCase):
    async def test_async_get_matches_sync_for_csv_source(self) -> None:
        with patch("pvpc_holidays.core.download_holiday_csv", return_value=CSV_SAMPLE):
            sync_result = get_pvpc_holidays(2024, source="csv")
            async_result = await async_get_pvpc_holidays(2024, source="csv")
            self.assertEqual(sync_result, async_result)

    async def test_async_get_matches_sync_for_python_holidays_source(self) -> None:
        source_records = [
            HolidayRecord(date(2026, 1, 1), "Año Nuevo", "Nacional", "", ""),
            HolidayRecord(date(2026, 1, 6), "Epifanía del Señor", "Nacional", "", ""),
            HolidayRecord(date(2026, 4, 3), "Viernes Santo", "Nacional", "", ""),
            HolidayRecord(date(2026, 5, 1), "Fiesta del Trabajo", "Nacional", "", ""),
            HolidayRecord(date(2026, 8, 15), "Asunción de la Virgen", "Nacional", "", ""),
            HolidayRecord(date(2026, 10, 12), "Fiesta Nacional de España", "Nacional", "", ""),
            HolidayRecord(date(2026, 11, 1), "Todos los Santos", "Nacional", "", ""),
            HolidayRecord(date(2026, 12, 6), "Día de la Constitución", "Nacional", "", ""),
            HolidayRecord(date(2026, 12, 8), "Inmaculada Concepción", "Nacional", "", ""),
            HolidayRecord(date(2026, 12, 25), "Natividad del Señor", "Nacional", "", ""),
        ]
        with patch("pvpc_holidays.core.fetch_python_holidays", return_value=source_records):
            sync_result = get_pvpc_holidays(2026, source="python-holidays")
            async_result = await async_get_pvpc_holidays(2026, source="python-holidays")
            self.assertEqual(sync_result, async_result)

    async def test_async_load_holiday_records_matches_sync(self) -> None:
        source_records = [HolidayRecord(date(2026, 1, 1), "Año Nuevo", "Nacional", "", "")]
        with patch("pvpc_holidays.core.fetch_python_holidays", return_value=source_records):
            sync_records = load_holiday_records(2026, source="python-holidays")
            async_records = await async_load_holiday_records(2026, source="python-holidays")
            self.assertEqual(sync_records, async_records)

    async def test_warmup_helpers_are_repeatable(self) -> None:
        source_records = [
            HolidayRecord(date(2026, 1, 1), "Año Nuevo", "Nacional", "", ""),
            HolidayRecord(date(2026, 1, 6), "Epifanía del Señor", "Nacional", "", ""),
        ]
        with patch("pvpc_holidays.core.fetch_python_holidays", return_value=source_records):
            first = warmup_source(2026, source="python-holidays")
            second = warmup_source(2026, source="python-holidays")
            third = await async_warmup_source(2026, source="python-holidays")
            self.assertEqual(first, 2)
            self.assertEqual(second, first)
            self.assertEqual(third, first)


if __name__ == "__main__":
    unittest.main()
