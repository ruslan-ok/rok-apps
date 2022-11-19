const scripts = [
    'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.1/moment.min.js',
    'https://cdn.jsdelivr.net/npm/chart.js',
    'https://cdnjs.cloudflare.com/ajax/libs/chartjs-adapter-moment/1.0.0/chartjs-adapter-moment.min.js',
];

scripts.forEach(x => {
    let script = document.createElement('script');
    script.src = x;
    document.body.appendChild(script);
})

let dataEl = window.document.getElementById('chartData');
if (dataEl) {
    const data = dataEl.innerText;
    const jdata = JSON.parse(data);
    const ctx = document.getElementById('healthChart').getContext('2d');
    Chart.defaults.elements.point.radius = 0;
    new Chart(ctx, jdata);
}

function getChartData() {
    console.log('getChartData()');
}

function sayHello() {
    alert('hello');
}
