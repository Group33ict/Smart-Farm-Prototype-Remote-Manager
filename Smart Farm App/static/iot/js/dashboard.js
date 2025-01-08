// Define base URL for the backend API
const API_BASE_URL = "http://127.0.0.1:5000";

// Default thresholds
const thresholds = {
  temperature: 30,
  humidity: 60,
  co2: 1000,
  light_intensity: 500,
};

let dataChart; // Declare the chart variable globally

/**
 * Initialize the chart for data visualization.
 */
function initializeChart() {
  const ctx = document.getElementById("dataChart").getContext("2d");
  dataChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [], // Time labels will be updated dynamically
      datasets: [
        {
          label: "Temperature (°C)",
          data: [],
          borderColor: "red",
          backgroundColor: "rgba(255, 0, 0, 0.1)",
          fill: true,
        },
        {
          label: "Humidity (%)",
          data: [],
          borderColor: "blue",
          backgroundColor: "rgba(0, 0, 255, 0.1)",
          fill: true,
        },
        {
          label: "CO₂ (ppm)",
          data: [],
          borderColor: "gray",
          backgroundColor: "rgba(128, 128, 128, 0.1)",
          fill: true,
        },
        {
          label: "Light Intensity (lx)",
          data: [],
          borderColor: "orange",
          backgroundColor: "rgba(255, 165, 0, 0.1)",
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true,
          position: "top",
        },
      },
      scales: {
        x: {
          title: {
            display: true,
            text: "Time",
          },
        },
        y: {
          title: {
            display: true,
            text: "Values",
          },
        },
      },
    },
  });
}

/**
 * Fetch data for all parameters and update the dashboard overview and chart.
 */
async function fetchData() {
  try {
    console.log("Fetching data for all parameters...");

    const response = await fetch(`${API_BASE_URL}/data_retrieval`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch data: ${response.statusText}`);
    }

    const serverData = await response.json();
    console.log("Received data from server:", serverData);

    if (serverData.data && Array.isArray(serverData.data)) {
      updateOverview(serverData.data);
      updateChart(serverData.data);
    } else {
      console.warn("Unexpected server response:", serverData);
      alert("Invalid data format received from the server.");
    }
  } catch (error) {
    console.error("Error fetching data:", error);
    const alertMessageElement = document.getElementById("alert-message");
    if (alertMessageElement) {
      alertMessageElement.textContent = "Error fetching data. Please check your internet connection or server status.";
      alertMessageElement.style.display = "block";
    }
  }
}

/**
 * Update the dashboard overview with the fetched data.
 * @param {Array} data - Array of data objects from the server.
 */
function updateOverview(data) {
  const alertMessageElement = document.getElementById("alert-message");
  const overviewCards = {
    temperature: document.getElementById("temperature-value"),
    humidity: document.getElementById("humidity-value"),
    co2: document.getElementById("co2-value"),
    light_intensity: document.getElementById("light-value"),
  };

  // Clear any existing alerts
  if (alertMessageElement) {
    alertMessageElement.style.display = "none";
  }

  if (!data || data.length === 0) {
    if (alertMessageElement) {
      alertMessageElement.textContent = "No data available.";
      alertMessageElement.style.display = "block";
    }
    return;
  }

  // Get the latest data for each parameter
  const latestData = data[data.length - 1];

  Object.keys(overviewCards).forEach((key) => {
    const valueElement = overviewCards[key];

    if (valueElement) {
      const value = parseFloat(latestData[key]) || 0;
      valueElement.textContent = value;

      // Highlight card if value exceeds the threshold
      const cardElement = valueElement.closest(".card");
      if (cardElement) {
        cardElement.style.backgroundColor = exceedsThreshold(key, value) ? "#ffcccc" : "#ffffff";
      }
    }
  });
}

/**
 * Update the chart with fetched data.
 * @param {Array} data - Array of data objects from the server.
 */
function updateChart(data) {
  console.log("Updating chart with data:", data);

  if (!data || data.length === 0) {
    console.warn("No data available for chart update.");
    return;
  }

  // Extract time labels and parameter data
  const timeLabels = data.map((entry) => entry.time || "N/A"); // Use default if time is undefined
  const temperatureData = data.map((entry) => parseFloat(entry.temperature) || 0);
  const humidityData = data.map((entry) => parseFloat(entry.humidity) || 0);
  const co2Data = data.map((entry) => parseFloat(entry.co2) || 0);
  const lightData = data.map((entry) => parseFloat(entry.light_intensity) || 0);

  console.log("Time Labels:", timeLabels);
  console.log("Temperature Data:", temperatureData);
  console.log("Humidity Data:", humidityData);
  console.log("CO2 Data:", co2Data);
  console.log("Light Intensity Data:", lightData);

  // Update chart data
  dataChart.data.labels = timeLabels;
  dataChart.data.datasets[0].data = temperatureData;
  dataChart.data.datasets[1].data = humidityData;
  dataChart.data.datasets[2].data = co2Data;
  dataChart.data.datasets[3].data = lightData;

  // Refresh the chart
  dataChart.update();
}

/**
 * Check if a value exceeds the threshold.
 * @param {string} filter - The parameter (temperature, humidity, co2, light_intensity).
 * @param {number} value - The current value to check.
 * @returns {boolean} - True if the value exceeds the threshold, otherwise false.
 */
function exceedsThreshold(filter, value) {
  return parseFloat(value) > thresholds[filter];
}

// Initialize the chart and fetch data on page load
window.onload = function () {
  initializeChart();
  fetchData(); // Fetch data and update overview and chart
};
