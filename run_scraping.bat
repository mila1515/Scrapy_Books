@echo off
:: ===================================================
:: Script de scraping automatique pour Scrapy_Books
:: Fonctionnalités :
:: - Exécution du spider Scrapy
:: - Gestion des logs et sauvegardes
:: - Option de planification automatique
:: ===================================================

:: Vérifier si on doit planifier ou exécuter
if "%~1"=="--schedule" (
    goto :schedule
) else if "%~1"=="" (
    goto :execute
) else (
    echo Utilisation :
    echo   %~n0                - Exécuter le scraping maintenant
    echo   %~n0 --schedule     - Planifier l'exécution quotidienne à 17h
    goto :eof
)

:execute
:: Désactiver l'affichage des commandes
@echo off

:: Format de date et heure pour les noms de fichiers
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set DATE_PART=%dt:~0,8%
set TIME_PART=%dt:~8,4%

:: Dossiers de sortie
set DATA_DIR=books_api\data
set LOGS_DIR=logs
set DB_FILE=%DATA_DIR%\books.db

:: Créer les dossiers s'ils n'existent pas
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

:: Journalisation
echo [%DATE_PART% %TIME_PART%] Démarrage du processus de scraping... > "%LOGS_DIR%\scraping_%DATE_PART%.log"
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

:: Fichier de log unique
set LOG_FILE=%LOGS_DIR%\scraping_%DATE_PART%_%TIME_PART%.log

:: En-tête du log
echo ========================================= > "%LOG_FILE%"
echo %date% %time% - Démarrage du scraping >> "%LOG_FILE%"
echo ========================================= >> "%LOG_FILE%"

:: Vérifier si la base de données existe
echo %date% %time% - Vérification de la base de données... >> "%LOG_FILE%"
if exist "%DB_FILE%" (
    echo %date% %time% - Base de données trouvée: %DB_FILE% >> "%LOG_FILE%"
    echo %date% %time% - Taille de la base de données: %%~zDB_FILE% octets >> "%LOG_FILE%"
) else (
    echo %date% %time% - ATTENTION: La base de données n'existe pas, elle sera créée automatiquement >> "%LOG_FILE%"
)

:: Activer l'environnement virtuel
call env\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo %date% %time% - ERREUR: Impossible d'activer l'environnement virtuel >> "%LOG_FILE%"
    exit /b 1
)

:: Fichier de sortie temporaire (JSON)
set OUTPUT_FILE=%TEMP%\books_temp_%RANDOM%.json

:: Se placer dans le répertoire du projet
cd monprojet

:: Exécution du spider avec le pipeline SQLite activé
echo %date% %time% - Lancement du spider scrapybooks avec mise à jour de la base de données >> "..\%LOG_FILE%"
scrapy crawl scrapybooks -o "%OUTPUT_FILE%" --logfile="..\%LOGS_DIR%\scrapy_latest.log"

if %ERRORLEVEL% NEQ 0 (
    echo %date% %time% - ATTENTION: Le spider a rencontré des erreurs >> "..\%LOG_FILE%"
) else (
    echo %date% %time% - Spider exécuté avec succès >> "..\%LOG_FILE%"
    
    :: Vérifier la taille de la base de données après l'exécution
    if exist "..\%DB_FILE%" (
        echo %date% %time% - Base de données mise à jour: %DB_FILE% >> "..\%LOG_FILE%"
        echo %date% %time% - Nouvelle taille: %%~zDB_FILE% octets >> "..\%LOG_FILE%"
    )
    
    :: Sauvegarder les données brutes (optionnel)
    if exist "%OUTPUT_FILE%" (
        copy "%OUTPUT_FILE%" "..\%DATA_DIR%\books_%DATE_PART%_%TIME_PART%.json" >> "..\%LOG_FILE%"
        del "%OUTPUT_FILE%"
        
        :: Garder uniquement les 5 dernières versions
        for /f "skip=5 delims=" %%F in ('dir /b /o-d /a-d "..\%DATA_DIR%\books_*.json" ^| findstr /v "latest"') do (
            echo Suppression de l'ancien fichier: %%F >> "..\%LOG_FILE%"
            del "..\%DATA_DIR%\%%F"
        )
    )
)

:: Nettoyage des anciens logs (conserver les 5 derniers)
for /f "skip=5 delims=" %%F in ('dir /b /o-d /a-d "..\%LOGS_DIR%\scrapy_*.log"') do (
    echo Suppression de l'ancien log: %%F >> "..\%LOG_FILE%"
    del "..\%LOGS_DIR%\%%F"
)

:: Vérifier l'intégrité de la base de données
echo %date% %time% - Vérification de l'intégrité de la base de données... >> "..\%LOG_FILE%"
sqlite3 "..\%DB_FILE%" "PRAGMA integrity_check;" >> "..\%LOG_FILE%"

:: Faire une sauvegarde de la base de données
echo %date% %time% - Création d'une sauvegarde de la base de données... >> "..\%LOG_FILE%"
copy "..\%DB_FILE%" "..\%DB_FILE%.%DATE_PART%_%TIME_PART%.bak" >> "..\%LOG_FILE%"

:: Nettoyer les anciennes sauvegardes (garder les 5 plus récentes)
for /f "skip=5 delims=" %%F in ('dir /b /o-d /a-d "..\%DB_FILE%.*.bak"') do (
    echo Suppression de l'ancienne sauvegarde: %%F >> "..\%LOG_FILE%"
    del "..\%%F"
)

:: Revenir au répertoire racine
cd ..

:: Désactiver l'environnement virtuel
deactivate

echo %date% %time% - Script terminé >> "%LOG_FILE%"
echo ========================================= >> "%LOG_FILE%"
echo.

echo Le scraping est terminé et la base de données a été mise à jour.
echo Consultez le fichier de log pour plus de détails: %LOG_FILE%
echo.

exit /b 0
