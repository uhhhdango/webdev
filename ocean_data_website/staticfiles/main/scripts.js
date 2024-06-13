document.addEventListener('DOMContentLoaded', function() {
    // Initialize the map
    var map = L.map('map').setView([0, 0], 2);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Event listener for data source change
    document.getElementById('data-source').addEventListener('change', updateAvailability);
    // Event listeners for other input fields
    document.getElementById('temperature').addEventListener('change', updateAvailability);
    document.getElementById('salinity').addEventListener('change', updateAvailability);
    document.getElementById('north').addEventListener('change', updateAvailability);
    document.getElementById('south').addEventListener('change', updateAvailability);
    document.getElementById('east').addEventListener('change', updateAvailability);
    document.getElementById('west').addEventListener('change', updateAvailability);
    document.getElementById('start-time').addEventListener('change', updateAvailability);
    document.getElementById('end-time').addEventListener('change', updateAvailability);

    // Function to update availability notifications
    function updateAvailability() {
        var source = document.getElementById('data-source').value;
        var parameters = [];
        if (document.getElementById('temperature').checked) parameters.push('temperature');
        if (document.getElementById('salinity').checked) parameters.push('salinity');
        var north = document.getElementById('north').value;
        var south = document.getElementById('south').value;
        var east = document.getElementById('east').value;
        var west = document.getElementById('west').value;
        var startTime = document.getElementById('start-time').value;
        var endTime = document.getElementById('end-time').value;

        // Fetch availability from the server
        fetch(`/get_availability/?source=${source}&parameters=${parameters.join(',')}&north=${north}&south=${south}&east=${east}&west=${west}&start_time=${startTime}&end_time=${endTime}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('parameter-availability').textContent = `Available data: ${data.parameters || 'None'}`;
                document.getElementById('latitude-availability').textContent = `Available latitude: ${data.latitude || 'None'}`;
                document.getElementById('longitude-availability').textContent = `Available longitude: ${data.longitude || 'None'}`;
                document.getElementById('time-availability').textContent = `Available time range: ${data.time_range || 'None'}`;
            })
            .catch(error => console.error('Error fetching availability:', error));
    }
});
