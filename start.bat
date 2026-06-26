@echo off
REM ─── NidBuyer - Démarrage backend + frontend ──────────────────────────────

echo.
echo  NidBuyer - Demarrage...
echo.

REM Activer le venv si present
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo [WARN] Pas de .venv trouve - utilisation du Python systeme
)

REM Verifier qu'Ollama tourne
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [WARN] Ollama ne repond pas sur 127.0.0.1:11434
    echo        Lancez Ollama puis relancez ce script.
    echo        Commande : ollama serve
    echo.
) else (
    echo [OK] Ollama repond sur 127.0.0.1:11434
)

REM Lancer le backend FastAPI dans un nouveau terminal
echo [*] Demarrage du backend FastAPI sur http://localhost:8000 ...
start "NidBuyer Backend" cmd /k "cd /d "%~dp0" && uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

REM Attendre que le backend soit pret
echo [*] Attente du backend (5 secondes)...
timeout /t 5 /nobreak >nul

REM Lancer le frontend Streamlit dans ce terminal
echo [*] Demarrage du frontend Streamlit sur http://localhost:8501 ...
echo.
streamlit run frontend/app.py --server.port 8501
