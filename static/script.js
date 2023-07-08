document.getElementById('login-form').addEventListener('submit', login);

function login(event) {
  event.preventDefault(); // Prevent the form from submitting

  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');

  const username = usernameInput.value;
  const password = passwordInput.value;

  // Send a request to the server to handle the login
  fetch('/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username, password })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Login successful
      window.location.href = '/tasks';
    } else {
      // Login failed
      displayErrorMessage(data.message);
      clearInputs();
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}

function displayErrorMessage(message) {
  const errorElement = document.getElementById('error-message');
  errorElement.textContent = message;
  errorElement.style.display = 'block'; // Show the error message
}

function clearInputs() {
  document.getElementById('username').value = '';
  document.getElementById('password').value = '';
}
