// Init Neutralino
//
Neutralino.init();
Neutralino.events.on('windowClose', onWindowClose);
Neutralino.events.on('pingResult', onPingResult);


document.addEventListener('DOMContentLoaded', function () {
    const elems = document.querySelectorAll('select');
    const instances = M.FormSelect.init(elems);
});

function onWindowClose() {
    Neutralino.app.exit();
}

async function onPingResult(e) {
    console.log('DBG RECEIVED: ' + e.detail);

    let msg = document.getElementById('msg');
    msg.innerHTML += e.detail + '<br>';
}

// Init Python Extension
const PYTHON = new PythonExtension(true)

async function existsFile(path) {
    try {
        await Neutralino.filesystem.getStats(path);
        return true;
    } catch (error) {
        return false;
    }
}

async function createAppFolder() {
    const tmp = await Neutralino.os.getPath('config');
    console.log('tmp: ', tmp);
    const folder = tmp + '/.feinstaubsensor';
    console.log('folder: ', folder);

    const exists = await existsFile(folder);
    if(!exists) {
        await Neutralino.filesystem.createDirectory(folder);
        return folder;
    }
    return folder;
}

async function extractFile(destination, filename) {
    const filePath = destination + `/${filename}`;
    console.log('filePath: ', filePath);
    await Neutralino.resources.extractFile(`/extensions/python/${filename}`, filePath);
    return filePath;
}

async function executePythonFile(appFolder, pythonFilePath) {
    console.log(`source ${appFolder}/.venv/bin/activate && python3 ${pythonFilePath}`);
    return Neutralino.os.execCommand(`cd ${appFolder} && source .venv/bin/activate && python3 ${pythonFilePath}`);
}

async function createVenv(appFolder) {
    if(await existsFile(`${appFolder}/.venv`)) {
        return;
    }
    await Neutralino.os.execCommand(`python -m venv ${appFolder}/.venv`);
    await Neutralino.os.execCommand(`chmod +x ${appFolder}/.venv/bin/activate`);
    console.log(`${appFolder}/.venv/bin/pip install -r ${appFolder}/requirements.txt`);
    return Neutralino.os.execCommand(`${appFolder}/.venv/bin/pip install -r ${appFolder}/requirements.txt`);
}

Neutralino.filesystem.getStats(NL_PATH).then((stats) => {
    console.log('stats: ', JSON.stringify(stats));
});
createAppFolder().then(async (appFolder) => {
    console.log('created app folder ', appFolder);
    await extractFile(appFolder, 'requirements.txt');
    await extractFile(appFolder, 'app.py');
    await extractFile(appFolder, 'NeutralinoExtension.py', false);
    await extractFile(appFolder, 'server.py', false);
    await createVenv(appFolder);

    extractFile(appFolder, 'main.py', true).then((pythonFilePath) => {
        console.log('Starting backend');
        executePythonFile(appFolder, pythonFilePath).then((result) => {
            console.log('result: ', JSON.stringify(result));
        });
    });
});
console.log('PYTHON:', JSON.stringify(PYTHON));
PYTHON.run('test', 'Heyho from JS').then((result) => {
    console.log('result: ', JSON.stringify(result));
}).catch((err) => {console.log('err: ', JSON.stringify(err))});