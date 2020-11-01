AfterCalendarChanged(1, 1);
AfterCalendarChanged(1, 2);
AfterCalendarChanged(1, 3);

function AfterCalendarChanged(init, field)
{
  if ((field == 1) || (field == 0))
    GetRateOnDate(145, init, "id_AvansDate",   "id_AvansRate");
  if ((field == 2) || (field == 0))
    GetRateOnDate(145, init, "id_PaymentDate", "id_PaymentRate");
  if ((field == 3) || (field == 0))
    GetRateOnDate(145, init, "id_Part2Date",   "id_Part2Rate");
}

