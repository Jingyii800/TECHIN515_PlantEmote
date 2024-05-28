async function askQuestion(question) {
    try {
        const response = await fetch('/ask_question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: question })
        });
        const data = await response.json();
        document.getElementById('answer-box').textContent = data.answer;
    } catch (error) {
        document.getElementById('answer-box').textContent = 'Error occurred: ' + error;
    }
}

// document.addEventListener('DOMContentLoaded', function() {
//     fetch('/plant-data')
//         .then(response => response.json())
//         .then(data => {
//             if (data.length > 0) {
//                 const latestData = data[data.length - 1]; // Assuming the latest data is at the end of the array

//                 // Update soil moisture status
//                 const waterStatusText = document.getElementById('waterStatusText');
//                 const waterCircle = document.getElementById('waterCircle');
//                 waterStatusText.textContent = latestData.soil_moisture === 'wet' ? 'I feel good' : 'I am thirsty';
//                 waterCircle.style.backgroundColor = latestData.soil_moisture === 'wet' ? 'green' : 'red';

//                 // Update line chart image
//                 const lineChartImage = document.getElementById('lineChartImage');
//                 lineChartImage.src = latestData.standard_plot_url;

//                 // Load artistic images
//                 const gallery = document.getElementById('artGallery');
//                 gallery.innerHTML = ''; // Clear previous images
//                 const img = document.createElement('img');
//                 img.src = latestData.artistic_image_url;
//                 img.alt = "Artistic Image";
//                 gallery.appendChild(img);
//             }
//         })
//         .catch(error => {
//             console.error('Error fetching plant data:', error);
//         });
// });
