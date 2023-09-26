const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const WebSocket = require('ws');
const os = require('os');

let ws;
let reconnectInterval = 100; 
const maxReconnectInterval = 3000; 
const reconnectDecay = 1.5;

function connect() {
    ws = new WebSocket('ws://52.33.88.92/ws/');

    ws.onopen = () => {
        reconnectInterval = 1000;
        ws.send(JSON.stringify({ type: 'CLIENT_ID', id: '219194885071175680' }));
        sendToRenderer('ws-open', null);
        console.log('WebSocket Client Connected');
    };

    ws.onmessage = (event) => {
        sendToRenderer('ws-message', event.data);
        const data = JSON.parse(event.data);
        if (data.type === 'SEND_MESSAGE') {
            shell.stdin.write(data.body + '\n');
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

connect();

// Start a new shell process
const shell = spawn('bash');

// Handle shell outputs
shell.stdout.on('data', (data) => {
    sendToRenderer('ws-message', JSON.stringify({type: 'LLM_RESULT', body: data.toString()}));
    ws.send(JSON.stringify({ type: 'LLM_RESULT', body: data.toString() }));
});

shell.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
});

shell.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
});

// Send commands to the shell
shell.stdin.write('export OPENAI_API_KEY="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"\n');
shell.stdin.write('source /Users/msl/src/scratch/.venv/bin/activate\n');
shell.stdin.write('interpreter -y\n');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 1500,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true
        }
    });

    mainWindow.webContents.openDevTools();
    mainWindow.loadFile('index.html');
}

app.on('ready', createWindow);

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', function () {
    if (mainWindow === null) {
        createWindow();
    }
});

app.on('before-quit', () => {
    shell.kill();
});

function sendToRenderer(type, data) {
    mainWindow.webContents.send(type, data);
}