// Sample data for initial display
let light = 350;       // Light in lx
let temperature = 24;  // Temperature in °C
let humidity = 55;     // Humidity in %
let co2 = 400;         // CO2 in ppm

// Update the overview widget values
function updateDashboardValues() {
  document.getElementById("light-value").textContent = `${light} lx`;
  document.getElementById("temperature-value").textContent = `${temperature} °C`;
  document.getElementById("humidity-value").textContent = `${humidity} %`;
  document.getElementById("co2-value").textContent = `${co2} ppm`;
}

// Simulate real-time data updates
function simulateData() {
  light = Math.round(300 + Math.random() * 100);
  temperature = Math.round(22 + Math.random() * 6);
  humidity = Math.round(50 + Math.random() * 10);
  co2 = Math.round(350 + Math.random() * 150);
  updateDashboardValues();
  updateChart();
}

// Control functions
function toggleLight() {
  light = light > 300 ? 150 : 400; // Toggle light intensity
  updateDashboardValues();
}

function adjustTemperature(value) {
  temperature += value;
  updateDashboardValues();
}

function adjustHumidity(value) {
  humidity += value;
  updateDashboardValues();
}

function adjustCO2(value) {
  co2 += value;
  updateDashboardValues();
}

// Save settings function
function saveSettings() {
  const lightThreshold = document.getElementById("light-threshold").value;
  const tempThreshold = document.getElementById("temp-threshold").value;
  const humidityThreshold = document.getElementById("humidity-threshold").value;
  const co2Threshold = document.getElementById("co2-threshold").value;
  
  alert(`Settings saved! \nLight Threshold: ${lightThreshold} lx\nTemperature Threshold: ${tempThreshold} °C\nHumidity Threshold: ${humidityThreshold} %\nCO2 Threshold: ${co2Threshold} ppm`);
}

// Chart.js for data visualization
const ctx = document.getElementById('dataChart').getContext('2d');
const dataChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: Array.from({ length: 10 }, (_, i) => `Time ${i + 1}`),
    datasets: [
      {
        label: 'Light (lx)',
        borderColor: 'orange',
        data: Array(10).fill(0),
      },
      {
        label: 'Temperature (°C)',
        borderColor: 'red',
        data: Array(10).fill(0),
      },
      {
        label: 'Humidity (%)',
        borderColor: 'blue',
        data: Array(10).fill(0),
      },
      {
        label: 'CO₂ (ppm)',
        borderColor: 'green',
        data: Array(10).fill(0),
      }
    ]
  },
  options: {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});

// Update the chart data in real-time
function updateChart() {
  const maxDataPoints = 10;
  const datasets = dataChart.data.datasets;

  // Shift old data and add new values
  datasets[0].data.push(light);
  datasets[1].data.push(temperature);
  datasets[2].data.push(humidity);
  datasets[3].data.push(co2);

  // Limit data points to the max defined
  datasets.forEach(dataset => {
    if (dataset.data.length > maxDataPoints) {
      dataset.data.shift();
    }
  });

  dataChart.update();
}

// Run data simulation at intervals
setInterval(simulateData, 3000);
document.addEventListener("DOMContentLoaded", updateDashboardValues);

//wifi
document.addEventListener("DOMContentLoaded", () => {
  // List WiFi
  const wifiListElement = document.getElementById("wifi-list");

  function fetchWiFiNetworks() {
      console.log("Fetching WiFi networks..."); // Log kiểm tra

      // Danh sách WiFi mô phỏng (thay thế bằng API thực tế)
      const wifiNetworks = [
          { name: "USTH Classroom", strength: "Strong" },
          { name: "USTH Guest", strength: "Moderate" },
          { name: "USTH Student", strength: "Weak" }
      ];

      // Xóa các mục cũ trong dropdown
      wifiListElement.innerHTML = "";

      // Kiểm tra nếu không có mạng WiFi nào
      if (wifiNetworks.length === 0) {
          wifiListElement.innerHTML = `<li><a class="dropdown-item" href="#">No WiFi networks found</a></li>`;
          return;
      }

      // Thêm các mạng WiFi vào danh sách
      wifiNetworks.forEach(network => {
          const listItem = document.createElement("li");
          listItem.innerHTML = `<a class="dropdown-item" href="#">${network.name} - ${network.strength}</a>`;
          wifiListElement.appendChild(listItem);
      });
  }

  const wifiDropdown = wifiListElement.parentElement;
  wifiDropdown.addEventListener("show.bs.dropdown", () => {
      fetchWiFiNetworks(); 
  });
});




