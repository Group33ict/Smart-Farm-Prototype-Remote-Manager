const sampleData = {
  temperature: {
    labels: ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00'],
    data: [20, 21, 22, 25, 24, 23],
    unit: '°C',
    threshold: 23 // Threshold for temperature
  },
  humidity: {
    labels: ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00'],
    data: [55, 50, 53, 60, 58, 54],
    unit: '%',
    threshold: 60 // Threshold for humidity
  },
  co2: {
    labels: ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00'],
    data: [400, 420, 430, 440, 450, 455],
    unit: 'ppm',
    threshold: 450 // Threshold for CO2
  },
  light: {
    labels: ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00'],
    data: [200, 250, 300, 400, 350, 300],
    unit: 'lx',
    threshold: 350 // Threshold for light
  }
};

let dataChart;

function showData(type) {
  const selectedData = sampleData[type];
  const threshold = selectedData.threshold;

  // Update current stats display
  document.getElementById("current-stats").innerHTML = 
    `Current Plant Stats: Temperature: ${selectedData.data[selectedData.data.length - 1]} ${selectedData.unit}, 
     Humidity: ${sampleData.humidity.data[sampleData.humidity.data.length - 1]} %, 
     Light: ${sampleData.light.data[sampleData.light.data.length - 1]} lx, 
     CO₂: ${sampleData.co2.data[sampleData.co2.data.length - 1]} ppm`;

  document.getElementById("alert-message").textContent = "";

  const tableBody = document.getElementById("data-table-body");
  tableBody.innerHTML = ""; // Clear previous table data
  selectedData.data.forEach((value, index) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${selectedData.labels[index]}</td>
      <td class="${value > threshold ? 'table-danger' : ''}">${value} ${selectedData.unit}</td>
    `;
    tableBody.appendChild(row);

    if (value > threshold) {
      document.getElementById("alert-message").textContent = 
        `Warning: ${type.charAt(0).toUpperCase() + type.slice(1)} exceeded safe threshold!`;
    }
  });

  if (dataChart) {
    dataChart.destroy(); // Destroy existing chart
  }

  const ctx = document.getElementById("dataChart").getContext("2d");

  dataChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: selectedData.labels,
      datasets: [
        {
          label: `${type.charAt(0).toUpperCase() + type.slice(1)} (${selectedData.unit})`,
          data: selectedData.data,
          borderColor: 'rgba(0, 0, 0, 0.1)',
          borderWidth: 1,
          segment: {
            backgroundColor: ctx => ctx.p1.parsed.y > threshold ? 'rgba(255, 99, 132, 0.5)' : 'rgba(54, 162, 235, 0.5)',
          },
          fill: true,
          pointRadius: 4,
          pointBackgroundColor: 'rgba(0, 0, 0, 0.5)'
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: true },
        annotation: {
          annotations: [{
            type: 'line',
            yMin: threshold,
            yMax: threshold,
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 2,
            label: {
              enabled: true,
              content: 'Threshold',
              color: 'rgba(255, 99, 132, 1)',
              position: 'start'
            }
          }]
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: `${type.charAt(0).toUpperCase() + type.slice(1)} (${selectedData.unit})`
          }
        },
        x: {
          title: {
            display: true,
            text: 'Time'
          }
        }
      }
    }
  });
}

// Adjust temperature function
function adjustTemperature(delta) {
  const currentTemp = sampleData.temperature.data[sampleData.temperature.data.length - 1];
  const newTemp = currentTemp + delta;
  sampleData.temperature.data.push(newTemp); // Update data
  sampleData.temperature.labels.push(`Next Hour`); // Simulate new time label
  showData('temperature'); // Refresh data display
}

// Toggle light function
function toggleLight() {
  alert("Toggling light...");
}

// Adjust fan function
function adjustFan() {
  alert("Adjusting fan settings...");
}

// Water plant function
function waterPlant() {
  alert("Watering plant...");
}

// Initialize with temperature data
window.onload = function() {
  showData('temperature');
};

function hideNotification() {
  const notificationCount = document.getElementById('notification-count');
  notificationCount.style.display = 'none'; // Ẩn số thông báo
}
