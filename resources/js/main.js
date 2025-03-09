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
