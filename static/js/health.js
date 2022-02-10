function buildChart(data) {
    let jdata = JSON.parse(data);
    const ctx = document.getElementById('healthChart').getContext('2d');
    new Chart(ctx, jdata);
}

