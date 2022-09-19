afterCalendarChanged(1, 1);

function afterCalendarChanged(init, field) {
    getRateOnDate('USD', init, 'id_event', 'id_expen_rate_usd');
    getRateOnDate('EUR', init, 'id_event', 'id_expen_rate_eur');
    getRateOnDate('GBP', init, 'id_event', 'id_expen_rate_gbp');
}
