# 需要以「系統管理員」身分執行（開始選單搜尋 PowerShell → 右鍵 → 以系統管理員身分執行），然後貼上這段
$ruleName = "F6Chem Notes Site (8899)"
Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName $ruleName `
  -Description "允許區域網內的 iPhone/iPad 存取 F6 化學筆記整合網（僅限本機子網）" `
  -Direction Inbound -Action Allow `
  -Protocol TCP -LocalPort 8899 `
  -Profile Any `
  -RemoteAddress LocalSubnet `
  -Enabled True | Format-List DisplayName,Enabled,Action,Direction,Profile

Write-Host ""
Write-Host "=== 驗證 ===" -ForegroundColor Green
Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue |
  Format-List DisplayName, Enabled, Action, Direction, Profile
Write-Host ""
Write-Host "完成！現在用手機 Safari 打開：http://192.168.3.9:8899/" -ForegroundColor Cyan
