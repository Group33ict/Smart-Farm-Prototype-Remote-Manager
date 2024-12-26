// Define base URL for the backend API
const API_BASE_URL = "http://127.0.0.1:5000"; // Replace with your backend URL

let dataChart = null; // Store Chart.js instance

/**
 * Fetch data from the server and update the display for all parameters.
 */
async function fetchData() {
  try {
    console.log("Fetching data from server...");

    const response = await fetch(`${API_BASE_URL}/data_retrieval`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`, // Optional JWT Token
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch data: ${response.statusText}`);
    }

    const serverData = await response.json();
    console.log("Received data from server:", serverData);

    // Check if data exists in the server response
    if (serverData.data && Array.isArray(serverData.data)) {
      updateDisplay(serverData.data);
    } else {
      console.warn("Unexpected server response:", serverData);
      alert("Invalid data format received from the server.");
    }
  } catch (error) {
    console.error("Error fetching data:", error);
    alert("Failed to fetch data. Please try again later.");
  }
}

/**
 * Update the UI with fetched data.
 * @param {Array} data - Array of data objects from the server.
 */
function updateDisplay(data) {
  const tableBody = document.getElementById("data-table-body");
  const alertMessageElement = document.getElementById("alert-message");

  // Clear existing table content
  tableBody.innerHTML = "";

  if (!data || data.length === 0) {
    alertMessageElement.textContent = "No data available.";
    return;
  }

  // Define thresholds for alerts
  const thresholds = {
    temperature: 30,
    humidity: 70,
    co2: 1000,
    light_intensity: 500,
  };

  // Populate the table with new data
  data.forEach((row) => {
    const tableRow = document.createElement("tr");

    tableRow.innerHTML = `
      <td>${row.updated_time || "N/A"}</td>
      <td class="${row.temperature > thresholds.temperature ? "table-danger" : ""}">${row.temperature} °C</td>
      <td class="${row.humidity > thresholds.humidity ? "table-danger" : ""}">${row.humidity} %</td>
      <td class="${row.co2 > thresholds.co2 ? "table-danger" : ""}">${row.co2} ppm</td>
      <td class="${row.light_intensity > thresholds.light_intensity ? "table-danger" : ""}">${row.light_intensity} lux</td>
    `;

    tableBody.appendChild(tableRow);
  });

  // Display alerts if necessary
  const exceededParameters = [];
  data.forEach((row) => {
    if (row.temperature > thresholds.temperature) exceededParameters.push("Temperature");
    if (row.humidity > thresholds.humidity) exceededParameters.push("Humidity");
    if (row.co2 > thresholds.co2) exceededParameters.push("CO₂");
    if (row.light_intensity > thresholds.light_intensity) exceededParameters.push("Light Intensity");
  });

  if (exceededParameters.length > 0) {
    alertMessageElement.textContent = `Warning: ${exceededParameters.join(", ")} exceeded safe thresholds!`;
  } else {
    alertMessageElement.textContent = "";
  }

  // Update the chart with the most recent data row
  if (data.length > 0) {
    updateChart(data[data.length - 1]);
  }
}

/**
 * Create or update the Chart.js chart.
 * @param {Object} latestData - The most recent data object from the server.
 */
function updateChart(latestData) {
  const ctx = document.getElementById("dataChart").getContext("2d");

  if (dataChart) {
    dataChart.destroy(); // Destroy the previous chart instance
  }

  const labels = ["Temperature", "Humidity", "CO₂", "Light Intensity"];
  const data = [
    latestData.temperature,
    latestData.humidity,
    latestData.co2,
    latestData.light_intensity,
  ];

  dataChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Latest Measurements",
          data: data,
          backgroundColor: [
            "rgba(255, 99, 132, 0.2)",
            "rgba(54, 162, 235, 0.2)",
            "rgba(75, 192, 192, 0.2)",
            "rgba(255, 206, 86, 0.2)",
          ],
          borderColor: [
            "rgba(255, 99, 132, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(75, 192, 192, 1)",
            "rgba(255, 206, 86, 1)",
          ],
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: true },
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
 * Initialize the page by fetching data on load.
 */
window.onload = function () {
  fetchData();
};
