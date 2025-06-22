#!/bin/bash

echo "Building Tzotzil Bible APK..."

# Install dependencies
npm install

# Build for Android using Expo CLI
npx expo build:android --type apk --release-channel production

echo "APK build process completed!"
echo "Check the output for download link or local APK file."