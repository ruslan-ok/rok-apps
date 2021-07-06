OperTest();

function OperTest()
{
  let sel = document.getElementById('id_oper');
  if (sel.value == 0)
  {
    document.getElementById("days_field").style.display = "block";
    document.getElementById("price_field").style.display = "block";
    document.getElementById("summa_field").style.display = "none";
  }
  else
  {
    document.getElementById("days_field").style.display = "none";
    document.getElementById("price_field").style.display = "none";
    document.getElementById("summa_field").style.display = "block";
  }
}
