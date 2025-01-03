// Define base URL for the backend API
const API_BASE_URL = "http://127.0.0.1:5000"; 

let dataChart = null; // Store Chart.js instance
let currentFilter = "temperature"; // Default filter

// Default thresholds
const thresholds = {
  temperature: 30, // Default threshold for temperature
  humidity: 60,    // Default threshold for humidity
  co2: 1000,       // Default threshold for CO₂ level
  light_intensity: 500 // Default threshold for light intensity
};

/**
 * Fetch data from the server and update the display for the current filter.
 */
async function fetchData() {
  try {
    console.log(`Fetching data for filter: ${currentFilter}...`);

    const response = await fetch(`${API_BASE_URL}/data_retrieval`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("access_token")}` // Optional JWT Token
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch data: ${response.statusText}`);
    }

    const serverData = await response.json();
    console.log("Received data from server:", serverData);

    if (serverData.data && Array.isArray(serverData.data)) {
      updateDisplay(serverData.data);
    } else {
      console.warn("Unexpected server response:", serverData);
      alert("Invalid data format received from the server.");
    }
  } catch (error) {
    console.error("Error fetching data:", error);
    const alertMessageElement = document.getElementById("alert-message");
    alertMessageElement.textContent = "Error fetching data. Please check your internet connection or server status.";
    alertMessageElement.style.display = "block";
  }
}

/**
 * Update the UI with fetched data based on the current filter.
 * @param {Array} data - Array of data objects from the server.
 */
function updateDisplay(data) {
  const tableBody = document.getElementById("data-table-body");
  const alertMessageElement = document.getElementById("alert-message");

  // Clear existing table content and alert
  tableBody.innerHTML = "";
  alertMessageElement.style.display = "none";

  if (!data || data.length === 0) {
    alertMessageElement.textContent = "No data available.";
    alertMessageElement.style.display = "block";
    return;
  }

  // Update thresholds from input fields
  updateThresholds();

  // Filter and display data
  const filteredData = data.map((row) => ({
    time: row.updated_time || "N/A",
    value: parseFloat(row[currentFilter]) || "N/A" // Parse value to ensure it's numeric
  }));

  // Populate the table with all filtered data
  filteredData.forEach((row) => {
    const tableRow = document.createElement("tr");
    tableRow.innerHTML = `
      <td>${row.time}</td>
      <td>${row.value}</td>
    `;

    // Highlight row in red if value exceeds threshold
    if (exceedsThreshold(currentFilter, row.value)) {
      tableRow.style.backgroundColor = "#ffcccc"; // Light red background
    }

    tableBody.appendChild(tableRow);
  });

  // Check the latest data value
  const latestData = filteredData[filteredData.length - 1];
  if (latestData && exceedsThreshold(currentFilter, latestData.value)) {
    alertMessageElement.textContent = `Warning: Latest ${currentFilter} value (${latestData.value}) exceeds the threshold of ${thresholds[currentFilter]}!`;
    alertMessageElement.style.display = "block";
  }

  // Update the chart with the filtered data and threshold
  updateChart(filteredData);
}

/**
 * Update the Chart.js chart with a threshold line and red fill above the threshold.
 * @param {Array} data - Array of filtered data objects.
 */
function updateChart(data) {
  const ctx = document.getElementById("dataChart").getContext("2d");

  if (dataChart) {
    dataChart.destroy(); // Destroy the previous chart instance
  }

  const labels = data.map((row) => row.time);
  const values = data.map((row) => row.value);
  const thresholdValue = thresholds[currentFilter];

  dataChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: `Latest ${currentFilter} Data`,
          data: values,
          borderColor: "rgba(75, 192, 192, 1)",
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          borderWidth: 2,
          fill: {
            target: { value: thresholdValue },
            above: "rgba(255, 0, 0, 0.3)", // Red fill above threshold
            below: "rgba(0, 0, 0, 0)", // No fill below threshold
          },
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: true },
        annotation: {
          annotations: {
            threshold: {
              type: "line",
              yMin: thresholdValue,
              yMax: thresholdValue,
              borderColor: "red",
              borderWidth: 2,
              label: {
                content: `Threshold: ${thresholdValue}`,
                enabled: true,
                position: "end",
              },
            },
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
}

/**
 * Check if a value exceeds the threshold.
 * @param {string} filter - The current filter (temperature, humidity, co2, light_intensity).
 * @param {number} value - The current value to check.
 * @returns {boolean} - True if the value exceeds the threshold, otherwise false.
 */
function exceedsThreshold(filter, value) {
  return parseFloat(value) > thresholds[filter];
}

/**
 * Update thresholds from input fields.
 */
function updateThresholds() {
  thresholds.temperature = parseFloat(document.getElementById("temp-threshold").value) || thresholds.temperature;
  thresholds.humidity = parseFloat(document.getElementById("humidity-threshold").value) || thresholds.humidity;
  thresholds.co2 = parseFloat(document.getElementById("co2-threshold").value) || thresholds.co2;
  thresholds.light_intensity = parseFloat(document.getElementById("light-threshold").value) || thresholds.light_intensity;
}

/**
 * Set the filter and update the display.
 * @param {string} filter - The filter to apply (temperature, humidity, co2, light_intensity).
 */
function setFilter(filter) {
  currentFilter = filter;
  console.log(`Filter set to: ${filter}`);
  fetchData(); // Re-fetch data to update display
}

/**
 * Control actions for devices: lights, fans, and windows.
 * @param {string} action - The action to perform (open_window, close_window, light_on, light_off, open_fan, close_fan).
 */
async function controlDevice(action) {
  try {
    const response = await fetch(`${API_BASE_URL}/${action}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to ${action}: ${response.statusText}`);
    }

    const result = await response.json();
    alert(`Action '${action}' successful: ${result.message}`);
  } catch (error) {
    console.error(`Error performing action '${action}':`, error);
    alert(`Failed to perform action '${action}'. Please try again later.`);
  }
}

/**
 * Initialize the page by setting up event listeners and fetching data on load.
 */
window.onload = function () {
  const temperatureBtn = document.getElementById("btn-temperature");
  const humidityBtn = document.getElementById("btn-humidity");
  const co2Btn = document.getElementById("btn-co2");
  const lightBtn = document.getElementById("btn-light");
  const lightOnBtn = document.getElementById("btn-light-on");
  const lightOffBtn = document.getElementById("btn-light-off");
  const fanOnBtn = document.getElementById("btn-fan-on");
  const fanOffBtn = document.getElementById("btn-fan-off");
  const windowOpenBtn = document.getElementById("btn-window-open");
  const windowCloseBtn = document.getElementById("btn-window-close");

  // Ensure buttons exist in DOM before adding event listeners
  if (temperatureBtn) {
    temperatureBtn.addEventListener("click", () => setFilter("temperature"));
  }
  if (humidityBtn) {
    humidityBtn.addEventListener("click", () => setFilter("humidity"));
  }
  if (co2Btn) {
    co2Btn.addEventListener("click", () => setFilter("co2"));
  }
  if (lightBtn) {
    lightBtn.addEventListener("click", () => setFilter("light_intensity"));
  }
  if (lightOnBtn) {
    lightOnBtn.addEventListener("click", () => toggleDevice("light_on"));
  }
  if (lightOffBtn) {
    lightOffBtn.addEventListener("click", () => toggleDevice("light_off"));
  }
  if (fanOnBtn) {
    fanOnBtn.addEventListener("click", () => toggleDevice("open_fan"));
  }
  if (fanOffBtn) {
    fanOffBtn.addEventListener("click", () => toggleDevice("close_fan"));
  }
  if (windowOpenBtn) {
    windowOpenBtn.addEventListener("click", () => toggleDevice("open_window"));
  }
  if (windowCloseBtn) {
    windowCloseBtn.addEventListener("click", () => toggleDevice("close_window"));
  }

  fetchData(); // Initial fetch
};
