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

function onDisplayImage(base64Data) {
    let userDisplay = document.getElementById("userDisplay");
    userDisplay.innerHTML = ""; // Clear the current content

    console.log("BASE64test", JSON.stringify(base64Data));
    
    
    // Create an image element
    let imgElement = document.createElement("img");
    
    // Set the source to the base64 data
    // Make sure the base64Data includes the proper prefix if it doesn't already

    // if (!base64Data.startsWith('data:image')) {
    //     imgElement.src = 'data:image/png;base64,' + base64Data;
    // } else {
    //     imgElement.src = base64Data;
    // }
    
    imgElement.src = base64Data;

    // imgElement.alt = altText;

    imgElement.style.maxWidth = "100%"; // Make the image responsive
    
    // Append the image to the userDisplay div
    userDisplay.appendChild(imgElement);
}

document.getElementById("submitFormDataButton").addEventListener("click", function () {
    setFormDataFromHtmlDocument();

    let isYearFormatValid = checkYearFormValidity(startYear, endYear);
    if (!isYearFormatValid) {
        return;
    }

    PYTHON.run("analyze_sensor_wrapper", [startYear, endYear, sensorType, sensorId]);
});

function onAnalyzeSensorWrapperResult(e) {
    let userDisplay = document.getElementById("userDisplay");
    userDisplay.innerHTML += e.detail + '<br>';
}

function onCleanResultWindow(e) {
    let userDisplay = document.getElementById("userDisplay");
    userDisplay.innerHTML = "";
}

Neutralino.events.on("analyzeSensorWrapperResult", onAnalyzeSensorWrapperResult);
Neutralino.events.on("cleanResultWindow", onPingResult);
Neutralino.events.on("displaySensorImage", onDisplayImage);