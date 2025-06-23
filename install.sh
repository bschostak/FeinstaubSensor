#!/bin/bash
echo "Building..."
neu build
USER_DATA_PATH="${XDG_DATA_HOME:-$HOME/.local/share}"
DATA_PATH="${USER_DATA_PATH}/feinstaubsensor"
VENV_PATH="${DATA_PATH}/.venv"

echo "Creating venv at ${VENV_PATH}"
python -m venv "${VENV_PATH}"

echo "Activating venv"
source "${VENV_PATH}/bin/activate"

echo "Installing requirements"
pip install -r requirements.txt

echo "Copying files to ${DATA_PATH}"
cp -rfv dist/feinstaubsensor/* "${DATA_PATH}"
cp -rfv installer/* "${DATA_PATH}"
cp -rfv sensor_data/ "${DATA_PATH}"
echo "Icon=${DATA_PATH}/favicon.png" >> "${DATA_PATH}/feinstaubsensor.desktop"
echo "Exec=${DATA_PATH}/runner.sh" >> "${DATA_PATH}/feinstaubsensor.desktop"
chmod +x "${DATA_PATH}/runner.sh"

echo "Copying desktop file to ${USER_DATA_PATH}/applications/feinstaubsensor.desktop"
cp -fv "${DATA_PATH}/feinstaubsensor.desktop" "${USER_DATA_PATH}/applications/feinstaubsensor.desktop"

echo "Installation complete"