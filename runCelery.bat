:MINE
@ECHO off

set "script_path=%~dp0"
set "script_path=%script_path%restart_celery.py"

celery -A app.celery worker
GOTO :MINE