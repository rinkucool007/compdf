/* static/js/app.js */

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const loginScreen = document.getElementById('login-screen');
    const landingPage = document.getElementById('landing-page');
    const singlePdfScreen = document.getElementById('single-pdf-screen');
    const progressScreen = document.getElementById('progress-screen');
    const resultsScreen = document.getElementById('results-screen');
    const singlePdfBtn = document.getElementById('single-pdf-btn');
    const backFromSingle = document.getElementById('back-from-single');
    const backFromProgress = document.getElementById('back-from-progress');
    const backFromResults = document.getElementById('back-from-results');
    const compareSingleBtn = document.getElementById('compare-single-btn');
    const logoutBtns = document.querySelectorAll('[id^="logout-btn"]');
    const terminalOutput = document.getElementById('terminal-output');
    const pdfViewer = document.getElementById('pdf-viewer');
    const downloadPdfBtn = document.getElementById('download-pdf');

    // File inputs
    const file1Input = document.getElementById('file-1');
    const file2Input = document.getElementById('file-2');
    const file1Preview = document.getElementById('file-1-preview');
    const file2Preview = document.getElementById('file-2-preview');

    // Chatbot elements
    const chatbotToggles = document.querySelectorAll('[id^="chatbot-toggle"]');
    const chatbotWindows = document.querySelectorAll('[id^="chatbot-window"]');
    const closeChatbotBtns = document.querySelectorAll('[id^="close-chatbot"]');
    const chatbotMessages = document.querySelectorAll('[id^="chatbot-messages"]');
    const chatbotInputs = document.querySelectorAll('[id^="chatbot-input"]');

    // Navigation
    if (singlePdfBtn) {
        singlePdfBtn.addEventListener('click', () => {
            landingPage.classList.add('hidden');
            singlePdfScreen.classList.remove('hidden');
        });
    }

    if (backFromSingle) {
        backFromSingle.addEventListener('click', () => {
            singlePdfScreen.classList.add('hidden');
            landingPage.classList.remove('hidden');
        });
    }

    if (backFromProgress) {
        backFromProgress.addEventListener('click', () => {
            progressScreen.classList.add('hidden');
            singlePdfScreen.classList.remove('hidden');
        });
    }

    if (backFromResults) {
        backFromResults.addEventListener('click', () => {
            resultsScreen.classList.add('hidden');
            landingPage.classList.remove('hidden');
        });
    }

    // Logout
    logoutBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('div[id$="-screen"], #landing-page').forEach(screen => {
                screen.classList.add('hidden');
            });
            loginScreen.classList.remove('hidden');
            document.getElementById('username').value = '';
            document.getElementById('password').value = '';
        });
    });

    // File Previews
    if (file1Input) {
        file1Input.addEventListener('change', function() {
            if (this.files.length > 0) {
                document.getElementById('file-1-name').textContent = this.files[0].name;
                file1Preview.classList.remove('hidden');
            } else {
                file1Preview.classList.add('hidden');
            }
        });
    }

    if (file2Input) {
        file2Input.addEventListener('change', function() {
            if (this.files.length > 0) {
                document.getElementById('file-2-name').textContent = this.files[0].name;
                file2Preview.classList.remove('hidden');
            } else {
                file2Preview.classList.add('hidden');
            }
        });
    }

    // Drag & Drop
    function setupDragAndDrop(dropZone, inputElement) {
        if (!dropZone || !inputElement) return;
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(e => {
            dropZone.addEventListener(e, e => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });

        dropZone.addEventListener('dragover', () => {
            dropZone.classList.add('border-blue-500');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('border-blue-500');
        });

        dropZone.addEventListener('drop', e => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                inputElement.files = files;
                const event = new Event('change');
                inputElement.dispatchEvent(event);
            }
            dropZone.classList.remove('border-blue-500');
        });
    }

    setupDragAndDrop(document.getElementById('drop-zone-1'), file1Input);
    setupDragAndDrop(document.getElementById('drop-zone-2'), file2Input);

    // Real Comparison Function (calls backend)
    if (compareSingleBtn) {
        compareSingleBtn.addEventListener('click', function() {
            if (!file1Input.files[0] || !file2Input.files[0]) {
                alert('Please select both PDF files to compare.');
                return;
            }

            const formData = new FormData();
            formData.append('file1', file1Input.files[0]);
            formData.append('file2', file2Input.files[0]);

            singlePdfScreen.classList.add('hidden');
            progressScreen.classList.remove('hidden');
            terminalOutput.innerHTML = '<div class="terminal-line">Uploading files...</div>';

            fetch('/compare', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) throw new Error('Network error');
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    terminalOutput.innerHTML += `<div class="terminal-line">❌ Error: ${data.error}</div>`;
                    setTimeout(() => alert("Error: " + data.error), 1000);
                    return;
                }

                terminalOutput.innerHTML += `<div class="terminal-line">✅ Comparison completed!</div>`;
                setTimeout(() => {
                    progressScreen.classList.add('hidden');
                    resultsScreen.classList.remove('hidden');
                    pdfViewer.src = data.result_url;
                    downloadPdfBtn.onclick = () => {
                        const a = document.createElement('a');
                        a.href = data.result_url;
                        a.download = 'comparison_result.pdf';
                        a.click();
                    };
                }, 1000);
            })
            .catch(err => {
                terminalOutput.innerHTML += `<div class="terminal-line">❌ Network error: ${err.message}</div>`;
                setTimeout(() => alert("Failed to connect. Is the server running?"), 1000);
            });
        });
    }

    // Logo Home
    document.querySelectorAll('[id^="logo-home"]').forEach(logo => {
        logo.addEventListener('click', () => {
            document.querySelectorAll('div[id$="-screen"]').forEach(s => s.classList.add('hidden'));
            landingPage.classList.remove('hidden');
        });
    });

    // Chatbot
    chatbotToggles.forEach((toggle, i) => {
        toggle.addEventListener('click', () => {
            chatbotWindows[i].style.display = chatbotWindows[i].style.display === 'flex' ? 'none' : 'flex';
        });
    });

    closeChatbotBtns.forEach((btn, i) => {
        btn.addEventListener('click', () => {
            chatbotWindows[i].style.display = 'none';
        });
    });

    chatbotInputs.forEach((input, i) => {
        input.addEventListener('keypress', e => {
            if (e.key === 'Enter' && input.value.trim()) {
                const msg = input.value.trim();
                input.value = '';
                const userDiv = document.createElement('div');
                userDiv.className = 'message user mb-2 flex justify-end';
                userDiv.innerHTML = `<div class="text-sm bg-blue-100 p-2 rounded">${msg}</div>`;
                chatbotMessages[i].appendChild(userDiv);

                setTimeout(() => {
                    const botDiv = document.createElement('div');
                    botDiv.className = 'message bot mb-2';
                    botDiv.innerHTML = `<div class="text-sm bg-gray-100 p-2 rounded">Thanks for your message. I'm a demo assistant.</div>`;
                    chatbotMessages[i].appendChild(botDiv);
                    chatbotMessages[i].scrollTop = chatbotMessages[i].scrollHeight;
                }, 500);
                chatbotMessages[i].scrollTop = chatbotMessages[i].scrollHeight;
            }
        });
    });
});
