$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$docsPath = Join-Path $projectRoot "docs"

New-Item -ItemType Directory -Force -Path $docsPath | Out-Null
Push-Location $docsPath
try {
    $env:PYTHONPATH = $projectRoot
    python -m pydoc -w main
}
finally {
    Pop-Location
}

Write-Output "Documentation generated in $docsPath\main.html"
