let startYear = 0;
let endYear = 0;
// let sensorId = "";
let sensorId = "dht22"; //! Should be deleted when the other sensor is added

function setFormDataFromHtmlDocument() {
    startYear = document.getElementById("startYear").value;
    endYear = document.getElementById("endYear").value;
    // sensorId = document.getElementById("sensorId").value;
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
    console.log("SEND DATA!");
}

document.getElementById("submitFormDataButton").addEventListener("click", function () {
    setFormDataFromHtmlDocument();

    let isYearFormatValid = checkYearFormValidity(startYear, endYear);
    if (!isYearFormatValid) {
        return;
    }

    sendSensorDataForSensorAnalyze();
});