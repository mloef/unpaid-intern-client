const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const { ipcMain } = require('electron');
const initSocket = require('./websocket');

let OPENAI_API_KEY;
let CLIENT_ID;
let VENV_PATH;
let ws;

ipcMain.on('submit-params', (event, params) => {
    OPENAI_API_KEY = params.OPENAI_API_KEY;
    CLIENT_ID = params.CLIENT_ID;
    VENV_PATH = params.VENV_PATH;

    startOI();
    ws = initSocket(CLIENT_ID, shell, mainWindow);
});

let shell;
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

app.on('ready', function () {
    createWindow();
});

app.on('window-all-closed', function () {
    app.quit();
});

app.on('activate', function () {
    if (mainWindow === null) {
        createWindow();
    }
});

app.on('before-quit', () => {
    shell.kill();
});

function startOI() {
    // Start a new interpreter instance
    shell = spawn(VENV_PATH, ['-u', './run_interpreter.py'], {
        env: {
            OPENAI_API_KEY: OPENAI_API_KEY
        }
    });

    // Handle shell outputs
    shell.stdout.on('data', (data) => {
        sendToRenderer('ws-message', JSON.stringify({ type: 'LLM_RESULT', body: data.toString() }));
        ws.send(JSON.stringify({ type: 'LLM_RESULT', body: data.toString() }));
    });

    shell.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });

    shell.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
    });
}

function sendToRenderer(type, data) {
    mainWindow.webContents.send(type, data);
}