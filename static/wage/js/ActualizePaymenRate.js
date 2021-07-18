AfterCalendarChanged(1, 1);

function AfterCalendarChanged(init, field)
{
  GetRateOnDate('USD', init, "id_payed", "id_rate");
}

