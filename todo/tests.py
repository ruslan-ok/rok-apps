from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Task, NONE, DAILY, WEEKLY, MONTHLY, ANNUALLY
from .utils import get_term_for_two_dates, \
                   LONG_TIME, LAST_MONTH, THREE_WEEKS, TWO_WEEKS, LAST_WEEK, MON, TUE, WED, THU, FRI, SAT, SUN, YESTERDAY, \
                   TODAY, TOMORROW, THIS_WEEK, NEXT_WEEK, THIS_MONTH, NEXT_MONTH, MUCH_LATER

class NextIterationTests(TestCase):

    def do_test_next_iteration(self, repeat, start, last_compl, expected):
        self.task.repeat = repeat
        self.task.start = start
        self.task.last_compl = last_compl
        self.task.save()
        ni = self.task.next_iteration()
        days = (ni - date.today()).days
        self.assertEqual(days, expected)
    
    def do_test_next_iteration_date(self, repeat, start, last_compl, expect):
        self.task.repeat = repeat
        self.task.start = start
        self.task.last_compl = last_compl
        self.task.save()
        ni = self.task.next_iteration()
        self.assertEqual(ni, expect)
    
    def test_next_iteration(self):
        self.user = User.objects.create(username = 'tests.py')
        self.task = Task.objects.create(user = self.user, name = 'tests.py')

        # Если дата начала не определена, то независимо от режима повторений считаем, что срок задачи - сегодня
        self.do_test_next_iteration(NONE, None, None, 0)
        self.do_test_next_iteration(DAILY, None, None, 0)
        self.do_test_next_iteration(WEEKLY, None, None, 0)
        self.do_test_next_iteration(MONTHLY, None, None, 0)
        self.do_test_next_iteration(ANNUALLY, None, None, 0)

        # Первая итерация, независимо от режима повторений, ожидается в указанную день start
        today = date.today()
        self.do_test_next_iteration(NONE, today, None, 0)
        self.do_test_next_iteration(NONE, (today - timedelta(12)), None, -12)
        self.do_test_next_iteration(NONE, (today + timedelta(12)), None, 12)
        self.do_test_next_iteration(DAILY, (today - timedelta(12)), None, -12)
        self.do_test_next_iteration(DAILY, (today + timedelta(12)), None, 12)
        self.do_test_next_iteration(WEEKLY, (today - timedelta(12)), None, -12)
        self.do_test_next_iteration(WEEKLY, (today + timedelta(12)), None, 12)
        self.do_test_next_iteration(MONTHLY, (today - timedelta(12)), None, -12)
        self.do_test_next_iteration(MONTHLY, (today + timedelta(12)), None, 12)
        self.do_test_next_iteration(ANNUALLY, (today - timedelta(12)), None, -12)
        self.do_test_next_iteration(ANNUALLY, (today + timedelta(12)), None, 12)

        # Не первая итерация для повторяющихся задач
        # Ежедневно
        self.do_test_next_iteration(DAILY, (today - timedelta(12)), (today - timedelta(2)), -1)
        self.do_test_next_iteration(DAILY, (today - timedelta(12)), (today - timedelta(1)), 0)
        self.do_test_next_iteration(DAILY, (today - timedelta(12)), today, 1)
        self.do_test_next_iteration(DAILY, (today - timedelta(12)), (today + timedelta(1)), 2)
        
        # Еженедельно
        self.do_test_next_iteration(WEEKLY, (today - timedelta(12)), (today - timedelta(10)), -3)
        self.do_test_next_iteration(WEEKLY, (today - timedelta(12)), (today - timedelta(1)), 6)
        self.do_test_next_iteration(WEEKLY, (today - timedelta(12)), today, 7)

        # Ежемесячно
        self.do_test_next_iteration(MONTHLY, None, None, 0)

        # Ещё не началось
        beg    = date(2020, 7, 18)
        last   = None
        expect = date(2020, 7, 18)
        self.do_test_next_iteration_date(MONTHLY, beg, last, expect)
        
        # Должно было начаться в прошлом
        beg    = date(2020, 3, 18)
        last   = None
        expect = date(2020, 3, 18)
        self.do_test_next_iteration_date(MONTHLY, beg, last, expect)

        # Есть последняя итерация
        beg    = date(2020, 3, 25)
        last   = date(2020, 4, 25)
        expect = date(2020, 5, 25)
        self.do_test_next_iteration_date(MONTHLY, beg, last, expect)

        # Если день последней итерации отличается не более чем на 5 дней от дня начала повторений, то пытаемся вернуться к дню начала повторений
        beg    = date(2020, 3, 25)
        expect = date(2020, 5, 25)

        last   = date(2020, 4, 22)
        self.do_test_next_iteration_date(MONTHLY, beg, last, expect)
        last   = date(2020, 4, 22)
        self.do_test_next_iteration_date(MONTHLY, beg, last, expect)
        last   = date(2020, 4, 22)
        self.do_test_next_iteration_date(MONTHLY, beg, last, expect)
        last   = date(2020, 4, 22)
        self.do_test_next_iteration_date(MONTHLY, beg, last, expect)
        last   = date(2020, 4, 23)
        self.do_test_next_iteration_date(MONTHLY, beg, last, expect)
        last   = date(2020, 4, 24)
        self.do_test_next_iteration_date(MONTHLY, beg, last, expect)
        last   = date(2020, 4, 25)
        self.do_test_next_iteration_date(MONTHLY, beg, last, expect)
        last   = date(2020, 4, 26)
        self.do_test_next_iteration_date(MONTHLY, beg, last, expect)
        last   = date(2020, 4, 27)
        self.do_test_next_iteration_date(MONTHLY, beg, last, expect)
        last   = date(2020, 4, 28)
        self.do_test_next_iteration_date(MONTHLY, beg, last, expect)
        last   = date(2020, 4, 29)
        self.do_test_next_iteration_date(MONTHLY, beg, last, expect)

        beg    = date(2020, 3, 31)
        last   = date(2020, 4, 30)
        expect = date(2020, 5, 31)
        self.do_test_next_iteration_date(MONTHLY, beg, last, expect)

        beg    = date(2020, 4, 30)
        last   = date(2020, 5, 31)
        expect = date(2020, 6, 30)
        self.do_test_next_iteration_date(MONTHLY, beg, last, expect)

        beg    = date(2020, 1, 31)
        last   = date(2020, 1, 31)
        expect = date(2020, 2, 29)
        self.do_test_next_iteration_date(MONTHLY, beg, last, expect)

        beg    = date(2021, 1, 31)
        last   = date(2021, 1, 31)
        expect = date(2021, 2, 28)
        self.do_test_next_iteration_date(MONTHLY, beg, last, expect)

        beg    = date(2021, 1, 31)
        last   = date(2021, 12, 31)
        expect = date(2022, 1, 31)
        self.do_test_next_iteration_date(MONTHLY, beg, last, expect)

        self.task.delete()
        self.user.delete()

class TermCalculationTests(TestCase):
    
    def test_all_values(self):
        today = date(2020, 5, 1)
        self.assertIs(get_term_for_two_dates(today, date(2021, 1, 1)), MUCH_LATER)
        self.assertIs(get_term_for_two_dates(today, date(2020, 7, 1)), MUCH_LATER)
        self.assertIs(get_term_for_two_dates(today, date(2020, 6, 30)), NEXT_MONTH)
        self.assertIs(get_term_for_two_dates(today, date(2020, 6, 1)), NEXT_MONTH)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 31)), THIS_MONTH)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 11)), THIS_MONTH)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 10)), NEXT_WEEK)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 4)), NEXT_WEEK)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 3)), THIS_WEEK)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 2)), TOMORROW)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 1)), TODAY)
        today = date(2020, 5, 18)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 31)), NEXT_WEEK)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 25)), NEXT_WEEK)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 24)), THIS_WEEK)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 20)), THIS_WEEK)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 19)), TOMORROW)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 18)), TODAY)
        today = date(2020, 5, 17)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 18)), TOMORROW)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 17)), TODAY)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 16)), YESTERDAY)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 15)), FRI)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 14)), THU)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 13)), WED)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 12)), TUE)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 11)), MON)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 10)), LAST_WEEK)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 9)), LAST_WEEK)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 8)), LAST_WEEK)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 7)), LAST_WEEK)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 6)), LAST_WEEK)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 5)), LAST_WEEK)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 4)), LAST_WEEK)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 3)), TWO_WEEKS)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 2)), TWO_WEEKS)
        self.assertIs(get_term_for_two_dates(today, date(2020, 5, 1)), TWO_WEEKS)
        self.assertIs(get_term_for_two_dates(today, date(2020, 4, 30)), LAST_MONTH)
        self.assertIs(get_term_for_two_dates(today, date(2020, 4, 29)), LAST_MONTH)
        self.assertIs(get_term_for_two_dates(today, date(2020, 4, 2)), LAST_MONTH)
        self.assertIs(get_term_for_two_dates(today, date(2020, 4, 1)), LAST_MONTH)
        self.assertIs(get_term_for_two_dates(today, date(2020, 3, 31)), LONG_TIME)
        self.assertIs(get_term_for_two_dates(today, date(2019, 1, 1)), LONG_TIME)
