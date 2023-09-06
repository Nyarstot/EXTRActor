mkdir Build
cd venv/scripts
call activate.bat
pyinstaller --onefile --name EXTRActor --collect-all charset_normalizer --specpath ../../Build --distpath ../../ --workpath ../../Build --noconsole ../../EXTRActor.py
pause