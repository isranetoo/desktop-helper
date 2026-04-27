@echo off
echo ============================================
echo  Construindo executavel do Organizador
echo ============================================
echo.

pip install -r requirements.txt
pip install pyinstaller

echo.
echo Gerando .exe ...
echo.

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "Organizador de Arquivos" ^
    --add-data "config.json;." ^
    organizador_gui.py

echo.
echo ============================================
echo  Executavel criado em dist/
echo ============================================
pause
