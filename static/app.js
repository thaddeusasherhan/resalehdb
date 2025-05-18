async function onSubmit() {
  const location = document.getElementById('locationInput').value;
  if (!location) {
    alert("Please enter a location.");
    return;
  }

  try {
    const formData = new FormData();
    formData.append('locationInput', location);

    const response = await fetch('/process', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();

    if (data.error) {
      alert(data.error);
      return;
    }

    document.getElementById('prices').innerHTML = `Median Price: ${data.median_price}`;
    document.getElementById('median').innerHTML = `Price Range: ${data.min_price} - ${data.max_price}`;
    document.getElementById('distance').innerHTML = `Price Variance: ${data.variance}`;
    document.getElementById('amenities').innerHTML = `Standard Deviation: ${data.std}`;
  } catch (error) {
    console.error('Error:', error);
    alert('An error occurred while processing your request.');
  }
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