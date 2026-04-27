@echo off
echo ============================================
echo  Build multiplataforma do Sortify
echo ============================================
echo.

python scripts\build.py --target windows

if %ERRORLEVEL% neq 0 (
  echo.
  echo Build falhou.
  pause
  exit /b %ERRORLEVEL%
)

echo.
echo ============================================
echo  Build concluido. Artefatos em dist/
echo ============================================
pause
