# PowerShell стартовый скрипт для запуска компонентов SupportCopilot

Write-Host "Запускаю SupportCopilot..." -ForegroundColor Green

# Проверка, что запуск из корня репозитория
if (-not (Test-Path "apps")) {
    Write-Host "Ошибка: похоже, вы не в корне репозитория" -ForegroundColor Red
    exit 1
}

# Проверка активированного виртуального окружения
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Ошибка: активируйте виртуальное окружение" -ForegroundColor Red
    Write-Host "Пример: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    exit 1
}

# Утилита для запуска фоновых процессов
function Start-Service {
    param(
        [string]$Name,
        [string]$Command,
        [string]$WorkingDirectory
    )
    
    Write-Host "Стартую $Name..." -ForegroundColor Cyan
    
    try {
        if ($WorkingDirectory) {
            $process = Start-Process -FilePath "powershell" -ArgumentList "-Command", $Command -WorkingDirectory $WorkingDirectory -PassThru -WindowStyle Hidden
        } else {
            $process = Start-Process -FilePath "powershell" -ArgumentList "-Command", $Command -PassThru -WindowStyle Hidden
        }
        
        Write-Host "$Name запущен с PID: $($process.Id)" -ForegroundColor Green
        return $process
    }
    catch {
        Write-Host "Ошибка запуска $Name`: $_" -ForegroundColor Red
        return $null
    }
}

$processes = @()

try {
    # API сервер
    $apiProcess = Start-Service -Name "API Server" -Command "uvicorn main:app --host 0.0.0.0 --port 8000 --reload" -WorkingDirectory "apps\api"
    if ($apiProcess) {
        $processes += @{Name="API Server"; Process=$apiProcess}
    }
    
    Start-Sleep -Seconds 2
    
    # Telegram бот
    $botProcess = Start-Service -Name "Telegram Bot" -Command "python main.py" -WorkingDirectory "apps\bot"
    if ($botProcess) {
        $processes += @{Name="Telegram Bot"; Process=$botProcess}
    }
    
    Write-Host "`nГотово: все процессы запущены!" -ForegroundColor Green
    Write-Host "`n→ API Server: http://localhost:8000" -ForegroundColor Yellow
    Write-Host "→ Telegram Bot: включен" -ForegroundColor Yellow
    Write-Host "`nДля остановки используйте Ctrl+C" -ForegroundColor Cyan
    
    # Держим процесс живым
    while ($true) {
        Start-Sleep -Seconds 1
    }
    
}
catch {
    Write-Host "`nШтатная остановка сервисов..." -ForegroundColor Yellow
    
    foreach ($service in $processes) {
        try {
            Write-Host "Останавливаю $($service.Name)..." -ForegroundColor Cyan
            Stop-Process -Id $service.Process.Id -Force
            Write-Host "$($service.Name) остановлен" -ForegroundColor Green
        }
        catch {
            Write-Host "Ошибка остановки $($service.Name): $_" -ForegroundColor Red
        }
    }
    
    Write-Host "Готово: сервисы остановлены" -ForegroundColor Green
    exit 0
}

