cd "C:\Users\surface pro 7\Desktop\npk_90percent\frontend"
$env:NODE_OPTIONS="--trace-warnings --trace-uncaught"
npx next dev 2>&1 | Tee-Object -FilePath ".\dev-output.log" -Append
