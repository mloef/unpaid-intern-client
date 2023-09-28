const chatDiv = document.getElementById('chat');

// Listen for events from main process
window.electronAPI.receive('ws-open', () => {
    chatDiv.innerHTML += `<p>Connected to the server<p>`;
});

window.electronAPI.receive('ws-message', (data) => {
    data = JSON.parse(data);
    if (data.type === 'YOUR_ID') {
        chatDiv.innerHTML += `<p>Your client ID: ${data.id}</p>`;
    } else if (data.type === 'SEND_MESSAGE') {
        chatDiv.innerHTML += `<p>Message for LLM: ${data.body}</p>`;
    } else if (data.type === 'LLM_RESULT') {
        chatDiv.innerHTML += `<p>Message from LLM: ${data.body.toString()}</p>`;
    } else {
        chatDiv.innerHTML += `<p>Got unknown message: ${JSON.stringify(data)}</p>`;
    }
});

window.electronAPI.receive('ws-error', (error) => {
    chatDiv.innerHTML += `WebSocket Error: ` + error;
});

window.electronAPI.receive('ws-close', (data) => {
    chatDiv.innerHTML += 'WebSocket closed with code:' + data.code + ' and reason:' + data.reason;
});
