@echo off
REM Lanzador rápido de Claude Code para el proyecto ÁGORA.
REM Abrir CMD desde la raíz del repo y ejecutar: scripts\lanzar_claude.bat
cd /d "%~dp0\.."
echo Arrancando Claude Code en: %CD%
claude
