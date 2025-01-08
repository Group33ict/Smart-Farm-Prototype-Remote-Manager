document.addEventListener("DOMContentLoaded", () => {
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.nav-link');
  
    sidebarLinks.forEach(link => {
      if (currentPath.includes(link.getAttribute('href'))) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  });
  

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

/**
 * Fetch fresh data from the backend using the `/retrieve_sensor_data` endpoint.
 */
async function refreshData() {
  try {
    console.log("Refreshing data from the backend...");

    const response = await fetch(`${API_BASE_URL}/retrieve_sensor_data`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("access_token")}` // Optional JWT Token
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to refresh data: ${response.statusText}`);
    }

    const result = await response.json();
    console.log("Data refreshed successfully:", result);

    alert("Refresh successfully!");
    fetchData(); // Re-fetch the updated data to display
  } catch (error) {
    console.error("Error refreshing data:", error);
    alert("Cannot refresh.");
  }
}

const refreshBtn = document.getElementById("btn-refresh");
if (refreshBtn) {
  refreshBtn.addEventListener("click", refreshData);
}




