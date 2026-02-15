#!/bin/bash
# Set working directory and Python path
export PYTHONPATH=$PWD:$PYTHONPATH
exec python -m uvicorn main:app --host 0.0.0.0 --port $PORT
