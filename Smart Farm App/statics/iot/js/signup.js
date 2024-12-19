document.getElementById("signup-form").addEventListener("submit", async function (event) {
    event.preventDefault();
  
    const name = document.getElementById("signup-name").value;
    const email = document.getElementById("signup-email").value;
    const password = document.getElementById("signup-password").value;
  
    // Log user information to the console
    console.log("User Signup Info:", { name, email, password });

  });

/*
document.getElementById("signupForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  const username = document.getElementById("signupUsername").value;
  const password = document.getElementById("signupPassword").value;

  try {
    const response = await fetch("http://127.0.0.1:5000/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (response.ok) {
      document.getElementById("signupMessage").textContent =
        "Sign-up successful! Please log in.";
    } else {
      document.getElementById("signupMessage").textContent =
        data.message || "Sign-up failed.";
    }
  } catch (error) {
    console.error("Error during sign-up:", error);
    document.getElementById("signupMessage").textContent =
      "An error occurred. Please try again.";
  }
});

*/
  