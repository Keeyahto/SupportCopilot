# PowerShell скрипт для запуска SupportCopilot

Write-Host "🚀 Запуск SupportCopilot..." -ForegroundColor Green

# Проверяем, что мы в корневой директории проекта
if (-not (Test-Path "apps")) {
    Write-Host "❌ Ошибка: запустите скрипт из корневой директории проекта" -ForegroundColor Red
    exit 1
}

# Проверяем виртуальное окружение
if (-not $env:VIRTUAL_ENV) {
    Write-Host "❌ Ошибка: активируйте виртуальное окружение" -ForegroundColor Red
    Write-Host "Выполните: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    exit 1
}

# Функция для запуска сервиса
function Start-Service {
    param(
        [string]$Name,
        [string]$Command,
        [string]$WorkingDirectory
    )
    
    Write-Host "Запуск $Name..." -ForegroundColor Cyan
    
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
    # Запуск API сервера
    $apiProcess = Start-Service -Name "API Server" -Command "uvicorn main:app --host 0.0.0.0 --port 8000 --reload" -WorkingDirectory "apps\api"
    if ($apiProcess) {
        $processes += @{Name="API Server"; Process=$apiProcess}
    }
    
    Start-Sleep -Seconds 2
    
    # Запуск Tools API
    $toolsProcess = Start-Service -Name "Tools API" -Command "uvicorn main:app --host 0.0.0.0 --port 8001 --reload" -WorkingDirectory "apps\tools_api"
    if ($toolsProcess) {
        $processes += @{Name="Tools API"; Process=$toolsProcess}
    }
    
    Start-Sleep -Seconds 2
    
    # Запуск Telegram бота
    $botProcess = Start-Service -Name "Telegram Bot" -Command "python main.py" -WorkingDirectory "apps\bot"
    if ($botProcess) {
        $processes += @{Name="Telegram Bot"; Process=$botProcess}
    }
    
    Write-Host "`n✅ Все сервисы запущены!" -ForegroundColor Green
    Write-Host "`n🌐 API Server: http://localhost:8000" -ForegroundColor Yellow
    Write-Host "🔧 Tools API: http://localhost:8001" -ForegroundColor Yellow
    Write-Host "🤖 Telegram Bot: активен" -ForegroundColor Yellow
    Write-Host "`nДля остановки нажмите Ctrl+C" -ForegroundColor Cyan
    
    # Ждем сигнала остановки
    while ($true) {
        Start-Sleep -Seconds 1
    }
    
}
catch {
    Write-Host "`n🛑 Остановка сервисов..." -ForegroundColor Yellow
    
    foreach ($service in $processes) {
        try {
            Write-Host "Остановка $($service.Name)..." -ForegroundColor Cyan
            Stop-Process -Id $service.Process.Id -Force
            Write-Host "$($service.Name) остановлен" -ForegroundColor Green
        }
        catch {
            Write-Host "Ошибка остановки $($service.Name): $_" -ForegroundColor Red
        }
    }
    
    Write-Host "✅ Все сервисы остановлены" -ForegroundColor Green
    exit 0
}
