const ws = new WebSocket('ws://52.33.88.92/ws/');

const chatDiv = document.getElementById('chat');

ws.onopen = () => {
    chatDiv.innerHTML += `<p>Connected to the server<p>`;
    ws.send(JSON.stringify({ type: 'CLIENT_ID', id: '+12078319547' }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'YOUR_ID') {
        chatDiv.innerHTML += `<p>Your client ID: ${data.id}</p>`;
    } else if (data.type === 'SEND_MESSAGE') {
        chatDiv.innerHTML += `<p>Message for LLM: ${data.body}</p>`;
        const reversedMessage = data.body.split('').reverse().join('');
        ws.send(JSON.stringify({type: "SEND_MESSAGE", body: reversedMessage}));
        chatDiv.innerHTML += `<p>Message from LLM: ${reversedMessage}</p>`;
    } else {
        chatDiv.innerHTML += `<p>Got unknown message: ${event.data}</p>`;
    }
};

ws.onerror = (error) => {
    chatDiv.innerHTML += `WebSocket Error: ` + error;
};

ws.onclose = (event) => {
    chatDiv.innerHTML += 'WebSocket closed with code:' + event.code + ' and reason:' + event.reason;
};