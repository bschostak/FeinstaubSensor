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

async function extractPyFile(destination, pythonFileName) {
    const pythonFilePath = destination + `/${pythonFileName}.py`;
    console.log('pythonFilePath: ', pythonFilePath);
    await Neutralino.resources.extractFile(`/extensions/python/${pythonFileName}.py`, pythonFilePath);
    return pythonFilePath;
}

async function startBackend(pythonFilePath) {
    console.log('python3 ' + pythonFilePath);
    return Neutralino.os.execCommand('python3 ' + pythonFilePath);
}

console.log('neu path', NL_PATH);
createAppFolder().then(async (appFolder) => {
    console.log('created app folder ', appFolder);
    await extractPyFile(appFolder, 'app');
    await extractPyFile(appFolder, 'NeutralinoExtension', false);
    await extractPyFile(appFolder, 'server', false);
    extractPyFile(appFolder, 'main', true).then((pythonFilePath) => {
        console.log('Starting backend');
        startBackend(pythonFilePath).then((result) => {
            console.log('result: ', JSON.stringify(result));
        });
    });
});