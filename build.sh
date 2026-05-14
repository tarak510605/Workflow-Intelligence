#!/bin/bash
python -m pip install --upgrade 'pip>=26.0'
python -m pip install --only-binary :all: -r requirements.txt
