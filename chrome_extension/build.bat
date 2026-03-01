@echo off

if exist dist rmdir /s /q dist

if "%1"=="prod" (
    set NODE_ENV=production
    node build.js
    powershell -Command "Compress-Archive -Path dist -DestinationPath dist.zip -Force"
    echo Build complete ^-^> dist/ and dist.zip
) else (
    node build.js
)