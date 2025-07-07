# PowerShell Skript zum automatischen Ausführen der Python-Pipeline

Write-Host "Starte Sniper-Bot Datenpipeline..." -ForegroundColor Green

# Pfad anpassen falls nötig
$python = "python"
$script = "C:\Users\benja\desktop\sniper-bot\run_full_pipeline.py"

# Pipeline starten
& $python $script

if ($LASTEXITCODE -eq 0) {
    Write-Host "Pipeline erfolgreich abgeschlossen." -ForegroundColor Green
} else {
    Write-Host "Fehler in Pipeline. Bitte Logs prüfen." -ForegroundColor Red
    exit $LASTEXITCODE
}
