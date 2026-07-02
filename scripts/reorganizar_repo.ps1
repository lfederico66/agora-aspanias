# reorganizar_repo.ps1
# v2 — sin recursión que reentra en cuarentena.
# Aplica el plan de reorganización propuesto por la skill ordenador-archivos.
# Registra cada movimiento y genera deshacer al terminar.

$ErrorActionPreference = 'Stop'
$root = (Get-Location).Path
$log = @()
$deshacer = @()

function Move-Tracked {
    param([string]$src, [string]$dst)
    if (-not (Test-Path $src)) { Write-Host "  skip (no existe): $src"; return }
    $dstDir = Split-Path $dst -Parent
    if (-not (Test-Path $dstDir)) { New-Item -ItemType Directory -Path $dstDir -Force | Out-Null }
    Move-Item -Path $src -Destination $dst -Force
    $script:log += [PSCustomObject]@{accion='mover'; origen=$src; destino=$dst}
    $script:deshacer += "Move-Item -Path '$dst' -Destination '$src' -Force"
    Write-Host "  + $($src.Replace($root,'.'))  ->  $($dst.Replace($root,'.'))"
}

Write-Host "`n=== 1. frontend/ vacia a cuarentena ===" -ForegroundColor Cyan
$cuarentena = "$root\_PARA_REVISAR"
if (-not (Test-Path $cuarentena)) { New-Item -ItemType Directory -Path $cuarentena | Out-Null }
$frontendVacio = "$root\frontend"
if (Test-Path $frontendVacio) {
    $contenido = Get-ChildItem $frontendVacio -Recurse -ErrorAction SilentlyContinue
    if ($null -eq $contenido) {
        Move-Tracked -src $frontendVacio -dst "$cuarentena\frontend_vacia"
    }
}

Write-Host "`n=== 2. dist/ para artefactos build ===" -ForegroundColor Cyan
Move-Tracked -src "$root\AGORA-demo-para-netlify.zip" -dst "$root\dist\actual\AGORA-demo-para-netlify.zip"
Move-Tracked -src "$root\AGORA-demo-2026-05-19.zip"    -dst "$root\dist\historico\AGORA-demo-2026-05-19.zip"

Write-Host "`n=== 3. docs/fases/ agrupando fase0..fase4 ===" -ForegroundColor Cyan
foreach ($f in 'fase0','fase1','fase3','fase4') {
    Move-Tracked -src "$root\docs\$f" -dst "$root\docs\fases\$f"
}

Write-Host "`n=== 4. docs/modelo-datos: decisiones/ + historico/ ===" -ForegroundColor Cyan
$md = "$root\docs\modelo-datos"
$decisiones = @(
    @{ src = 'decision_dinero_bolsillo.md';                dst = '01_dinero_bolsillo.md' }
    @{ src = 'decision_facturacion_servicios_extras.md';   dst = '02_facturacion_servicios_extras.md' }
    @{ src = 'decision_fis_incidencias.md';                dst = '03_fis_incidencias.md' }
    @{ src = 'decision_servicios_multiples.md';            dst = '04_servicios_multiples.md' }
    @{ src = 'decision_modulo_equipo_solapamiento.md';     dst = '05_modulo_equipo_solapamiento.md' }
)
foreach ($d in $decisiones) {
    Move-Tracked -src "$md\$($d.src)" -dst "$md\decisiones\$($d.dst)"
}
Move-Tracked -src "$md\analisis_cgpr_estructura.md" -dst "$md\decisiones\analisis_cgpr_estructura.md"

foreach ($v in 1..11) {
    Move-Tracked -src "$md\modelo_v0_$v.md" -dst "$md\historico\modelo_v0_$v.md"
}
# v0_12 se renombra como modelo_actual.md (en su sitio)
if (Test-Path "$md\modelo_v0_12.md") {
    $oldFull = "$md\modelo_v0_12.md"
    $newFull = "$md\modelo_actual.md"
    Move-Item -Path $oldFull -Destination $newFull -Force
    $script:log += [PSCustomObject]@{accion='renombrar'; origen=$oldFull; destino=$newFull}
    $script:deshacer += "Move-Item -Path '$newFull' -Destination '$oldFull' -Force"
    Write-Host "  + renombrar  modelo_v0_12.md -> modelo_actual.md"
}

Write-Host "`n=== 5. scripts/utilidades/ + scripts/historico/ ===" -ForegroundColor Cyan
$scr = "$root\scripts"
$utilidades = @(
    'auditar_demo.py',
    'pseudonimizar_excel_pv.py',
    'prueba_seco_importador.py',
    'generar_mapa_interactivo.py',
    'analizar_cgpr_estructura.py',
    'limpiar_comentarios_django.py',
    'lanzar_claude.bat',
    'arranque_local.md'
)
foreach ($u in $utilidades) {
    Move-Tracked -src "$scr\$u" -dst "$scr\utilidades\$u"
}

$historico = @(
    'fix_backslash_definitivo.py',
    'fix_breadcrumbs_duplicados.py',
    'fix_centros_casos_sueltos.py',
    'fix_equipo_tab.py',
    'fix_modales_scope.py',
    'refactor_centros_count.py',
    'refactor_nav_demo.py',
    'refactor_nombres_centros.py',
    'refactor_sidebar_v2.py',
    'rebrand_sipas_to_agora.py',
    'add_generar_factura.py',
    'aplicar_shell_ux.py',
    'reinsertar_tabs_familia_medico.py',
    'rellenar_tabs_persona.py',
    'reordenar_tabla_centro.py'
)
foreach ($h in $historico) {
    Move-Tracked -src "$scr\$h" -dst "$scr\historico\$h"
}

# Script con acento -> historico/ + sin acento
$conAcento = "$scr\rediseñar_personas_lista.py"
$sinAcento = "$scr\historico\redisenar_personas_lista.py"
if (Test-Path $conAcento) {
    if (-not (Test-Path "$scr\historico")) { New-Item -ItemType Directory -Path "$scr\historico" -Force | Out-Null }
    Move-Item -Path $conAcento -Destination $sinAcento -Force
    $script:log += [PSCustomObject]@{accion='renombrar+mover'; origen=$conAcento; destino=$sinAcento}
    $script:deshacer += "Move-Item -Path '$sinAcento' -Destination '$conAcento' -Force"
    Write-Host "  + renombrar  rediseñar_personas_lista.py -> historico/redisenar_personas_lista.py"
}

Write-Host "`n=== 6. Guardar log y deshacer ===" -ForegroundColor Cyan
$logPath = "$root\scripts\utilidades\reorganizacion_log.csv"
if (-not (Test-Path (Split-Path $logPath -Parent))) {
    New-Item -ItemType Directory -Path (Split-Path $logPath -Parent) -Force | Out-Null
}
$log | Export-Csv -Path $logPath -NoTypeInformation -Encoding UTF8
Write-Host "  log:       $($logPath.Replace($root,'.'))"

$deshacerPath = "$root\scripts\utilidades\deshacer_reorganizacion.ps1"
$header = "# deshacer_reorganizacion.ps1`n# Revierte los movimientos de reorganizar_repo.ps1`n# Generado: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n`n`$ErrorActionPreference = 'Continue'`nWrite-Host 'Revirtiendo reorganizacion...' -ForegroundColor Yellow`n`n"
$body = ($deshacer | Sort-Object -Descending) -join "`n"
$footer = "`n`nWrite-Host 'Hecho.' -ForegroundColor Green"
Set-Content -Path $deshacerPath -Value ($header + $body + $footer) -Encoding UTF8
Write-Host "  deshacer:  $($deshacerPath.Replace($root,'.'))"

Write-Host "`n=== RESUMEN ===" -ForegroundColor Green
Write-Host "  Movimientos: $($log.Count)"
