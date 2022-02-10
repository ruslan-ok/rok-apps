afterCalendarChanged(1, 1);
afterCalendarChanged(1, 2);
afterCalendarChanged(1, 3);

function afterCalendarChanged(init, field)
{
  if ((field == 1) || (field == 0))
    getRateOnDate('USD', init, "id_AvansDate",   "id_AvansRate");
  if ((field == 2) || (field == 0))
    getRateOnDate('USD', init, "id_PaymentDate", "id_PaymentRate");
  if ((field == 3) || (field == 0))
    getRateOnDate('USD', init, "id_Part2Date",   "id_Part2Rate");
}

