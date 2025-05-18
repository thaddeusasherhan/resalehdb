function onSubmit() {
  const locationInput = document.getElementById('locationInput').value;
  const analysisImage = document.getElementById('analysis-image');

  fetch('/process', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `locationInput=${encodeURIComponent(locationInput)}`
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      // Add timestamp to prevent caching
      analysisImage.src = `/static/${data.image}?t=${Date.now()}`;
      analysisImage.style.display = 'block';
      document.getElementById('median').textContent = `Latest Median Price: $${data.median_price}/sqm`;
    } else {
      alert('Town not found');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert('An error occurred');
  });
}

// Stub functions

function fetchResales(location) {
  console.log("Fetching resales for:", location);
  // TODO: Replace with actual API call and DOM update
}

function fetchMedian(location) {
  console.log("Fetching median for:", location);
  // TODO: Replace with actual logic
}

function fetchDistance(location) {
  console.log("Calculating distance for:", location);
  // TODO: Replace with actual logic
}

function fetchAmenities(location) {
  console.log("Fetching nearby amenities for:", location);
  // TODO: Replace with actual logic
}