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
});

function onPopulateYearDropdowns(e) {
    const startYearSelect = document.getElementById('startYear');
    const endYearSelect = document.getElementById('endYear');
    
    startYearSelect.innerHTML = '<option value="" disabled selected>Choose start year</option>';
    endYearSelect.innerHTML = '<option value="" disabled selected>Choose end year</option>';

    let years;
    try {
        const parsedDetail = JSON.parse(e.detail);
        years = Array.isArray(parsedDetail) ? parsedDetail : null;

        // Probably should be refactored...
        if (Array.isArray(years)) {
            years.forEach(year => {
                const startOption = document.createElement('option');
                startOption.value = year;
                startOption.textContent = year;
                
                const endOption = document.createElement('option');
                endOption.value = year;
                endOption.textContent = year;
                
                startYearSelect.appendChild(startOption);
                endYearSelect.appendChild(endOption);
            });
        } else {
            console.error('Could not find years array in event data:', e);
        }
    } catch (error) {
        console.error('Error processing event data:', error, e);
    }
    
    // Reinitialize Materialize select elements
    M.FormSelect.init(startYearSelect);
    M.FormSelect.init(endYearSelect);
}

function onAnalyzeSensorWrapperResult(e) {
    let userDisplay = document.getElementById("userDisplay");
    userDisplay.innerHTML += e.detail + '<br>';
}

function onDisplayImage(e) {
    cleanUserDisplay();

    let imgElement = document.createElement("img");
    imgElement.src = 'data:image/png;base64, ' + e.detail;
    imgElement.style.maxWidth = "100%"; 
    
    userDisplay.appendChild(imgElement);
}

Neutralino.events.on("populateYearDropdowns", onPopulateYearDropdowns);
Neutralino.events.on("analyzeSensorWrapperResult", onAnalyzeSensorWrapperResult);
Neutralino.events.on("displaySensorImage", onDisplayImage);

PYTHON.run("fetch_available_years_wrapper");