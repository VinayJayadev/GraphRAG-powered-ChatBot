@echo off
REM Batch script to start the backend server on Windows
cd /d "%~dp0"

echo Current directory: %CD%
echo.
echo Starting backend server...
echo Server will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Use the start.py script which handles Python path correctly
python start.py

pause
