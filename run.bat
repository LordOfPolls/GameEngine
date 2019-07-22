@echo off
echo Verifying python is installed
WHERE python
IF %ERRORLEVEL% NEQ 0 start "" https://www.python.org/ftp/python/3.5.4/python-3.5.4-amd64.exe

echo Checking and installing dependencies
python -m pip install -r requirements.txt --quiet

echo Dependencies should be installed...
echo Booting Game Engine
python main.py