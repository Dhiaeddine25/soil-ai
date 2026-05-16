# Kill processes on ports 3000 and 8000
$ports = @(3000, 8000)
foreach ($port in $ports) {
    $connection = netstat -ano | findstr ":$port" | findstr "LISTENING"
    if ($connection) {
        $pid = ($connection -split '\s+')[-1]
        Write-Host "Killing process $pid on port $port"
        Stop-Process -Id $pid -Force
    }
}
Write-Host "Cleanup complete. Starting backend..."