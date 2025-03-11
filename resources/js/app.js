let startYear = 0;
let endYear = 0;
// let sensorType = "";
let sensorType = "dht22"; //! Should be deleted when the other sensor is added
let sensorId = ""; 

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

function sendSensorDataForSensorAnalyze() {
    PYTHON.run("analyze_sensor_wrapper", [startYear, endYear, sensorType, sensorId]);
}

function onAnalyzeSensorWrapperResult(e) {
    console.log("DBG RECEIVED: " + e.detail);
    let msg = document.getElementById("msg");
    msg.innerHTML += e.detail + '<br>';
}

document.getElementById("submitFormDataButton").addEventListener("click", function () {
    setFormDataFromHtmlDocument();

    let isYearFormatValid = checkYearFormValidity(startYear, endYear);
    if (!isYearFormatValid) {
        return;
    }

    sendSensorDataForSensorAnalyze();
});