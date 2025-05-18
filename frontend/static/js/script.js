document.getElementById('aqi-form').addEventListener('submit', async function (e) {
  e.preventDefault();

  const city = document.getElementById('city').value;
  const date = document.getElementById('date').value;

  try {
    const response = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ city, date })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    const container = document.getElementById('results');
    container.innerHTML = '';

    if (data.predicted_aqi_next_7_days) {
      const cardsRow = document.createElement('div');
      cardsRow.className = 'row justify-content-center';

      data.predicted_aqi_next_7_days.forEach(day => {
        const level = getAQILevel(day.predicted_aqi);
        const icon = getAQIIcon(level);

        const card = `
          <div class="col-md-4 d-flex justify-content-center mb-4">
            <div class="card shadow" style="width: 20rem; border-radius: 2rem;">
              <div class="card-body text-center">
                <div class="mb-3">
                  <img src="${icon}" class="rounded-circle" style="width: 80px; height: 80px;" alt="${level}" )" />
                </div>
                <h5 class="card-title">${day.date}</h5>
                <p class="card-text">
                  AQI: <strong>${day.predicted_aqi}</strong><br/>
                  Level: <span class="badge bg-${getAQIBootstrapColor(level)}">${level}</span>
                </p>
              </div>
            </div>
          </div>
        `;
        cardsRow.innerHTML += card;
      });

      container.appendChild(cardsRow);
    } else {
      container.innerHTML = '<p class="text-danger">No prediction available for the selected date.</p>';
    }
  } catch (error) {
    console.error('Error fetching prediction:', error);
    document.getElementById('results').innerHTML = '<p class="text-danger">Error fetching prediction. Please try again.</p>';
  }
});

// Helper functions
function getAQILevel(aqi) {
  if (aqi <= 50) return 'Good';
  if (aqi <= 100) return 'Moderate';
  if (aqi <= 150) return 'Unhealthy for Sensitive Groups';
  if (aqi <= 200) return 'Unhealthy';
  if (aqi <= 300) return 'Poor';
  if (aqi <= 400) return 'Very Poor';
  return 'Severe';
}

function getAQIBootstrapColor(level) {
  switch (level) {
    case 'Good': return 'success';
    case 'Moderate': return 'info';
    case 'Unhealthy for Sensitive Groups': return 'primary';
    case 'Unhealthy': return 'warning';
    case 'Poor': return 'danger';
    case 'Very Poor': return 'dark';
    case 'Severe': return 'dark';
    default: return 'secondary';
  }
}

function getAQIIcon(level) {
  const basePath = '/static/images/';
  switch (level) {
    case 'Good': return `${basePath}good.png`;
    case 'Moderate': return `${basePath}moderate.png`;
    case 'Unhealthy for Sensitive Groups': return `${basePath}sensitive.png`;
    case 'Unhealthy': return `${basePath}Unhealthy.png`;
    case 'Poor': return `${basePath}Unhealthy.png`;
    case 'Very Poor': return `${basePath}very_poor.png`;
    case 'Severe': return `${basePath}severe.png`;
    default: return `${basePath}severe.png`;
  }
}