function checkYearProportion(startYear, endYear) {
    if (startYear > endYear) {
        alert("Start year must be less than or equal to end year.");
        console.log("Start year must be less than or equal to end year.");
        return;
    }
}

function sendSensorDataForChecking() {
    const startYear = document.getElementById("startYear").value;
    const endYear = document.getElementById("endYear").value;
    // const sensorId = document.getElementById("sensorId").value;
    const sensorId = "dht22"; //! Should be deleted when the other sensor is added

    checkYearProportion(startYear, endYear);
}

document.getElementById("submitFormDataButton").addEventListener("click", function () {
    sendSensorDataForChecking();
});