#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUBYOPT_FIX="-r${ROOT_DIR}/scripts/ruby_cxx_fix.rb"

cd "$ROOT_DIR"
RUBYOPT="$RUBYOPT_FIX" bundle install
RUBYOPT="$RUBYOPT_FIX" bundle exec jekyll build
