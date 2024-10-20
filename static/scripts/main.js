function sendMessage() {
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();
    if (message) {
        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                appendMessage(message, 'user-message');
                userInput.value = '';
                appendMessage(data.message, 'bot-message');
            } else {
                window.location.href = ''
            }
        })
        .catch(
            error => {
                console.error('Error:', error);
                window.location.href = '/'
            }
        );
    }
}

function appendMessage(message, className) {
    const chatBody = document.getElementById('chat-body');
    const div = document.createElement('div');
    div.classList.add('message', className);
    div.innerHTML = `<div class="message-text">${message}</div>`;
    chatBody.appendChild(div);
    scrollToBottom(); // Scroll to bottom whenever a message is appended
}

function scrollToBottom() {
    const chatBody = document.getElementById('chat-body');
    chatBody.scrollTop = chatBody.scrollHeight; // Scroll to the bottom
}

function uploadFile() {
    const fileInput = document.getElementById('file-upload');
    const files = fileInput.files;
    if (files.length > 0) {
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                appendMessage(data.message, 'bot-message');
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

function toggleTheme() {
    const body = document.body;
    const themeIcon = document.querySelector('.theme-toggle');
    body.classList.toggle('light-mode');
    themeIcon.classList.toggle('fa-moon');
    themeIcon.classList.toggle('fa-sun');
}

function deleteChat() {
    const chatBody = document.getElementById('chat-body');
    fetch('/clear', {
        method: 'POST',
    })
    .then(response => {
        if (response.ok) {
            chatBody.innerHTML = ''; // Clear chat history
        }
    })
    .catch(error => console.error('Error:', error));    
}

// Add event listener for Enter key press
document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

function logout() {
    fetch('/logout', {
        method: 'POST',
    })
    .then(response => {
        if (response.ok) {
            window.location.href = '/';
        } else {
            alert('Logout failed');
        }
    })
    .catch(error => console.error('Error:', error));
}

// Scroll to bottom on page load
window.onload = scrollToBottom; // Scroll to bottom on page load


function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('error-message');

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
    })
    .then(response => {
        if (response.ok) {
            window.location.href = '/home';
        } else {
            errorMessage.innerText = 'Invalid credentials';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        errorMessage.innerText = 'An error occurred. Please try again.';
    });
}