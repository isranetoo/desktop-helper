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

python -c "from icon_factory import ensure_icon_assets; ensure_icon_assets()"

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "Organizador de Arquivos" ^
    --add-data "config.json;." ^
    --add-data "generated/icons;generated/icons" ^
    --icon="generated/icons/sortify.ico" ^
    organizador_gui.py

echo.
echo ============================================
echo  Executavel criado em dist/
echo ============================================
pause
