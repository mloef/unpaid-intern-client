const WebSocket = require('ws');

class WebSocketClient {
    constructor() {
        this.ws = null;
        this.reconnectInterval = 200;
        this.maxReconnectInterval = 3000;
        this.reconnectDecay = 1.5;

        this.clientId = null;
        this.oiClient = null;
        this.mainWindow = null;
    }

    connect() {
        console.log(`Attempting to connect to WebSocket with reconnectInterval: ${this.reconnectInterval}ms`);
        this.ws = new WebSocket('ws://52.33.88.92/ws/');

        this.ws.onopen = () => {
            this.ws.send(JSON.stringify({ type: 'CLIENT_ID', id: this.clientId }));
            this.sendToRenderer('ws-open', null);
            console.log('WebSocket Client Connected');
        };

        this.ws.onmessage = (event) => {
            this.sendToRenderer('ws-message', event.data);
            const data = JSON.parse(event.data);
            if (data.type === 'SEND_MESSAGE' && data.body === 'reset') {
                this.oiClient.restartShell();
                this.ws.send(JSON.stringify({ type: 'LLM_RESULT', body: 'that intern did not receive a return offer :(' }));
            }
            else if (data.type === 'SEND_MESSAGE') {
                this.oiClient.getShell().stdin.write(data.body + '\n');
            }
        };

        this.ws.onerror = (error) => {
            console.log('WebSocket Error: ', error);
            this.reconnectInterval = Math.min(this.maxReconnectInterval, this.reconnectInterval * this.reconnectDecay);
            setTimeout(() => this.connect(), this.reconnectInterval);
            this.sendToRenderer('ws-error', error);
        };

        this.ws.onclose = (event) => {
            console.log('WebSocket connection closed: ', event.code, event.reason);
            this.reconnectInterval = Math.min(this.maxReconnectInterval, this.reconnectInterval * this.reconnectDecay);
            setTimeout(() => this.connect(), this.reconnectInterval);
            this.sendToRenderer('ws-close', { code: event.code, reason: event.reason });
        };
    }

    initSocket(clientId, oiClient, mainWindow) {
        this.clientId = clientId;
        this.oiClient = oiClient;
        this.mainWindow = mainWindow;
        this.connect();
    }

    send(message) {
        if (this.ws) {
            this.ws.send(message);
        } else {
            console.error("WebSocket not initialized");
            setTimeout(() => this.send(message), 1000);
        }
    }

    sendToRenderer(type, data) {
        this.mainWindow.webContents.send(type, data);
    }
}

module.exports = WebSocketClient;