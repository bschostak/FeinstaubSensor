let startYear = 0;
let endYear = 0;
// let sensorType = "";
let sensorType = "dht22"; //! Should be deleted when the other sensor is added
let sensorId = "4594"; //TODO: Make error message when sensorId is not set

const notificationSound = new Audio("../assets/notification.mp3");
notificationSound.preload = "auto";

function setFormDataFromHtmlDocument() {
    startYear = document.getElementById("startYear").value;
    endYear = document.getElementById("endYear").value;
    sensorId = document.getElementById("sensorId").value;
}

function checkYearFormValidity(startYear, endYear) {
    if (startYear > endYear) {
        alert("Start year must be less than or equal to end year.");
        return false;
    } else if (startYear === 0 || endYear === 0) {
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

function playNotificationSound() {

    if (!document.querySelector('input[class="notification_sound"]').checked) {
        return;
    }

    const playPromise = notificationSound.play();

    if (playPromise !== undefined) {
        playPromise
            .then(() => {
            })
            .catch(error => {
                console.log('Audio playback was prevented due to browser autoplay policy. This is normal before user interaction.');
            });
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

    playNotificationSound();

    PYTHON.run("delete_sensor_data_files_wrapper");
});

document.getElementById("cancelDownloadDataButton").addEventListener("click", function () {

    PYTHON.run("stop_download_wrapper");
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

function isBase64(str) {
    try {
        return btoa(atob(str)) === str;
    } catch (err) {
        return false;
    }
}

function onDisplayHtml(e) {

    let userDisplay = document.getElementById("userDisplay");

    cleanUserDisplay();

    const htmlContent = e.detail;

    const iframe = document.createElement('iframe');
    iframe.style.width = '100%';
    iframe.style.height = '100%';
    iframe.style.border = 'none';

    if (typeof htmlContent === 'string' &&
        (htmlContent.startsWith('data:text/html;base64,') || isBase64(htmlContent))) {

        iframe.src = `data:text/html;base64,${htmlContent}`;
    } else {
        userDisplay.innerHTML = "Could not display html content.";
        return;
    }

    playNotificationSound();

    userDisplay.appendChild(iframe);
}

Neutralino.events.on("populateYearDropdowns", onPopulateYearDropdowns);
Neutralino.events.on("analyzeSensorWrapperResult", onAnalyzeSensorWrapperResult);
Neutralino.events.on("displaySensorHtml", onDisplayHtml);

PYTHON.run("fetch_available_years_wrapper");
