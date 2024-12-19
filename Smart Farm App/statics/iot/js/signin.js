document.getElementById("signin-form").addEventListener("submit", async function (event) {
    event.preventDefault();
  
    const email = document.getElementById("signin-email").value;
    const password = document.getElementById("signin-password").value;
  
    
    console.log("Sign In Info:", { email, password });
  
  });

/*
document.getElementById("loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  const username = document.getElementById("loginUsername").value;
  const password = document.getElementById("loginPassword").value;

  try {
    const response = await fetch("http://127.0.0.1:5000/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (response.ok) {
      // Store the JWT token in localStorage
      localStorage.setItem("access_token", data.access_token);
      document.getElementById("loginMessage").textContent = "Log-in successful!";
      // Redirect to the dashboard or another page
      window.location.href = "/dashboard";
    } else {
      document.getElementById("loginMessage").textContent =
        data.message || "Log-in failed.";
    }
  } catch (error) {
    console.error("Error during log-in:", error);
    document.getElementById("loginMessage").textContent =
      "An error occurred. Please try again.";
  }
});
  
*/