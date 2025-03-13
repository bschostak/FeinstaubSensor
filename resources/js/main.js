document.addEventListener('DOMContentLoaded', function () {
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems);
});

function onWindowClose() {
    Neutralino.app.exit();
}

async function onPingResult(e) {
    console.log("DBG RECEIVED: " + e.detail );

    let msg = document.getElementById("msg");
    msg.innerHTML += e.detail + '<br>';
}

//! Work in progress... (Should be deleted in the future)

// function onAnalyzeSensorWrapperResult(e) {
//     console.log("DBG RECEIVED: " + e.detail);
//     let msg = document.getElementById("msg");
//     msg.innerHTML += e.detail + '<br>';
// }

// Init Neutralino
//
Neutralino.init();
Neutralino.events.on("windowClose", onWindowClose);
Neutralino.events.on("pingResult", onPingResult);


//* App Event result handlers (Should be deleted in the future)
// Neutralino.events.on("analyzeSensorWrapperResult", onAnalyzeSensorWrapperResult);

// Set title
//
(async () => {
    await Neutralino.window.setTitle(`Neutralino PythonExtension ${NL_APPVERSION}`);
})();

// Init Python Extension
const PYTHON = new PythonExtension(true)
