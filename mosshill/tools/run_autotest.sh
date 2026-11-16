#!/usr/bin/env bash
# 사용법: tools/run_autotest.sh <테스트이름> <스크린샷 폴더> [renpy SDK 경로]
# 예:     tools/run_autotest.sh m0 /tmp/shots ~/renpy-8.3.7-sdk
set -euo pipefail
NAME="${1:?테스트 이름}"; OUT="${2:?스크린샷 폴더}"
SDK="${3:-${RENPY_SDK:?RENPY_SDK 환경변수나 세 번째 인자로 SDK 경로를 주세요}}"
PROJECT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$OUT"
"$SDK/renpy.sh" "$PROJECT" lint
MH_AUTOTEST="$NAME" MH_SHOT_DIR="$OUT" SDL_AUDIODRIVER=dummy \
  xvfb-run -a -s "-screen 0 1920x1080x24" "$SDK/renpy.sh" "$PROJECT"
cat "$OUT/autotest.log"
