document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('lineChart').getContext('2d');
    const lineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({length: 31}, (_, i) => i + 1),
            datasets: [
                {
                    label: 'Temperature',
                    data: [300, 200, 150, 300, 450, 250, 200, 300, 350, 400, 450, 200, 300, 250, 350, 400, 450, 300, 200, 150, 300, 450, 250, 200, 300, 350, 400, 450, 200, 300, 250],
                    borderColor: 'rgba(255, 206, 86, 1)',
                    fill: false,
                },
                {
                    label: 'Humidity',
                    data: [150, 250, 350, 450, 200, 300, 250, 350, 400, 450, 300, 200, 150, 300, 450, 250, 200, 300, 350, 400, 450, 200, 300, 250, 350, 400, 450, 300, 200, 150, 300],
                    borderColor: 'rgba(75, 192, 192, 1)',
                    fill: false,
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Day of the Month'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Value'
                    }
                }
            }
        }
    });
});
