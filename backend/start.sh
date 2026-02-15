#!/bin/bash
cd /opt/render/project/src/backend
export PYTHONPATH=/opt/render/project/src/backend:$PYTHONPATH
exec python -m uvicorn main:app --host 0.0.0.0 --port $PORT
