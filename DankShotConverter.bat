@echo off
set input=%~f1
set p=%~dp0
call python %p%DankShotConverter.py %input%