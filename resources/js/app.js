let startYear = 0;
let endYear = 0;
// let sensorType = "";
let sensorType = "dht22"; //! Should be deleted when the other sensor is added
let sensorId = "4594"; //TODO: Make error message when sensorId is not set

function setFormDataFromHtmlDocument() {
    startYear = document.getElementById("startYear").value;
    endYear = document.getElementById("endYear").value;
    sensorId = document.getElementById("sensorId").value;
}

function checkYearFormValidity(startYear, endYear) {
    if (startYear > endYear) {
        alert("Start year must be less than or equal to end year.");
        return false;
    } else if (startYear == 0 || endYear == 0) {
        alert("Start year and end year must be set.");
        return false;
    } else {
        return true;
    }
}

function cleanUserDisplay() {
    let userDisplay = document.getElementById("userDisplay");
    userDisplay.innerHTML = "";
}

function onDisplayImage(e) {
    cleanUserDisplay();

    let imgElement = document.createElement("img");
    imgElement.src = 'data:image/png;base64, ' + e.detail;
    imgElement.style.maxWidth = "100%"; 
    
    userDisplay.appendChild(imgElement);
}

function playNotificationSound() {
    // if (!audio) {
    //     audio = new Audio('./resources/sounds/notification.mp3'); // Path to your sound file
    //     document.getElementById("userDisplay").innerHTML = "Sound is playing...";
    // }
    
    //TODO: make as base64
    audio = new Audio('/resources/sounds/notification.mp3');

    document.getElementById("userDisplay").innerHTML = "Sound is playing...";

    if (audio.paused || audio.ended) {
        audio.play();
    } else {
        audio.pause();
        audio.currentTime = 0;
    }
}

document.getElementById("submitFormDataButton").addEventListener("click", function () {
    cleanUserDisplay();

    setFormDataFromHtmlDocument();

    let isYearFormatValid = checkYearFormValidity(startYear, endYear);
    if (!isYearFormatValid) {
        return;
    }

    PYTHON.run("analyze_sensor_wrapper", [startYear, endYear, sensorType, sensorId]);
});

document.getElementById("deleteDownloadedSensorDataButton").addEventListener("click", function () {
    cleanUserDisplay();

    PYTHON.run("delete_sensor_data_files_wrapper");
    playNotificationSound();
});

function onAnalyzeSensorWrapperResult(e) {
    let userDisplay = document.getElementById("userDisplay");
    userDisplay.innerHTML += e.detail + '<br>';
}

Neutralino.events.on("analyzeSensorWrapperResult", onAnalyzeSensorWrapperResult);
Neutralino.events.on("displaySensorImage", onDisplayImage);