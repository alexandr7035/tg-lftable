#!/bin/bash

REQ_FILE='requirements.txt'
ENV_NAME='venv'

# Create virtualenv
echo "[!] CREATING VIRTUAL ENVIROMENT"
python3 -m venv "$ENV_NAME"
echo "[!] DONE"

# Install requirements
echo "[!] INSTALL REQUIREMENTS"
"$ENV_NAME"/bin/pip3 install -r "$REQ_FILE"
echo "[!] DONE"
