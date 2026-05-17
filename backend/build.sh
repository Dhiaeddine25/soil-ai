#!/bin/bash
cd ..
pip install --upgrade pip setuptools wheel
pip install --no-cache-dir --only-binary :all: -r requirements.txt
