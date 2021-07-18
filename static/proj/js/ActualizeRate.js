AfterCalendarChanged(1, 1);

function AfterCalendarChanged(init, field)
{
  GetRateOnDate('USD', init, "id_date", "id_rate");
  GetRateOnDate('EUR', init, "id_date", "id_rate_2");
}

