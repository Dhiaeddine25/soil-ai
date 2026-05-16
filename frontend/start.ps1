Set-Location "C:\Users\surface pro 7\Desktop\npk_90percent\frontend"
Write-Host "=== Demarrage Next.js production ==="
npx next start -p 3000 --hostname 127.0.0.1
Write-Host "=== Termine code: $LASTEXITCODE ==="
pause
