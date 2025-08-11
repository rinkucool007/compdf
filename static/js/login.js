/* static/js/login.js */

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            // In a real application, you would send these credentials to a server for validation.
            // For this demo, we'll use a simple check.
            if (username === 'admin' && password === 'password') {
                // Simulate a successful login
                document.getElementById('login-screen').classList.add('hidden');
                document.getElementById('landing-page').classList.remove('hidden');
            } else {
                alert('Invalid credentials. Please try again.');
            }
        });
    }

    const forgotPasswordLink = document.getElementById('forgot-password');
    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener('click', function(e) {
            e.preventDefault();
            alert('Password recovery instructions would be sent to your email.');
        });
    }
});
