from datetime import datetime
from django.test import TestCase
from django.utils.translation import activate
from django.contrib.auth.models import User
from .models import Car, Fuel, Part, Repl

class TestOverdue(TestCase):
    
    def check_case(self, limit_km, fuel_odo, repl_odo, limit_mo, fuel_date, repl_date, expected_en, expected_ru, expected_color, debug=False):
        self.fuel.odometr = fuel_odo
        self.fuel.pub_date = datetime.strptime(fuel_date, '%d.%m.%Y')
        self.fuel.save()
        self.part.chg_km = limit_km
        self.part.chg_mo = limit_mo
        self.part.save()
        self.repl.odometr = repl_odo
        self.repl.dt_chg = datetime.strptime(repl_date, '%d.%m.%Y')
        self.repl.save()
        activate('en')
        info, color = self.part.get_rest(debug)
        self.assertEqual(self.part.info(), expected_en)
        activate('ru')
        self.assertEqual(self.part.info(), expected_ru)
        self.assertEqual(color, expected_color)
        
    def test_overdue_cases(self):
        self.user = User.objects.create(username = 'tests.py')
        self.car = Car.objects.create(user = self.user, name = 'tests.py')
        self.fuel = Fuel.objects.create(car = self.car, pub_date = datetime(2021, 3, 15), odometr = 100000, volume = 50, price = 1.83)
        self.part = Part.objects.create(car = self.car, name = 'tests.py', chg_km = 100, chg_mo = 12)
        self.repl = Repl.objects.create(car = self.car, part = self.part, dt_chg = datetime(2020, 2, 7), odometr = 138000)

        # Checking duration designation options
        self.check_case(None, 100000, 100000, 1, '15.3.2021', '15.3.2021', '1 month / 1 month', '1 месяц / 1 месяц', 'warning')
        self.check_case(None, 100000, 100000, 2, '15.3.2021', '15.3.2021', '2 months / 2 months', '2 месяца / 2 месяца', 'normal')
        self.check_case(None, 100000, 100000, 4, '15.3.2021', '15.3.2021', '4 months / 4 months', '4 месяца / 4 месяца', 'normal')
        self.check_case(None, 100000, 100000, 5, '15.3.2021', '15.3.2021', '5 months / 5 months', '5 месяцев / 5 месяцев', 'normal')
        self.check_case(None, 100000, 100000, 10, '15.3.2021', '15.3.2021', '10 months / 10 months', '10 месяцев / 10 месяцев', 'normal')
        self.check_case(None, 100000, 100000, 11, '15.3.2021', '15.3.2021', '11 months / 11 months', '11 месяцев / 11 месяцев', 'normal')
        self.check_case(None, 100000, 100000, 12, '15.3.2021', '15.3.2021', '12 months / 1 year', '12 месяцев / 1 год', 'normal')
        self.check_case(None, 100000, 100000, 13, '15.3.2021', '15.3.2021', '13 months / 1 year and 1 month', '13 месяцев / 1 год и 1 месяц', 'normal')
        self.check_case(None, 100000, 100000, 14, '15.3.2021', '15.3.2021', '14 months / 1 year and 2 months', '14 месяцев / 1 год и 2 месяца', 'normal')
        self.check_case(None, 100000, 100000, 16, '15.3.2021', '15.3.2021', '16 months / 1 year and 4 months', '16 месяцев / 1 год и 4 месяца', 'normal')
        self.check_case(None, 100000, 100000, 17, '15.3.2021', '15.3.2021', '17 months / 1 year and 5 months', '17 месяцев / 1 год и 5 месяцев', 'normal')
        self.check_case(None, 100000, 100000, 22, '15.3.2021', '15.3.2021', '22 months / 1 year and 10 months', '22 месяца / 1 год и 10 месяцев', 'normal')
        self.check_case(None, 100000, 100000, 23, '15.3.2021', '15.3.2021', '23 months / 1 year and 11 months', '23 месяца / 1 год и 11 месяцев', 'normal')
        self.check_case(None, 100000, 100000, 24, '15.3.2021', '15.3.2021', '24 months / 2 years', '24 месяца / 2 года', 'normal')
        self.check_case(None, 100000, 100000, 25, '15.3.2021', '15.3.2021', '25 months / 2 years and 1 month', '25 месяцев / 2 года и 1 месяц', 'normal')
        self.check_case(None, 100000, 100000, 66, '15.3.2021', '15.3.2021', '66 months / 5 years and 6 months', '66 месяцев / 5 лет и 6 месяцев', 'normal')
        
        # checking the remaining duration
        self.check_case(None, 100000, 100000, 12, '14.3.2021', '15.3.2020', '12 months / 1 day', '12 месяцев / 1 день', 'warning')
        self.check_case(None, 100000, 100000, 12, '15.3.2021', '15.3.2020', '12 months / 0 days', '12 месяцев / 0 дней', 'warning')
        self.check_case(None, 100000, 100000, 12, '16.3.2021', '15.3.2020', '12 months / 1 day overdue', '12 месяцев / 1 день просрочено', 'error')
        self.check_case(None, 100000, 100000, 12, '20.3.2021', '15.3.2020', '12 months / 5 days overdue', '12 месяцев / 5 дней просрочено', 'error')
        self.check_case(None, 100000, 100000, 12, '20.5.2021', '15.3.2020', '12 months / 2 months overdue', '12 месяцев / 2 месяца просрочено', 'error')

        # Checking mileage designation options
        self.check_case(500, 110000, 110000, None, '15.3.2021', '15.3.2021', '500 km / 500 km', '500 км / 500 км', 'warning')
        self.check_case(10000, 110000, 110000, None, '15.3.2021', '15.3.2021', '10 thsd km / 10 thsd km', '10 тыс. км / 10 тыс. км', 'normal')
        self.check_case(300000, 110000, 110000, None, '15.3.2021', '15.3.2021', '300 thsd km / 300 thsd km', '300 тыс. км / 300 тыс. км', 'normal')

        # checking the remaining mileage
        self.check_case(10000, 110000, 100000, None, '15.3.2021', '15.3.2021', '10 thsd km / 0 km', '10 тыс. км / 0 км', 'warning')

        self.check_case(10000, 109000, 100000, None, '15.3.2021', '15.3.2021', '10 thsd km / 1 thsd km', '10 тыс. км / 1 тыс. км', 'normal')
        self.check_case(10000, 109001, 100000, None, '15.3.2021', '15.3.2021', '10 thsd km / 999 km', '10 тыс. км / 999 км', 'warning')
        self.check_case(10000, 109999, 100000, None, '15.3.2021', '15.3.2021', '10 thsd km / 1 km', '10 тыс. км / 1 км', 'warning')
        self.check_case(10000, 110001, 100000, None, '15.3.2021', '15.3.2021', '10 thsd km / 1 km overdue', '10 тыс. км / 1 км просрочено', 'error')
        self.check_case(10000, 110500, 100000, None, '15.3.2021', '15.3.2021', '10 thsd km / 500 km overdue', '10 тыс. км / 500 км просрочено', 'error')
        self.check_case(10000, 110999, 100000, None, '15.3.2021', '15.3.2021', '10 thsd km / 999 km overdue', '10 тыс. км / 999 км просрочено', 'error')
        self.check_case(10000, 111000, 100000, None, '15.3.2021', '15.3.2021', '10 thsd km / 1 thsd km overdue', '10 тыс. км / 1 тыс. км просрочено', 'error')
