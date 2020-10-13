#!/usr/bin/bash
sudo apt install -y virtualenv
virtualenv -p python3 venv
. ./venv/bin/activate
pip install -r requirements.txt