afterCalendarChanged(1, 1);

function afterCalendarChanged(init, field) {
    getRateOnDate('USD', init, 'id_event', 'id_expen_rate');
    getRateOnDate('EUR', init, 'id_event', 'id_expen_rate_2');
}
