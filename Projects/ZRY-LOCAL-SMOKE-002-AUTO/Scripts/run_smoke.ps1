# ZRY-LOCAL-SMOKE-002-AUTO runner (rewritten 2026-10-08).
#
# The 2026-09-26 runner was not saved to disk. Its output showed the bug: the REAPER marker was
# read with Get-Content and put into a hashtable, so ConvertTo-Json serialized PowerShell's
# hidden PSPath/PSDrive/PSProvider note properties and wrote 105,996,152 bytes of reflection
# metadata. This runner reads files with [IO.File] (plain .NET strings, no note properties),
# writes smoke_result.json as exactly what check_wav.py prints, and refuses oversized output.

$ErrorActionPreference = 'Stop'
$proj   = '%ZIRYAB_STUDIO%\Projects\ZRY-LOCAL-SMOKE-002-AUTO'
$reaper = 'C:\Program Files\REAPER (x64)\reaper.exe'
$lua    = "$proj\Scripts\ziryab_auto_smoke.lua"
$check  = "$proj\Scripts\check_wav.py"
$wav    = "$proj\Renders\ZRY-LOCAL-SMOKE-002-AUTO.wav"
$marker = "$proj\Provenance\reaper_done.txt"
$result = "$proj\Provenance\smoke_result.json"
$manifest = "$proj\Provenance\smoke_manifest.json"
$maxBytes = 64KB
$timeoutSec = 120

if (Get-Process reaper -ErrorAction SilentlyContinue) { throw 'REAPER is already running; close it first so the script runs in a fresh instance.' }

# The Lua script renders to a fixed path; keep the previous render instead of overwriting it.
if (Test-Path $wav) {
    $archive = "$proj\Renders\archive"
    New-Item -ItemType Directory -Force $archive | Out-Null
    $prev = Get-Item $wav
    $tag = $prev.LastWriteTime.ToString('yyyyMMdd-HHmmss') + '_' + (Get-FileHash $wav -Algorithm SHA256).Hash.Substring(0, 12)
    Move-Item $wav "$archive\ZRY-LOCAL-SMOKE-002-AUTO_$tag.wav"
}

Remove-Item $marker -ErrorAction SilentlyContinue
$started = Get-Date
$p = Start-Process -FilePath $reaper -ArgumentList '-nosplash', '-new', "`"$lua`"" -PassThru

# The Lua script writes the marker after the render command returns.
$deadline = $started.AddSeconds($timeoutSec)
while (-not (Test-Path $marker)) {
    if ((Get-Date) -gt $deadline) { throw "Timed out after $timeoutSec s waiting for $marker" }
    Start-Sleep -Milliseconds 500
}
$elapsed = ((Get-Date) - $started).TotalSeconds

# Close only the REAPER instance this script started.
if (-not $p.HasExited) {
    $null = $p.CloseMainWindow()
    if (-not $p.WaitForExit(15000)) { $p.Kill() }
}

if (-not (Test-Path $wav)) { throw "Render missing: $wav" }
if ((Get-Item $wav).LastWriteTime -lt $started) { throw "Render not refreshed by this run: $wav" }

# smoke_result.json holds exactly the one line check_wav.py prints.
$line = (& python -I $check $wav | Out-String).Trim()
if ($LASTEXITCODE -ne 0) { throw "check_wav.py failed: $line" }
[IO.File]::WriteAllText($result, $line + "`n", (New-Object Text.UTF8Encoding $false))

# Hashes and the marker go to a separate manifest, built from plain strings only.
function Sha($f) { (Get-FileHash $f -Algorithm SHA256).Hash }
$m = [ordered]@{
    test_id         = 'ZRY-LOCAL-SMOKE-002-AUTO'
    completed_at    = (Get-Date).ToString('o')
    reaper_version  = [string](Get-Item $reaper).VersionInfo.ProductVersion
    render_seconds  = [math]::Round($elapsed, 2)
    reaper_marker   = [IO.File]::ReadAllText($marker)
    wav_bytes       = (Get-Item $wav).Length
    wav_sha256      = Sha $wav
    check_wav       = $line | ConvertFrom-Json
}
[IO.File]::WriteAllText($manifest, ($m | ConvertTo-Json -Depth 3), (New-Object Text.UTF8Encoding $false))

foreach ($f in $result, $manifest) {
    $n = (Get-Item $f).Length
    if ($n -gt $maxBytes) { throw "$f is $n bytes, over the $maxBytes guard" }
}
Get-Item $result, $manifest | Select-Object Length, Name
