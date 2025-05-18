function onSubmit() {
  const location = document.getElementById('locationInput').value;
  if (!location) {
    alert("Please enter a location.");
    return;
  }

  console.log("Submitted location:", location);
  fetchResales(location);
  fetchMedian(location);
  fetchDistance(location);
  fetchAmenities(location);
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
