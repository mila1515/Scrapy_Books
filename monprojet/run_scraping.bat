@echo off
:: Configuration du script de scraping automatique
:: Version simplifiée - tout dans le dossier data
:: Créé le 01/10/2025

:: Désactiver l'affichage des commandes
@echo off

:: Format de date et heure pour les noms de fichiers
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set DATE_PART=%dt:~0,8%
set TIME_PART=%dt:~8,4%

:: Fichier de log unique
set LOG_FILE=data\scraping.log

:: Créer le dossier data s'il n'existe pas
if not exist "data" mkdir "data"

:: En-tête du log
echo ========================================= >> "%LOG_FILE%"
echo %date% %time% - Démarrage du scraping >> "%LOG_FILE%"
echo ========================================= >> "%LOG_FILE%"

:: Activer l'environnement virtuel
call ..\env\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo %date% %time% - ERREUR: Impossible d'activer l'environnement virtuel >> "%LOG_FILE%"
    exit /b 1
)

:: Fichier de sortie unique (écrase à chaque exécution)
set OUTPUT_FILE=data\books_latest.json

:: Exécution du spider
echo %date% %time% - Lancement du spider scrapybooks >> "%LOG_FILE%"
scrapy crawl scrapybooks -o "%OUTPUT_FILE" --logfile="data\scrapy_latest.log"

if %ERRORLEVEL% NEQ 0 (
    echo %date% %time% - ATTENTION: Le spider a rencontré des erreurs >> "%LOG_FILE%"
) else (
    echo %date% %time% - Spider exécuté avec succès >> "%LOG_FILE%"
    
    # Créer une copie avec horodatage
    copy "%OUTPUT_FILE" "data\books_%DATE_PART%_%TIME_PART%.json" >> "%LOG_FILE%"
    
    # Garder uniquement les 5 dernières versions
    for /f "skip=5 delims=" %%F in ('dir /b /o-d /a-d "data\books_*.json" ^| findstr /v "latest"') do (
        echo Suppression de l'ancien fichier: %%F >> "%LOG_FILE%"
        del "data\%%F"
    )
)

:: Nettoyage des anciens logs (conserver les 5 derniers)
for /f "skip=5 delims=" %%F in ('dir /b /o-d /a-d "data\scrapy_*.log"') do (
    echo Suppression de l'ancien log: %%F >> "%LOG_FILE%"
    del "data\%%F"
)

:: Désactiver l'environnement virtuel
deactivate

echo %date% %time% - Script terminé >> "%LOG_FILE%"
echo ========================================= >> "%LOG_FILE%"
echo.

exit /b 0
