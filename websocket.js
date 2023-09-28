const WebSocket = require('ws');

let ws;
let reconnectInterval = 200;
const maxReconnectInterval = 3000;
const reconnectDecay = 1.5;

let CLIENT_ID;
let SHELL;
let MAIN_WINDOW;

function connect() {
    console.log('Attempting to connect to WebSocket with reconnectInterval: ' + reconnectInterval + 'ms');
    ws = new WebSocket('ws://52.33.88.92/ws/');

    ws.onopen = () => {
        ws.send(JSON.stringify({ type: 'CLIENT_ID', id: CLIENT_ID }));
        sendToRenderer('ws-open', null);
        console.log('WebSocket Client Connected');
    };

    ws.onmessage = (event) => {
        sendToRenderer('ws-message', event.data);
        const data = JSON.parse(event.data);
        if (data.type === 'SEND_MESSAGE') {
            SHELL.stdin.write(data.body + '\n');
        }
    };

    ws.onerror = (error) => {
        console.log('WebSocket Error: ', error);
        reconnectInterval = Math.min(maxReconnectInterval, reconnectInterval * reconnectDecay);
        setTimeout(connect, reconnectInterval);
        sendToRenderer('ws-error', error);
    };

    ws.onclose = (event) => {
        console.log('WebSocket connection closed: ', event.code, event.reason);
        reconnectInterval = Math.min(maxReconnectInterval, reconnectInterval * reconnectDecay);
        setTimeout(connect, reconnectInterval);
        sendToRenderer('ws-close', { code: event.code, reason: event.reason });
    };
}

function sendToRenderer(type, data) {
    MAIN_WINDOW.webContents.send(type, data);
}

function initSocket(client_id, shell, mainWindow) {
    CLIENT_ID = client_id;
    SHELL = shell;
    MAIN_WINDOW = mainWindow;
    connect();
    return ws;
}

module.exports = initSocket;