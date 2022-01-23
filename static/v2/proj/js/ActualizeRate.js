afterCalendarChanged(1, 1);

function afterCalendarChanged(init, field)
{
  getRateOnDate('USD', init, "id_date", "id_rate");
  getRateOnDate('EUR', init, "id_date", "id_rate_2");
}

