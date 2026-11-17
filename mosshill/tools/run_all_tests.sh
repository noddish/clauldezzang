#!/usr/bin/env bash
# 전체 검사: 엔진 단위 테스트 + 모든 자동 플레이 테스트. 실패가 하나라도 있으면 exit 1.
# 사용법: tools/run_all_tests.sh <결과 폴더> [renpy SDK 경로]
set -uo pipefail
OUT="${1:?결과 폴더}"; SDK="${2:-${RENPY_SDK:?SDK 경로}}"
HERE="$(cd "$(dirname "$0")" && pwd)"
TESTS="m0 m1 m1_lazy m2 m2_lose ui"
status=0
echo "== 엔진 단위 테스트"
python3 "$HERE/test_engine.py" | tail -1 || status=1
for t in $TESTS; do
  mkdir -p "$OUT/$t"; : > "$OUT/$t/autotest.log"
  timeout 900 "$HERE/run_autotest.sh" "$t" "$OUT/$t" "$SDK" > "$OUT/$t.out" 2>&1
  line=$(grep -E '^RESULT' "$OUT/$t/autotest.log" || true)
  if grep -qE 'FAIL|EXCEPTION' "$OUT/$t/autotest.log" || ! grep -q '^done' "$OUT/$t/autotest.log"; then
    status=1; echo "== $t  실패  $line"; grep -E 'FAIL|EXCEPTION' "$OUT/$t/autotest.log" | head -5
  else
    echo "== $t  통과  $line"
  fi
done
exit $status
