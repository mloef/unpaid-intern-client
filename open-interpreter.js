const { spawn } = require('child_process');

class OIClient {
    constructor() {
        this.shell = null;
        this.openaiApiKey = '';
        this.venvPath = '';
        this.mainWindow = null;
        this.wsClient = null;
    }

    initialize(openaiApiKey, venvPath, mainWindow, wsClient) {
        this.openaiApiKey = openaiApiKey;
        this.venvPath = venvPath;
        this.mainWindow = mainWindow;
        this.wsClient = wsClient;
        this.startOI();
    }

    startOI() {
        this.shell = spawn(this.venvPath, ['-u', './run_interpreter.py'], {
            env: {
                OPENAI_API_KEY: this.openaiApiKey
            }
        });

        this.shell.stdout.on('data', (data) => {
            this.mainWindow.webContents.send('ws-message', JSON.stringify({ type: 'LLM_RESULT', body: data.toString() }));
            this.wsClient.send(JSON.stringify({ type: 'LLM_RESULT', body: data.toString() }));
        });

        this.shell.stderr.on('data', (data) => {
            console.error(`stderr: ${data}`);
        });

        this.shell.on('close', (code) => {
            console.log(`child process exited with code ${code}`);
        });
    }

    killShell() {
        if (this.shell) {
            this.shell.kill();
        }
    }

    getShell() {
        return this.shell;
    }
}

module.exports = OIClient;