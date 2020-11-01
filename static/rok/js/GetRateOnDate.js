function GetRateOnDate(currency, init, id_date, id_rate)
{
  if (init == 1)
  {
    var old_rate = document.getElementById(id_rate).value;
    if ((old_rate != "") && (old_rate != "0.0000"))
      return;
  }
  const request = new XMLHttpRequest();
  const url = "https://www.nbrb.by/api/exrates/rates/" + currency;
  var dt = document.getElementById(id_date).value;
  if (dt == "")
    return;
  const params = "?ondate=" + dt.substring(6, 10) + "-" + dt.substring(3, 5) + "-" + dt.substring(0, 2);
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
        document.getElementById(id_rate).value = rate;
	}
  });
 
  request.send();
}
