$ErrorActionPreference = 'Stop'
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    if (-not (Get-Command xelatex -ErrorAction SilentlyContinue)) {
        throw 'XeLaTeX is required. Install TeX Live/MiKTeX with ctex, beamer, fontawesome5 and Fandol, or compile on Overleaf.'
    }
    New-Item -ItemType Directory -Path build -Force | Out-Null
    foreach ($pass in 1..2) {
        & xelatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build main.tex
        if ($LASTEXITCODE -ne 0) { throw "XeLaTeX pass $pass failed. See build/main.log." }
    }
    Copy-Item -LiteralPath build/main.pdf -Destination main.pdf -Force
} finally { Pop-Location }
