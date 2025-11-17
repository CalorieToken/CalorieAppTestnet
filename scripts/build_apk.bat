@echo off
REM CalorieApp APK Build Script for Windows

echo 🚀 CalorieApp APK Build Script
echo ==============================

REM Check if buildozer is installed
buildozer --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Buildozer not found. Installing...
    pip install buildozer
)

echo ✅ Buildozer found

REM Check if we're in the right directory
if not exist "buildozer.spec" (
    echo ❌ buildozer.spec not found. Make sure you're in the project root directory.
    pause
    exit /b 1
)

echo ✅ Project structure verified

REM Clean previous builds
echo 🧹 Cleaning previous builds...
buildozer android clean

REM Build debug APK
echo 🔨 Building debug APK...
buildozer android debug

REM Check if build was successful
if exist "bin\calorieapp-*.apk" (
    echo ✅ APK built successfully!
    echo 📱 APK location: bin\calorieapp-*.apk
    echo 🎉 Ready for installation!
) else (
    echo ❌ Build failed. Check the output above for errors.
    pause
    exit /b 1
)

pause