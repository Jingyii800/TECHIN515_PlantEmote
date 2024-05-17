document.addEventListener('DOMContentLoaded', function() {
    const waterStatusTextElement = document.getElementById('waterStatusText');
    const waterCircleElement = document.getElementById('waterCircle');

    // Replace this with actual sensor data logic
    const isLackingWater = Math.random() < 0.5; // Randomly simulates water status for demonstration

    if (isLackingWater) {
        waterStatusTextElement.textContent = 'I am thirsty';
        waterStatusTextElement.style.color = 'red';
        waterCircleElement.style.backgroundColor = 'red';
    } else {
        waterStatusTextElement.textContent = 'I feel good';
        waterStatusTextElement.style.color = 'green';
        waterCircleElement.style.backgroundColor = 'green';
    }

    const ctx = document.getElementById('lineChart').getContext('2d');
    const lineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({length: 31}, (_, i) => i + 1),
            datasets: [
                {
                    label: 'Soil Moisture',
                    data: Array.from({length: 31}, () => Math.random() * 100), // Random data for demonstration
                    borderColor: 'rgba(75, 192, 192, 1)',
                    fill: false,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
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
                        text: 'Soil Moisture (%)'
                    },
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
});
