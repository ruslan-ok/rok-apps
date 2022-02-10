afterCalendarChanged(1, 1);

function afterCalendarChanged(init, field)
{
  getRateOnDate('USD', init, "id_payed", "id_rate");
}

