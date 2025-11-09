@echo off
chcp 65001 > nul



python tests\test_algorithms.py

if %errorlevel% neq 0 (
    echo FAIL: Algorithm tests failed
    pause
    exit /b %errorlevel%
)
echo.


python tests\test_performance.py

if %errorlevel% neq 0 (
    echo FAIL: Performance tests failed
    pause
    exit /b %errorlevel%
)
echo.


python tests\test_advanced.py

if %errorlevel% neq 0 (
    echo FAIL: Advanced tests failed
    pause
    exit /b %errorlevel%
)

echo.

pause
