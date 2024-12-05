@echo off
REM Specify paths
set SCRIPT=main.py
set ICON=logo.ico
set ADDITIONAL_FILES=Additional_files
set OUTPUT_DIR=dist

REM Check if PyInstaller is installed
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller is not installed. Installing now...
    pip install pyinstaller
)

REM Build the executable
pyinstaller --onefile --noconsole --icon="%ADDITIONAL_FILES%\logo.ico" ^
    --add-data "%ADDITIONAL_FILES%\logo.png;%ADDITIONAL_FILES%" ^
    --add-data "%ADDITIONAL_FILES%\documentation.html;%ADDITIONAL_FILES%" ^
    %SCRIPT%

REM Check if build succeeded
if exist %OUTPUT_DIR%\main.exe (
    echo Executable created successfully in %OUTPUT_DIR%.
) else (
    echo Failed to create the executable.
)

pause
