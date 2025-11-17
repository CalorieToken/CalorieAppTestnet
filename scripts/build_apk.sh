#!/bin/bash
# CalorieApp APK Build Script

echo "🚀 CalorieApp APK Build Script"
echo "=============================="

# Check if buildozer is installed
if ! command -v buildozer &> /dev/null; then
    echo "❌ Buildozer not found. Installing..."
    pip install buildozer
fi

echo "✅ Buildozer found"

# Check if we're in the right directory
if [ ! -f "buildozer.spec" ]; then
    echo "❌ buildozer.spec not found. Make sure you're in the project root directory."
    exit 1
fi

echo "✅ Project structure verified"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
buildozer android clean

# Build debug APK
echo "🔨 Building debug APK..."
buildozer android debug

# Check if build was successful
if [ -f "bin/calorieapp-*.apk" ]; then
    echo "✅ APK built successfully!"
    echo "📱 APK location: bin/calorieapp-*.apk"
    echo "🎉 Ready for installation!"
else
    echo "❌ Build failed. Check the output above for errors."
    exit 1
fi