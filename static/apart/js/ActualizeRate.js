AfterCalendarChanged(1, 1);

function AfterCalendarChanged(init, field) {
  GetRateOnDate('USD', init, "id_payment_0", "id_rate");
}

