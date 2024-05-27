document.addEventListener('DOMContentLoaded', function() {
    fetch('/plant-data')
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                const latestData = data[data.length - 1]; // Assuming the latest data is at the end of the array

                // Update soil moisture status
                const waterStatusText = document.getElementById('waterStatusText');
                const waterCircle = document.getElementById('waterCircle');
                waterStatusText.textContent = latestData.soil_moisture === 'wet' ? 'I feel good' : 'I am thirsty';
                waterCircle.style.backgroundColor = latestData.soil_moisture === 'wet' ? 'green' : 'red';

                // Update line chart image
                const lineChartImage = document.getElementById('lineChartImage');
                lineChartImage.src = latestData.standard_plot_url;

                // Load artistic images
                const gallery = document.getElementById('artGallery');
                gallery.innerHTML = ''; // Clear previous images
                const img = document.createElement('img');
                img.src = latestData.artistic_image_url;
                img.alt = "Artistic Image";
                gallery.appendChild(img);
            }
        })
        .catch(error => {
            console.error('Error fetching plant data:', error);
        });
});
