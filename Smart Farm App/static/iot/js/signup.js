document.getElementById('signup-form').addEventListener('submit', async function(event) {
  event.preventDefault();

  
  const email = document.getElementById('signup-email').value;
  const password = document.getElementById('signup-password').value;

  const payload = { username: email, password: password };

  try {
    const response = await fetch('http://127.0.0.1:5000/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (response.ok) {
      // Registration success, you can redirect to the sign-in page
      window.location.href = 'signin.html'; // Redirect to sign in page
    } else {
      // Show error message
      document.getElementById('signup-error-message').textContent = data.message;
    }
  } catch (error) {
    document.getElementById('signup-error-message').textContent = 'An error occurred. Please try again.';
  }
});
