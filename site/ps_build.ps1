# 模拟 build.py 的构建逻辑，用 PowerShell 完成
$ErrorActionPreference = "Stop"

$root = "f6chem"
$site = "$root\site"
$dataDir = "$root\data"
$quizDir = "$root\quiz"
$extrasDir = "$root\extras"

# 1) 读取 version.json
$version = Get-Content "$site\version.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$siteName = $version.name
$siteVer = $version.version

Write-Host "站名: $siteName $siteVer" -ForegroundColor Cyan

# 2) 发现科目
$subjectIds = @()
Get-ChildItem $dataDir -Directory | ForEach-Object {
    $sid = $_.Name
    if (Test-Path "$dataDir\$sid\subject.json") {
        $subjectIds += $sid
    }
}
Write-Host "科目: $($subjectIds -join ', ')" -ForegroundColor Cyan

# 3) 构建 payload
$payload = @{
    site = @{
        name = $siteName
        version = $siteVer
        subtitle = $version.subtitle
        tagline = $version.tagline
        note = $version.note
        copyright = $version.copyright
        disclaimer = $version.disclaimer
    }
    subjects = @()
}

$RESERVED = @("subject", "links", "index")

foreach ($sid in $subjectIds) {
    $sdir = "$dataDir\$sid"
    $qdir = "$quizDir\$sid"
    $meta = Get-Content "$sdir\subject.json" -Raw -Encoding UTF8 | ConvertFrom-Json

    # 列出的课题
    $listed = @()
    if ($meta.topics) {
        foreach ($t in $meta.topics) {
            if ($t -and $t -notin $RESERVED) {
                $listed += $t
            }
        }
    }

    # 扫描 data 目录里的课题
    $found = @()
    Get-ChildItem "$sdir\*.json" -File | ForEach-Object {
        $stem = $_.BaseName
        if ($stem -notin $RESERVED -and -not $stem.StartsWith("payload") -and -not $stem.StartsWith("batch") -and -not $stem.StartsWith("tmp") -and -not $stem.StartsWith("_") -and -not $stem.EndsWith("-batch")) {
            $found += $stem
        }
    }
    $found = $found | Sort-Object

    if ($listed.Count -gt 0) {
        $topicsIds = $listed
    } else {
        $topicsIds = $found
    }

    # 读取课题数据
    $topics = @()
    foreach ($tid in $topicsIds) {
        $path = "$sdir\$tid.json"
        if (-not (Test-Path $path)) {
            Write-Host "  warning: $sid 缺少课题档 $tid.json" -ForegroundColor Yellow
            continue
        }
        $t = Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json
        if (-not $t.PSObject.Properties.Name.Contains("id")) {
            $t | Add-Member -NotePropertyName "id" -NotePropertyValue $tid
        }
        $topics += $t
    }
    # 排序
    $topics = $topics | Sort-Object { $_.id }

    # 读取 links
    $linksPath = "$sdir\links.json"
    $links = @()
    if (Test-Path $linksPath) {
        $links = Get-Content $linksPath -Raw -Encoding UTF8 | ConvertFrom-Json
    }
    # 过滤无效链接
    $pointIds = @{}
    foreach ($t in $topics) {
        foreach ($s in $t.sections) {
            foreach ($p in $s.points) {
                $pointIds[$p.id] = $true
            }
        }
    }
    $validLinks = @()
    $dropped = 0
    foreach ($l in $links) {
        if ($pointIds[$l.from] -and $pointIds[$l.to]) {
            $validLinks += $l
        } else {
            $dropped++
        }
    }
    if ($dropped -gt 0) {
        Write-Host "  note: $sid links.json 有 $dropped 条指向不存在的知识点，已忽略" -ForegroundColor Yellow
    }
    $links = $validLinks

    # 读取 quiz
    $quiz = @{}
    foreach ($tid in $topicsIds) {
        $qpath = "$qdir\$tid.json"
        if (-not (Test-Path $qpath)) {
            continue
        }
        $q = Get-Content $qpath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($q.questions) {
            $qs = @()
            foreach ($x in $q.questions) {
                $qs += $x
            }
            if ($qs.Count -gt 0) {
                $quiz[$tid] = $qs
            }
        }
    }

    # 统计
    $nPts = 0
    foreach ($t in $topics) {
        foreach ($s in $t.sections) {
            $nPts += $s.points.Count
        }
    }
    $nQ = 0
    foreach ($k in $quiz.Keys) {
        $nQ += $quiz[$k].Count
    }
    $ready = ($nPts -gt 0)

    # units
    $units = @()
    $rawUnits = @()
    if ($meta.PSObject.Properties.Name.Contains("units")) {
        $rawUnits = $meta.units
    }
    $tidSet = @{}
    foreach ($t in $topics) {
        $tidSet[$t.id] = $true
    }
    foreach ($u in $rawUnits) {
        $uTids = @()
        if ($u.topics) {
            foreach ($x in $u.topics) {
                if ($tidSet[$x]) {
                    $uTids += $x
                }
            }
        }
        if ($uTids.Count -eq 0) {
            Write-Host "  warning: $sid 的单元 $($u.id) 没有对应课题，已略过" -ForegroundColor Yellow
            continue
        }
        $uTopics = @()
        foreach ($t in $topics) {
            if ($t.id -in $uTids) {
                $uTopics += $t
            }
        }
        $uPts = 0
        $uSec = 0
        foreach ($t in $uTopics) {
            $uSec += $t.sections.Count
            foreach ($s in $t.sections) {
                $uPts += $s.points.Count
            }
        }
        $uQ = 0
        foreach ($t in $uTopics) {
            if ($quiz[$t.id]) {
                $uQ += $quiz[$t.id].Count
            }
        }
        $units += @{
            id = $u.id
            title = if ($u.title) { $u.title } else { $u.id }
            emoji = if ($u.emoji) { $u.emoji } else { "" }
            description = if ($u.description) { $u.description } else { "" }
            topics = $uTids
            stats = @{
                topics = $uTids.Count
                sections = $uSec
                points = $uPts
                questions = $uQ
            }
        }
    }

    # 统计
    $nSec = 0
    foreach ($t in $topics) {
        $nSec += $t.sections.Count
    }

    $subject = @{
        id = $sid
        title = if ($meta.title) { $meta.title } else { $sid }
        full = if ($meta.full) { $meta.full } else { if ($meta.title) { $meta.title } else { $sid } }
        emoji = if ($meta.emoji) { $meta.emoji } else { "📘" }
        color = if ($meta.color) { $meta.color } else { "#0f766e" }
        order = if ($meta.order) { $meta.order } else { 99 }
        description = if ($meta.description) { $meta.description } else { "" }
        source = if ($meta.source) { $meta.source } else { "" }
        ready = $ready
        topics = $topics
        units = $units
        links = $links
        quiz = $quiz
        extras = @()
        stats = @{
            topics = $topics.Count
            sections = $nSec
            points = $nPts
            links = $links.Count
            questions = $nQ
            units = $units.Count
        }
    }

    Write-Host "  $sid : 课题 $($topics.Count) · 章节 $nSec · 知识点 $nPts · 串连 $($links.Count) · 题目 $nQ" -ForegroundColor Green
    $payload.subjects += $subject
}

# 排序
$payload.subjects = $payload.subjects | Sort-Object { $_.order }, { $_.id }

# 4) 读取模板并替换
$tpl = Get-Content "$site\template.html" -Raw -Encoding UTF8
$tpl = $tpl.Replace("/*__SITE_NAME__*/", $siteName)
$tpl = $tpl.Replace("/*__SITE_VERSION__*/", $siteVer)
$tpl = $tpl.Replace("/*__SITE_SUBTITLE__*/", $version.subtitle)
$tpl = $tpl.Replace("/*__SITE_COPYRIGHT__*/", $version.copyright)

$discList = @()
if ($version.disclaimer) {
    $discList = $version.disclaimer
}
$discHtml = ""
foreach ($d in $discList) {
    $discHtml += "<li>$d</li>"
}
$tpl = $tpl.Replace("/*__SITE_DISCLAIMER__*/", $discHtml)

# extras.js
$exPath = "$site\extras.js"
if (Test-Path $exPath) {
    $exJs = Get-Content $exPath -Raw -Encoding UTF8
    $tpl = $tpl.Replace("/*__EXTRAS_JS__*/", $exJs)
} else {
    $tpl = $tpl.Replace("/*__EXTRAS_JS__*/", "")
}

# search-worker.js 注入
$swPath = "$site\search-worker.js"
if (Test-Path $swPath) {
    $swBytes = [System.IO.File]::ReadAllBytes($swPath)
    $swB64 = [System.Convert]::ToBase64String($swBytes)
    $swSrc = "var __SEARCH_WORKER_URL__ = URL.createObjectURL(new Blob([atob('" + $swB64 + "')], {type:'application/javascript'}));"
    $tpl = $tpl.Replace("/*__SEARCH_WORKER__*/", $swSrc)
} else {
    $tpl = $tpl.Replace("/*__SEARCH_WORKER__*/", "var __SEARCH_WORKER_URL__ = null;")
}

# 5) 序列化 payload
$json = $payload | ConvertTo-Json -Depth 30 -Compress
$json = $json.Replace("</", "<\/")

# 6) 输出
$out = $tpl.Replace("/*__DATA__*/", $json)

$stablePath = "$site\$siteName.html"
$versionedPath = "$site\$siteName-$siteVer.html"

$out | Set-Content $stablePath -Encoding UTF8 -NoNewline
$out | Set-Content $versionedPath -Encoding UTF8 -NoNewline

Write-Host "written: $stablePath ($((Get-Item $stablePath).Length) bytes)" -ForegroundColor Green
Write-Host "written: $versionedPath ($((Get-Item $versionedPath).Length) bytes)" -ForegroundColor Green
