// Init Neutralino
//
Neutralino.init();
Neutralino.events.on("windowClose", onWindowClose);
Neutralino.events.on("pingResult", onPingResult);



document.addEventListener('DOMContentLoaded', function () {
    const elems = document.querySelectorAll('select');
    const instances = M.FormSelect.init(elems);
});

function onWindowClose() {
    Neutralino.app.exit();
}

async function onPingResult(e) {
    console.log("DBG RECEIVED: " + e.detail );

    let msg = document.getElementById("msg");
    msg.innerHTML += e.detail + '<br>';
}


// Set title
//
(async () => {
    await Neutralino.window.setTitle(`Neutralino PythonExtension ${NL_APPVERSION}`);
})();

// Init Python Extension
const PYTHON = new PythonExtension(true)

async function createTempFolder() {
    const tmp = await Neutralino.os.getPath('config');
    console.log("tmp: ", tmp);
    const folder = tmp + '/.feinstaubsensor';
    console.log("folder: ", folder);
    Neutralino.filesystem.createDirectory(folder).then(() => {}).catch(err => console.error('createTempFolder error', JSON.stringify(err)));
    return folder;
}

async function extractJarFile(destination, pythonFileName) {
    const pythonFilePath = destination + `${pythonFileName}.py`;
    console.log("pythonFilePath: ", pythonFilePath);
    Neutralino.resources.extractFile(`/extensions/python/${pythonFileName}.py`, pythonFilePath).then(value => {
        startBackend(pythonFilePath).then(() => {
            console.log('Backend started');
        }).catch(err => console.error('error', JSON.stringify(err)));
    });
}

async function startBackend(pythonFilePath) {
    console.log('python3 ' + pythonFilePath);
    return Neutralino.os.execCommand('python3 ' + pythonFilePath);
}

createTempFolder().then(tmpFolder => {

    extractJarFile(tmpFolder, 'server').then(appFile => {

    });

});