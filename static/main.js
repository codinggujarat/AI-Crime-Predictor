document.addEventListener("DOMContentLoaded", function () {
    // Initialize map
    const map = L.map("map").setView([20.5937, 78.9629], 5); // Default India view

    // Add OpenStreetMap layer
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);

    // Fetch heatmap data
    fetch("/get-heatmap-data")
        .then(response => response.json())
        .then(data => {
            const heatPoints = data.map(row => [row.latitude, row.longitude, row.intensity || 0.5]);

            // Add heat layer
            L.heatLayer(heatPoints, {
                radius: 20,
                blur: 15,
                maxZoom: 17,
            }).addTo(map);
        })
        .catch(err => console.error("Error loading heatmap:", err));
});
