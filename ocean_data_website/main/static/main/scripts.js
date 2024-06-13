document.addEventListener('DOMContentLoaded', () => {
    // Existing map initialization code
    const map = L.map('map').setView([0, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
    }).addTo(map);

    // Add a feature group to store drawn layers
    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    // Add the drawing control tool
    const drawControl = new L.Control.Draw({
        edit: {
            featureGroup: drawnItems,
        },
        draw: {
            polygon: false,
            polyline: false,
            circle: false,
            marker: false,
            rectangle: {
                shapeOptions: {
                    color: '#2a9df4'
                }
            }
        }
    });
    map.addControl(drawControl);

    let rectangle;

    // Event listener for when a new shape (rectangle) is created
    map.on(L.Draw.Event.CREATED, (event) => {
        const layer = event.layer;
        drawnItems.clearLayers();
        drawnItems.addLayer(layer);
        rectangle = layer;
        const bounds = layer.getBounds();
        document.getElementById('north').value = bounds.getNorth();
        document.getElementById('south').value = bounds.getSouth();
        document.getElementById('east').value = bounds.getEast();
        document.getElementById('west').value = bounds.getWest();
    });

    // Update the rectangle when coordinate fields change
    const coordinateFields = ['north', 'south', 'east', 'west'];
    coordinateFields.forEach(field => {
        document.getElementById(field).addEventListener('change', updateRectangle);
    });

    function updateRectangle() {
        const north = parseFloat(document.getElementById('north').value);
        const south = parseFloat(document.getElementById('south').value);
        const east = parseFloat(document.getElementById('east').value);
        const west = parseFloat(document.getElementById('west').value);

        if (!isNaN(north) && !isNaN(south) && !isNaN(east) && !isNaN(west)) {
            const bounds = [[south, west], [north, east]];
            if (rectangle) {
                drawnItems.removeLayer(rectangle);
            }
            rectangle = L.rectangle(bounds, { color: '#2a9df4' });
            drawnItems.addLayer(rectangle);
            map.fitBounds(bounds);
        }
    }

    // Existing event listeners
    document.getElementById('source').addEventListener('change', updateAvailableData);

    function updateAvailableData() {
        const source = document.getElementById('source').value;

        const url = `/get_available_data_ranges/?source=${source}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                document.getElementById('parameters-availability').textContent = `Available data: ${data.parameters || 'None'}`;
                document.getElementById('latitude-availability').textContent = `Available latitude: ${data.latitude || 'None'}`;
                document.getElementById('longitude-availability').textContent = `Available longitude: ${data.longitude || 'None'}`;
                document.getElementById('time-availability').textContent = `Available time range: ${data.time || 'None'}`;
            })
            .catch(error => console.error('Error fetching data availability:', error));
    }

    document.getElementById('download').addEventListener('click', () => {
        const source = document.getElementById('source').value;
        const parameters = Array.from(document.querySelectorAll('input[type="checkbox"]:checked')).map(cb => cb.value);
        const north = document.getElementById('north').value;
        const south = document.getElementById('south').value;
        const east = document.getElementById('east').value;
        const west = document.getElementById('west').value;

        const start_time = new Date(document.getElementById('start_time').value).toISOString();
        const end_time = new Date(document.getElementById('end_time').value).toISOString();

        const url = `/get_data/?source=${source}&parameters=${parameters.join(',')}&north=${north}&south=${south}&east=${east}&west=${west}&start_time=${start_time}&end_time=${end_time}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.length === 0) {
                    console.error('No data available for the selected criteria');
                    return;
                }

                const csvContent = "data:text/csv;charset=utf-8,"
                    + Object.keys(data[0]).join(",") + "\n"
                    + data.map(e => Object.values(e).join(",")).join("\n");

                const encodedUri = encodeURI(csvContent);
                const link = document.createElement("a");
                link.setAttribute("href", encodedUri);
                link.setAttribute("download", "ocean_data.csv");
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            })
            .catch(error => console.error('Error fetching data:', error));
    });
});
