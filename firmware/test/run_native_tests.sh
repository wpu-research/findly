#!/usr/bin/env bash
# Findy çekirdek birim testleri — yalnızca g++ gerekir (PlatformIO gerekmez).
# Kullanım: bash firmware/test/run_native_tests.sh   (çıkış kodu 0 = hepsi geçti)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE="$HERE/../lib/findy_core"
OUT="${FINDY_TEST_OUT:-$(mktemp -d)}"
CXX="${CXX:-g++}"
"$CXX" -std=c++17 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined \
  -I"$CORE" "$HERE/test_core.cpp" "$CORE"/*.cpp -o "$OUT/findy_tests" -lm
"$OUT/findy_tests"
