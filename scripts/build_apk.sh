#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../frontend"
flutter pub get
flutter build apk --release --dart-define=API_BASE_URL="${API_BASE_URL:-http://10.0.2.2:8000}"
mkdir -p ../artifacts
cp build/app/outputs/flutter-apk/app-release.apk ../artifacts/tonemind-ai-release.apk
printf 'APK generated at artifacts/tonemind-ai-release.apk
'
