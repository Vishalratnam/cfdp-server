#!/bin/bash
uvicorn server:app --port 8001 &
uvicorn server:app --port 8002 &
uvicorn server:app --port 8003 &
