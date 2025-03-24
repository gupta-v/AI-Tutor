document.addEventListener("DOMContentLoaded", function() {
    // Enter key event listener
    document.getElementById("user-input").addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });
});

// Global variable to track listening state
let isListening = false;

function sendMessage() {
    let userInput = document.getElementById("user-input").value.trim();
    if (userInput === "") return;

    let chatBox = document.getElementById("chat-box");

    // Display user message (Right-aligned)
    let userMessage = document.createElement("div");
    userMessage.className = "user-message";
    userMessage.innerHTML = `<strong>You:</strong> ${userInput}`;
    chatBox.appendChild(userMessage);

    // Send request to backend
    fetch("/ask", {
        method: "POST",
        body: JSON.stringify({ query: userInput }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        // Display AI response (Left-aligned)
        let aiMessage = document.createElement("div");
        aiMessage.className = "ai-message";
        aiMessage.innerHTML = `<strong>AI Tutor:</strong> ${data.response}`;
        chatBox.appendChild(aiMessage);
        
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to bottom
    });

    document.getElementById("user-input").value = ""; // Clear input field
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
    fetch("/stop-speech", { method: "POST" })
    .then(() => console.log("Speech output stopped"));
}