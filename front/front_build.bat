@echo off
rem ------------------------------------------------
rem 1. Clear old files
del /q C:\Web\dev\back\templates\*.*
rem rmdir C:\Web\dev\back\static /s /q
rem rmdir C:\Web\dev\back\staticfiles /s /q
rem mkdir C:\Web\dev\back\static
rem mkdir C:\Web\dev\back\staticfiles
rem goto test_mark

rem ------------------------------------------------
rem 1.1. Serve firebase-messaging-sw.js
xcopy C:\Web\dev\back\todo\static\todo\js\firebase-messaging-sw.js C:\Web\dev\back\templates /Y /Q

rem ------------------------------------------------
rem 2. Collect static
rem cd C:\Web\dev\back
rem call ..\env\scripts\activate.bat
rem pip freeze > requirements.txt
rem python manage.py collectstatic --noinput
rem call ..\env\scripts\deactivate

rem ------------------------------------------------
rem 3. Build frontend
rem cd C:\Web\dev\front
call npm run build
rem cd C:\Users\ok

rem ------------------------------------------------
rem 4. Copy frontend to backend
xcopy C:\Web\dev\front\build\asset-manifest.json  C:\Web\dev\back\templates /Y /Q
xcopy C:\Web\dev\front\build\manifest.json        C:\Web\dev\back\templates /Y /Q
xcopy C:\Web\dev\front\build\index.html           C:\Web\dev\back\templates /Y /Q
xcopy C:\Web\dev\front\build\robots.txt           C:\Web\dev\back\templates /Y /Q
xcopy C:\Web\dev\front\build\static               C:\Web\dev\back\static /E /Y /Q

npm run start