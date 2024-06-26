afterCalendarChanged(1, 1);

function afterCalendarChanged(init, field, django_host_api) {
    getRateOnDate(init, 'id_event', 'id_price_unit', 'id_expen_rate_usd', django_host_api);
}
