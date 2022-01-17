function getRateOnDate(currency, init, id_date, id_rate) {
  var el_rate = document.getElementById(id_rate);

  if (!el_rate)
    return;

  if (init == 1) {
    var old_rate = el_rate.value;
    if ((old_rate != "") && (old_rate != "0.0000"))
      return;
  }
  
  const request = new XMLHttpRequest();
  const url = "https://www.nbrb.by/api/exrates/rates/" + currency;
  
  var el_date = document.getElementById(id_date);
  if (!el_date)
    return;

  var dt = el_date.value;
  if (dt == "")
    return;
  var z1 = new Date(dt);
  const params = "?ondate=" + z1.toISOString().split('T')[0] + '&parammode=2';
  request.responseType = "json";
  request.open("GET", url + params, true);
  request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  request.addEventListener("readystatechange", () => {
    if (request.readyState === 4 && request.status === 200) {
      let obj = request.response;
      console.log(obj);       
      // Здесь мы можем обращаться к свойству объекта и получать его значение
      var rate = obj.Cur_OfficialRate;
      console.log(rate);
      el_rate.value = rate;
    }
  });
 
  request.send();
}
