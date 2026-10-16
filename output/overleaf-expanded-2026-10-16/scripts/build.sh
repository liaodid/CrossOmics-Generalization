#!/usr/bin/env bash
set -euo pipefail
project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$project_dir"
original_tex_inputs=${TEXINPUTS:-}
export TEXINPUTS="$project_dir/.texmf/tex/latex/ctex:$project_dir/.texmf/tex/latex/zhnumber:$original_tex_inputs"
if ! command -v xelatex >/dev/null 2>&1; then
  printf '%s\n' 'XeLaTeX is missing. Load a TeX module or install TeX Live with Chinese support.' >&2
  exit 1
fi
install_package() {
  local package=$1 checksum=$2 archive
  archive=$(mktemp "${TMPDIR:-/tmp}/ld-tex-${package}.XXXXXX")
  if ! curl -fsSL --retry 2 --connect-timeout 15 --max-time 90 \
    "https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/2021/tlnet-final/archive/${package}.tar.xz" \
    -o "$archive"; then
    rm -f "$archive"
    return 1
  fi
  if ! printf '%s  %s\n' "$checksum" "$archive" | sha256sum --check --status; then
    printf 'Checksum mismatch: %s\n' "$package" >&2
    rm -f "$archive"
    return 1
  fi
  mkdir -p .texmf
  tar -xJf "$archive" -C .texmf
  rm -f "$archive"
}
# These frozen packages match the cluster's TeX Live 2021.
if ! kpsewhich ctex.sty >/dev/null || ! kpsewhich ctexhook.sty >/dev/null; then
  printf '%s\n' 'Installing project-local ctex...'
  install_package ctex 057c481ab95ed5c4392d0fae4a49cad713064deb1e2c23695afbe3949d87ae76
fi
if ! kpsewhich zhnumber.sty >/dev/null; then
  printf '%s\n' 'Installing project-local zhnumber...'
  install_package zhnumber 25b72cac774ab01b612a6f7dbd63ede5ddfffcf25949e6d05b954bee62b2ac07
fi
mkdir -p build
# Recursive kpathsea lookup misses subdirectories on this filesystem because
# directory link counts are not conventional. Enumerate the package paths.
if [ -d "$project_dir/.texmf/tex" ]; then
  local_tex_paths=$(find "$project_dir/.texmf/tex" -type d -printf '%p:')
  export TEXINPUTS="$local_tex_paths$original_tex_inputs"
fi
for pass in 1 2; do
  printf 'XeLaTeX pass %s/2\n' "$pass"
  if ! xelatex -interaction=nonstopmode -halt-on-error -file-line-error \
    -output-directory=build main.tex > "build/pass-${pass}.txt" 2>&1; then
    tail -n 65 "build/pass-${pass}.txt" >&2
    exit 1
  fi
done
cp build/main.pdf main.pdf
printf 'Built: %s/main.pdf\n' "$project_dir"
if rg -n 'Overfull|Missing character|LaTeX Warning|Package .* Warning' build/main.log; then
  printf '%s\n' 'Review the warnings above before presenting.'
fi
