document.addEventListener("DOMContentLoaded", function() {
    // Enter key event listener
    document.getElementById("user-input").addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });

    // Clear session when page is refreshed or loaded
    clearSession();
});

// Global variables
let isListening = false;

// Function to clear session on page load/refresh
function clearSession() {
    fetch("/clear-session", {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        console.log("Session cleared:", data.message);
        // Reset RAG status indicator
        updateRagStatus(false);
    })
    .catch(error => {
        console.error("Error clearing session:", error);
    });
}

function displayFileNames(files) {
    const chatBox = document.getElementById("chat-box");
    const fileNameDisplay = document.createElement("div");
    fileNameDisplay.className = "file-name-display";
    
    const fileNames = Array.from(files).map(file => file.name).join(", ");
    fileNameDisplay.innerHTML = `<strong>AI Tutor:</strong> Loading documents: ${fileNames}`;
    chatBox.appendChild(fileNameDisplay);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function handleFileUpload(files) {
    if (!files || files.length === 0) return;

    // Display file names in chat
    displayFileNames(files);

    // Display initializing message
    const chatBox = document.getElementById("chat-box");
    const initializingMessage = document.createElement("div");
    initializingMessage.className = "ai-message";
    initializingMessage.innerHTML = `<strong>AI Tutor:</strong> Initializing RAG system with documents...`;
    chatBox.appendChild(initializingMessage);
    chatBox.scrollTop = chatBox.scrollHeight;

    // Show loading indicator
    document.getElementById("loading-indicator").classList.remove("hidden");

    const formData = new FormData();
    Array.from(files).forEach(file => {
        formData.append('files', file);
    });

    fetch("/initialize-rag", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Hide loading indicator
        document.getElementById("loading-indicator").classList.add("hidden");
        
        const chatBox = document.getElementById("chat-box");
        const ragMessage = document.createElement("div");
        ragMessage.className = "ai-message";

        if (data.success) {
            ragMessage.innerHTML = `<strong>AI Tutor:</strong> ✅ RAG initialized successfully! You can now ask questions about the uploaded documents.`;
            updateRagStatus(true);
        } else {
            ragMessage.innerHTML = `<strong>AI Tutor:</strong> ❌ Failed to initialize RAG. Falling back to standard response generation.`;
            updateRagStatus(false);
        }

        chatBox.appendChild(ragMessage);
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
        // Hide loading indicator
        document.getElementById("loading-indicator").classList.add("hidden");
        
        console.error("RAG initialization error:", error);
        
        const chatBox = document.getElementById("chat-box");
        const errorMessage = document.createElement("div");
        errorMessage.className = "ai-message";
        errorMessage.innerHTML = `<strong>AI Tutor:</strong> ❌ Error initializing RAG. Falling back to standard response generation.`;
        chatBox.appendChild(errorMessage);
        chatBox.scrollTop = chatBox.scrollHeight;
        
        updateRagStatus(false);
    });
}

function handleFolderUpload(files) {
    if (!files || files.length === 0) return;

    // Display folder name in chat
    const folderName = files[0].webkitRelativePath.split('/')[0];
    const chatBox = document.getElementById("chat-box");
    const folderNameDisplay = document.createElement("div");
    folderNameDisplay.className = "file-name-display";
    folderNameDisplay.innerHTML = `<strong>AI Tutor:</strong> Loading documents from folder: ${folderName}`;
    chatBox.appendChild(folderNameDisplay);
    chatBox.scrollTop = chatBox.scrollHeight;

    // Display initializing message
    const initializingMessage = document.createElement("div");
    initializingMessage.className = "ai-message";
    initializingMessage.innerHTML = `<strong>AI Tutor:</strong> Initializing RAG system with folder documents...`;
    chatBox.appendChild(initializingMessage);
    chatBox.scrollTop = chatBox.scrollHeight;

    // Show loading indicator
    document.getElementById("loading-indicator").classList.remove("hidden");

    // Get the first file's webkitRelativePath to extract the folder
    const folderPath = files[0].webkitRelativePath.split('/')[0];

    const formData = new FormData();
    formData.append('folder', folderPath);

    fetch("/initialize-rag", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Hide loading indicator
        document.getElementById("loading-indicator").classList.add("hidden");
        
        const ragMessage = document.createElement("div");
        ragMessage.className = "ai-message";

        if (data.success) {
            ragMessage.innerHTML = `<strong>AI Tutor:</strong> ✅ RAG initialized successfully with folder documents! You can now ask questions about the uploaded documents.`;
            updateRagStatus(true);
        } else {
            ragMessage.innerHTML = `<strong>AI Tutor:</strong> ❌ Failed to initialize RAG. Falling back to standard response generation.`;
            updateRagStatus(false);
        }

        chatBox.appendChild(ragMessage);
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
        // Hide loading indicator
        document.getElementById("loading-indicator").classList.add("hidden");
        
        console.error("RAG initialization error:", error);
        
        const errorMessage = document.createElement("div");
        errorMessage.className = "ai-message";
        errorMessage.innerHTML = `<strong>AI Tutor:</strong> ❌ Error initializing RAG. Falling back to standard response generation.`;
        chatBox.appendChild(errorMessage);
        chatBox.scrollTop = chatBox.scrollHeight;
        
        updateRagStatus(false);
    });
}

function updateRagStatus(isActive) {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-text');
    
    if (isActive) {
        statusDot.classList.remove('inactive');
        statusDot.classList.add('active');
        statusText.textContent = 'PDFs loaded - RAG enabled';
    } else {
        statusDot.classList.remove('active');
        statusDot.classList.add('inactive');
        statusText.textContent = 'No PDFs loaded';
    }
}

function sendMessage() {
    let userInput = document.getElementById("user-input").value.trim();
    if (userInput === "") return;

    let chatBox = document.getElementById("chat-box");

    // Display user message (Right-aligned)
    let userMessage = document.createElement("div");
    userMessage.className = "user-message";
    userMessage.innerHTML = `<strong>You:</strong> ${userInput}`;
    chatBox.appendChild(userMessage);
    
    // Show thinking message
    let thinkingMessage = document.createElement("div");
    thinkingMessage.className = "ai-message thinking";
    thinkingMessage.innerHTML = `<strong>AI Tutor:</strong> <em>Thinking...</em>`;
    chatBox.appendChild(thinkingMessage);
    
    chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to bottom

    // Send request to backend
    fetch("/ask", {
        method: "POST",
        body: JSON.stringify({ query: userInput }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        // Remove thinking message
        chatBox.removeChild(thinkingMessage);
        
        // Display AI response (Left-aligned)
        let aiMessage = document.createElement("div");
        aiMessage.className = "ai-message";
        aiMessage.innerHTML = `<strong>AI Tutor:</strong> ${data.response}`;
        chatBox.appendChild(aiMessage);
        
        // If there was retrieval info and we want to show it
        if (data.hasRetrieval && data.retrieved) {
            let retrievalInfo = document.createElement("div");
            retrievalInfo.className = "retrieval-info";
            retrievalInfo.innerHTML = `<details>
                <summary>📚 View retrieved information</summary>
                <div class="retrieved-content">${data.retrieved}</div>
            </details>`;
            chatBox.appendChild(retrievalInfo);
        }
        
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to bottom
    })
    .catch(error => {
        // Remove thinking message
        chatBox.removeChild(thinkingMessage);
        
        // Display error message
        let errorMessage = document.createElement("div");
        errorMessage.className = "ai-message error";
        errorMessage.innerHTML = `<strong>AI Tutor:</strong> Sorry, I encountered an error processing your request. Please try again.`;
        chatBox.appendChild(errorMessage);
        
        console.error("Error sending message:", error);
    });

    document.getElementById("user-input").value = ""; // Clear input field
}

function toggleVoiceInput() {
    if (isListening) {
        stopListening();
    } else {
        startVoiceInput();
    }
}

function startVoiceInput() {
    let popup = document.getElementById("listening-popup");
    let micButton = document.querySelector(".mic-button");

    // Toggle listening state
    if (isListening) {
        // If already listening, stop it
        stopListening();
        
        // Call backend to stop listening process
        fetch("/stop-listening", { method: "POST" })
        .then(() => console.log("Speech recognition stopped by user"));
        
        return;
    }
    
    // Start listening
    isListening = true;
    micButton.classList.add("active");
    popup.classList.remove("hidden");
    
    // Show the listening popup with waves
    document.getElementById("listening-text").textContent = "Listening...";
    
    fetch("/speech-to-text", { method: "POST" })
    .then(response => response.json())
    .then(data => {
        // Stop listening state
        stopListening();
        
        // Update input field with recognized text
        document.getElementById("user-input").value = data.query;
        
        // If we got valid text, send the message
        if (data.query && data.query.trim() !== "") {
            sendMessage();
        }
    })
    .catch(error => {
        console.error("Speech recognition error:", error);
        stopListening();
    });
}

function stopListening() {
    let popup = document.getElementById("listening-popup");
    let micButton = document.querySelector(".mic-button");
    
    isListening = false;
    micButton.classList.remove("active");
    popup.classList.add("hidden");
}


function stopSpeech() {
    // Visual feedback that the button was clicked
    const stopButton = document.querySelector('.stop-button');
    const originalContent = stopButton.innerHTML;
    stopButton.disabled = true;
    stopButton.style.backgroundColor = '#ffc107';
    stopButton.innerHTML = '⏱ Stopping...';
    
    // Make multiple attempts to stop the speech
    function attemptStopSpeech(attempts = 3) {
        fetch("/stop-speech", { 
            method: "POST",
            headers: { "Cache-Control": "no-cache" }  // Prevent caching
        })
        .then(response => response.json())
        .then(data => {
            console.log("Stop speech response:", data);
            
            if (data.success) {
                stopButton.style.backgroundColor = '#28a745';
                stopButton.innerHTML = '✓ Stopped';
                
                setTimeout(() => {
                    stopButton.disabled = false;
                    stopButton.style.backgroundColor = '#dc3545';
                    stopButton.innerHTML = originalContent;
                }, 1000);
            } 
            else if (attempts > 1) {
                // Try again
                console.log(`Speech stop attempt failed, trying again. ${attempts-1} attempts remaining`);
                setTimeout(() => attemptStopSpeech(attempts - 1), 500);
            }
            else {
                console.warn("Failed to stop speech after multiple attempts");
                stopButton.disabled = false;
                stopButton.style.backgroundColor = '#dc3545';
                stopButton.innerHTML = originalContent;
                
                // Last resort: reload the page
                if (confirm("Unable to stop speech. Would you like to reload the page to stop it?")) {
                    window.location.reload();
                }
            }
        })
        .catch(error => {
            console.error("Error stopping speech:", error);
            stopButton.disabled = false;
            stopButton.style.backgroundColor = '#dc3545';
            stopButton.innerHTML = originalContent;
        });
    }
    
    attemptStopSpeech();
}

function handleTextareaInput(event) {
    // Allow for shift+enter to create a new line without submitting
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
    
    // Auto-resize the textarea
    const textarea = event.target;
    textarea.style.height = "auto";
    const newHeight = Math.min(textarea.scrollHeight, 150); // Max height of 150px
    textarea.style.height = newHeight + "px";
}

// Welcome message on page load
window.onload = function() {
    setTimeout(() => {
        const chatBox = document.getElementById("chat-box");
        const welcomeMessage = document.createElement("div");
        welcomeMessage.className = "ai-message";
        const welcomeText = "Hello! I'm your AI tutor. You can ask me questions directly, or upload PDF documents using the buttons below to get document-specific answers. How can I help you today?";
        welcomeMessage.innerHTML = `<strong>AI Tutor:</strong> ${welcomeText}`;
        chatBox.appendChild(welcomeMessage);
        
        // Send welcome message for speech synthesis
        fetch("/text-to-speech", {
            method: "POST",
            body: JSON.stringify({ text: welcomeText }),
            headers: { "Content-Type": "application/json" }
        })
        .then(response => response.json())
        .then(data => console.log("Welcome message spoken"))
        .catch(error => console.error("Error speaking welcome message:", error));
    }, 500);
}