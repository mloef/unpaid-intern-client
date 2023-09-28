function startOI(venv_path, openai_api_key) {
    // Start a new interpreter instance
    shell = spawn(venv_path, ['-u', './run_interpreter.py'], {
        env: {
            OPENAI_API_KEY: openai_api_key,
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