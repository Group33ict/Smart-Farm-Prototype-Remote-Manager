document.getElementById("signup-form").addEventListener("submit", async function (event) {
    event.preventDefault();
  
    const name = document.getElementById("signup-name").value;
    const email = document.getElementById("signup-email").value;
    const password = document.getElementById("signup-password").value;
  
    // Log user information to the console
    console.log("User Signup Info:", { name, email, password });
  
    // Simulate API call
    /*
    try {
      const response = await fetch("http://127.0.0.1:5000/statics/iot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });
  
      const data = await response.json();
  
      if (response.ok) {
        alert("Sign up successful! Please sign in.");
        window.location.href = "signin.html";
      } else {
        document.getElementById("signup-error-message").innerText = data.message || "Sign up failed!";
      }
    } catch (error) {
      document.getElementById("signup-error-message").innerText = "An error occurred. Please try again.";
      console.error("Error:", error);
    }
    */
  });
  