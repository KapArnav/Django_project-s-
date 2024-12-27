document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const chatBox = document.getElementById("chat-box");
    const queryInput = document.getElementById("query");

    chatForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        
        const query = queryInput.value.trim();
        if (!query) {
            // Create and display error banner
            const errorBanner = document.createElement("div");
            errorBanner.classList.add("error-banner");
            errorBanner.textContent = "Please enter a query.";
            document.body.prepend(errorBanner);

            // Remove the banner after a few seconds
            setTimeout(() => {
                errorBanner.remove();
            }, 3000);

            return;
        }

        // Display user query in the chatbox
        const userMessage = document.createElement("div");
        userMessage.classList.add("message", "user-message");
        userMessage.textContent = query;
        chatBox.appendChild(userMessage);
        queryInput.value = "";

        try {
            const response = await fetch("/chatgpt-chat-api/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ query }),  // Correctly stringify the data
            });

            if (response.ok) {
                const data = await response.json();
                const chatgptMessage = document.createElement("div");
                chatgptMessage.classList.add("message", "chatgpt-message");
                chatgptMessage.textContent = data.message || "No response received.";
                chatBox.appendChild(chatgptMessage);
            } else {
                const errorMessage = document.createElement("div");
                errorMessage.classList.add("message", "error-message");
                errorMessage.textContent = `Error: ${response.statusText}`;
                chatBox.appendChild(errorMessage);
            }
        } catch (error) {
            const errorMessage = document.createElement("div");
            errorMessage.classList.add("message", "error-message");
            errorMessage.textContent = `Error: ${error.message}`;
            chatBox.appendChild(errorMessage);
        }

        // Scroll to the latest message
        chatBox.scrollTop = chatBox.scrollHeight;
    });
});



