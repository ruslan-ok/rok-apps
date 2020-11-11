AfterCalendarChanged(1, 1);

function AfterCalendarChanged(init, field)
{
  GetRateOnDate(145, init, "id_date", "id_rate");
  GetRateOnDate(292, init, "id_date", "id_rate_2");
}

