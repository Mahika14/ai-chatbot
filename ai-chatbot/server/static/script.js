document.addEventListener('DOMContentLoaded', () => {
    const sendButton = document.getElementById('send-button');
    const chatInput = document.getElementById('chat-input');
    const chatBox = document.getElementById('chat-box');
    const fileInput = document.getElementById('file-input');
    const stagedFilesArea = document.getElementById('staged-files-area');


    let stagedFiles = [];
    let conversationHistory = [];

    // --- Event listener for when user selects files ---
    fileInput.addEventListener('change', () => {
        stagedFiles.push(...fileInput.files);
        updateStagedFilesUI();
        fileInput.value = '';
    });

    // --- Function to display the names of staged files ---
    function updateStagedFilesUI() {
        stagedFilesArea.innerHTML = '';
        stagedFiles.forEach(file => {
            const fileElement = document.createElement('div');
            fileElement.className = 'staged-file';
            fileElement.textContent = file.name;
            stagedFilesArea.appendChild(fileElement);
        });
    }

    // Main function to handle sending messages ---
    const handleSendMessage = async () => {
        const userQuery = chatInput.value.trim();
        const gdocLink = findGoogleDocLink(userQuery);

        if (!userQuery && stagedFiles.length === 0) return;

        // Display the user's text message only if they actually typed one
        if (userQuery) {
            displayMessage(userQuery, 'user');
        }
        chatInput.value = '';

        if (stagedFiles.length > 0 || gdocLink) {
            displayMessage('<i>Processing documents...</i>', 'ai');
            const formData = new FormData();
            stagedFiles.forEach(file => formData.append('files', file));
            if (gdocLink) {
                formData.append('gdoc_link', gdocLink);
            }
           
            try {
                const uploadResponse = await fetch('/upload', {
                    method: 'POST',
                    body: formData,
                });
                const uploadResult = await uploadResponse.json();

                if (!uploadResponse.ok) {
                    displayMessage(`Error: ${uploadResult.error}`, 'ai');
                    stagedFiles = [];
                    updateStagedFilesUI();
                    return; // Stop if upload fails
                }
                if (!userQuery) {
                    displayMessage('✅ Knowledge base updated. You can now ask questions about the document(s).', 'ai');
                    stagedFiles = [];
                    updateStagedFilesUI();
                    return;
                }

                displayMessage('<i>Knowledge base updated. Now generating response...</i>', 'ai');
                stagedFiles = [];
                updateStagedFilesUI();

            } catch (error) {
                displayMessage('An error occurred during upload.', 'ai');
                return;
            }
        }

        if (!userQuery) return;

        const thikingMessage = displayMessage("<i>Thinking...</i>", 'ai');

        conversationHistory.push({ role: 'user', content: userQuery });
        if (conversationHistory.length > 6) {
            conversationHistory = conversationHistory.slice(-6);
        }

        try {
            const chatResponse = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: userQuery,
                    history: conversationHistory,
                }),
            });
            const chatResult = await chatResponse.json();
            thikingMessage.remove();
            displayMessage(chatResult.response, 'ai');
            conversationHistory.push({ role: 'ai', content: chatResult.response });

        } catch (error) {
            thikingMessage.remove();
            displayMessage('Sorry, an error occurred while getting a response.', 'ai');
        }
    };

    function findGoogleDocLink(text) {
        const gdocPattern = /https:\/\/docs\.google\.com\/document\/d\/[a-zA-Z0-9_-]+/;
        const match = text.match(gdocPattern);
        return match ? match[0] : null;
    }

    sendButton.addEventListener('click', handleSendMessage);
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = (chatInput.scrollHeight) + 'px';
    });

    function displayMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        if (sender === 'ai') {
            messageElement.innerHTML = marked.parse(message);
        } else {
            const p = document.createElement('p');
            p.textContent = message;
            messageElement.appendChild(p);
        }
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;

        return messageElement;
    }
});