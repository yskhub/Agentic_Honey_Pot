<#
.SYNOPSIS
  Generate or load a new AUDIT_HMAC_KEY and optionally write to an env file.

.DESCRIPTION
  PowerShell equivalent of dev-scripts/rotate_audit_key.sh. By default it prints
  the new key to stdout (do NOT commit). Use -Write to append to an env file.

.PARAMETER Generate
  Switch to generate a new random key.

.PARAMETER NewKeyFile
  Path to a file containing the new key.

.PARAMETER EnvFile
  Path to env file to append the AUDIT_HMAC_KEY_NEXT entry. Defaults to .env

.PARAMETER Write
  If present, append the new key to the env file. Otherwise the key is printed.

.EXAMPLE
  .\dev-scripts\rotate_audit_key.ps1 -Generate
  .\dev-scripts\rotate_audit_key.ps1 -Generate -Write -EnvFile .env

#>
param(
    [switch]$Generate,
    [string]$NewKeyFile = "",
    [string]$EnvFile = ".env",
    [switch]$Write
)

function Generate-Key {
    $bytes = New-Object byte[] 32
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    return [System.Convert]::ToBase64String($bytes)
}

if ($NewKeyFile -and $Generate) {
    Write-Error "Specify either -Generate or -NewKeyFile, not both."; exit 1
}

if ($NewKeyFile) {
    if (-not (Test-Path $NewKeyFile)) { Write-Error "New key file not found: $NewKeyFile"; exit 1 }
    $newKey = Get-Content -Raw -Path $NewKeyFile
} elseif ($Generate) {
    $newKey = Generate-Key
} else {
    Write-Error "Either -Generate or -NewKeyFile must be provided."; exit 1
}

Write-Host "New AUDIT HMAC key (first 8 chars): $($newKey.Substring(0,8))..."

if ($Write) {
    "$([System.Environment]::NewLine)# Added by dev-scripts/rotate_audit_key.ps1 - next audit HMAC key`nAUDIT_HMAC_KEY_NEXT=$newKey" | Out-File -FilePath $EnvFile -Encoding utf8 -Append
    Write-Host "Wrote AUDIT_HMAC_KEY_NEXT to $EnvFile"
} else {
    Write-Host "Key (do NOT commit):`n$newKey`n"
    Write-Host "To persist to $EnvFile, re-run with -Write or store the key in your secret manager."
}

Write-Host "Next steps:`n1) Store the new key in your secret manager; avoid committing secrets to VCS.`n2) Deploy app instances with both AUDIT_HMAC_KEY (current) and AUDIT_HMAC_KEY_NEXT set.`n3) When ready, set AUDIT_HMAC_KEY to the new key and remove AUDIT_HMAC_KEY_NEXT.`n"

exit 0
