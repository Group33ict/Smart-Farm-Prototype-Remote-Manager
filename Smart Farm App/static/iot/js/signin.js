document.getElementById('signin-form').addEventListener('submit', async function(event) {
  event.preventDefault();

  const email = document.getElementById('signin-email').value;
  const password = document.getElementById('signin-password').value;

  const payload = { username: email, password: password };

  try {
    const response = await fetch('http://127.0.0.1:5000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (response.ok) {
      // Login success, you can store the JWT token 
      localStorage.setItem('auth_token', data.token);
      window.location.href = 'dashboard.html'; // Redirect to dashboard 
    } else {
      // Show error message
      document.getElementById('signin-error-message').textContent = data.message;
    }
  } catch (error) {
    document.getElementById('signin-error-message').textContent = 'An error occurred. Please try again.';
  }
});
