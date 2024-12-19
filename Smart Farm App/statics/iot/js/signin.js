document.getElementById("signin-form").addEventListener("submit", async function (event) {
    event.preventDefault();
  
    const email = document.getElementById("signin-email").value;
    const password = document.getElementById("signin-password").value;
  
    // Log user information to the console
    console.log("Sign In Info:", { email, password });
  
    // Simulate API call
    /*
    try {
      const response = await fetch("http://127.0.0.1:5000/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
  
      const data = await response.json();
  
      if (response.ok) {
        alert("Sign in successful!");
        window.location.href = "dashboard.html";
      } else {
        document.getElementById("signin-error-message").innerText = data.message || "Sign in failed!";
      }
    } catch (error) {
      document.getElementById("signin-error-message").innerText = "An error occurred. Please try again.";
      console.error("Error:", error);
    }
    */
  });
  