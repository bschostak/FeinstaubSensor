#!/bin/bash
DATA_PATH="${XDG_DATA_HOME:-$HOME/.local/share/feinstaubsensor}"
VENV_PATH="${DATA_PATH}/.venv"
source "${VENV_PATH}/bin/activate"
export WEBKIT_DISABLE_DMABUF_RENDERER=1
cd "${DATA_PATH}" || exit
./ext-python-linux_x64
