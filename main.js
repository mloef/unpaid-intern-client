const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const WebSocketClient = require('./websocket');
const OIClient = require('./open-interpreter');

let mainWindow;
const wsClient = new WebSocketClient();
const openai = new OIClient();

ipcMain.on('submit-params', (event, params) => {
    openai.initialize(params.OPENAI_API_KEY, params.VENV_PATH, mainWindow, wsClient);
    wsClient.initSocket(params.CLIENT_ID, openai.getShell(), mainWindow);
});

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

app.on('window-all-closed', app.quit);

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});

app.on('before-quit', () => {
    openai.killShell();
});
