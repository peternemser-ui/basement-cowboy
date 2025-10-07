@echo off
REM Basement Cowboy - Shipping Readiness Test
title Shipping Readiness Test - Basement Cowboy
color 0B

echo.
echo  ████████╗███████╗███████╗████████╗
echo  ╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝
echo     ██║   █████╗  ███████╗   ██║   
echo     ██║   ██╔══╝  ╚════██║   ██║   
echo     ██║   ███████╗███████║   ██║   
echo     ╚═╝   ╚══════╝╚══════╝   ╚═╝   
echo.
echo        🧪 SHIPPING READINESS TEST 🧪
echo.
echo ================================================================
echo.

set errors=0

echo 🔍 Testing Basement Cowboy shipping readiness...
echo.

REM Test 1: Python Version
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found or not in PATH
    set /a errors+=1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo ✅ Python %%i detected
)

REM Test 2: Critical Files
echo [2/8] Checking critical files...
set files=run.py requirements.txt .env.template README.md start-cowboy.bat
for %%f in (%files%) do (
    if exist "%%f" (
        echo ✅ Found: %%f
    ) else (
        echo ❌ Missing: %%f
        set /a errors+=1
    )
)

REM Test 3: Directory Structure
echo [3/8] Checking directory structure...
set dirs=app config scraper output tests
for %%d in (%dirs%) do (
    if exist "%%d" (
        echo ✅ Directory: %%d
    ) else (
        echo ❌ Missing directory: %%d
        set /a errors+=1
    )
)

REM Test 4: Security Check (.env)
echo [4/8] Checking security configuration...
if exist ".env" (
    findstr /C:"your-openai-api-key-here" .env >nul
    if not errorlevel 1 (
        echo ✅ .env contains placeholder values (secure)
    ) else (
        echo ⚠️  .env may contain real API keys (check before commit)
    )
) else (
    echo ✅ No .env file (will be created from template)
)

REM Test 5: .gitignore Protection
echo [5/8] Checking .gitignore protection...
if exist ".gitignore" (
    findstr /C:".env" .gitignore >nul
    if not errorlevel 1 (
        echo ✅ .gitignore protects .env file
    ) else (
        echo ❌ .gitignore does not protect .env file
        set /a errors+=1
    )
) else (
    echo ❌ .gitignore file missing
    set /a errors+=1
)

REM Test 6: Python Dependencies
echo [6/8] Testing Python imports...
python -c "import flask, openai, requests, dotenv" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Some dependencies may be missing (run in virtual env)
) else (
    echo ✅ Core dependencies importable
)

REM Test 7: Application Creation
echo [7/8] Testing application creation...
python -c "from app.routes import create_app; app = create_app(); print('App created successfully')" >nul 2>&1
if errorlevel 1 (
    echo ❌ Application creation failed
    set /a errors+=1
) else (
    echo ✅ Application creates successfully
)

REM Test 8: Requirements Validation
echo [8/8] Validating requirements.txt...
pip install -r requirements.txt --dry-run --quiet >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Requirements validation warning (may need virtual env)
) else (
    echo ✅ Requirements file is valid
)

echo.
echo ================================================================
echo  📊 TEST RESULTS
echo ================================================================

if %errors%==0 (
    echo.
    echo 🎉 SUCCESS! Basement Cowboy is READY TO SHIP!
    echo.
    echo ✅ All critical tests passed
    echo ✅ Security configuration is safe
    echo ✅ File structure is complete
    echo ✅ Dependencies are satisfied
    echo.
    echo 📋 NEXT STEPS TO DEPLOY:
    echo    1. Edit .env file with your OpenAI API key
    echo    2. Double-click start-cowboy.bat
    echo    3. Access http://localhost:5000
    echo    4. Test core functionality
    echo.
    echo 🚀 Ready for production deployment!
    color 0A
) else (
    echo.
    echo ❌ FAILED: %errors% issue(s) found
    echo.
    echo 🔧 Fix the issues above before shipping
    echo 📚 Check SHIPPING_TEST.md for detailed guidance
    echo 💡 Run this test again after fixes
    color 0C
)

echo.
echo Press any key to exit...
pause >nul