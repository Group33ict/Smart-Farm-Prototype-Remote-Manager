const API_BASE_URL = "http://127.0.0.1:5000"; 
let currentFilter = "all"; // Default filter

const thresholds = {
    temperature: 30,
    humidity: 60,
    co2: 1000,
    light_intensity: 500,
};

/**
 * Fetch history data from the server and populate the table.
 */
async function fetchHistoryData() {
    try {
        console.log(`Fetching history data with filter: ${currentFilter}...`);
        const response = await fetch(`${API_BASE_URL}/data_retrieval`, {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch history data: ${response.statusText}`);
        }

        const data = await response.json();
        if (data && Array.isArray(data.data)) {
            populateHistoryTable(data.data);
        } else {
            displayAlert("Invalid data format received from the server.");
        }
    } catch (error) {
        console.error("Error fetching history data:", error);
        displayAlert("Error fetching history data. Please check your connection or server.");
    }
}

/**
 * Populate the history table with data.
 * @param {Array} data - Array of data objects.
 */
function populateHistoryTable(data) {
    const tableBody = document.getElementById("history-table-body");
    const alertMessageElement = document.getElementById("alert-message");

    // Clear existing table content and alerts
    tableBody.innerHTML = "";
    alertMessageElement.style.display = "none";

    if (!data || data.length === 0) {
        alertMessageElement.textContent = "No data available.";
        alertMessageElement.style.display = "block";
        return;
    }

    // Filter data based on the selected filter
    const filteredData = currentFilter === "all" ? data : data.map((row) => ({
        ...row,
        highlight: exceedsThreshold(currentFilter, row[currentFilter]),
    }));

    // Populate the table with filtered data
    filteredData.forEach((row) => {
        const tableRow = document.createElement("tr");

        // Highlight row in red if any value exceeds thresholds
        const isHighlighted = currentFilter === "all"
            ? Object.keys(thresholds).some((key) => exceedsThreshold(key, row[key]))
            : row.highlight;

        if (isHighlighted) {
            tableRow.style.backgroundColor = "#ffcccc"; // Light red
        }

        tableRow.innerHTML = `
            <td>${row.updated_time || "N/A"}</td>
            <td>${row.temperature || "N/A"}</td>
            <td>${row.humidity || "N/A"}</td>
            <td>${row.co2 || "N/A"}</td>
            <td>${row.light_intensity || "N/A"}</td>
        `;

        tableBody.appendChild(tableRow);
    });
}

/**
 * Check if a value exceeds the threshold for a specific filter.
 * @param {string} filter - The filter (temperature, humidity, co2, light_intensity).
 * @param {number} value - The value to check.
 * @returns {boolean} - True if the value exceeds the threshold, otherwise false.
 */
function exceedsThreshold(filter, value) {
    return parseFloat(value) > thresholds[filter];
}

/**
 * Display an alert message.
 * @param {string} message - The message to display.
 */
function displayAlert(message) {
    const alertMessageElement = document.getElementById("alert-message");
    alertMessageElement.textContent = message;
    alertMessageElement.style.display = "block";
}

/**
 * Set the current filter and re-fetch the data.
 * @param {string} filter - The selected filter.
 */
function setFilter(filter) {
    currentFilter = filter;
    console.log(`Filter set to: ${filter}`);
    fetchHistoryData();
}

// Fetch data on page load
window.onload = fetchHistoryData;
