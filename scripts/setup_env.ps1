<#
.SYNOPSIS
    智量通自动化测试 - Jenkins 环境准备脚本
.DESCRIPTION
    检查并准备 Jenkins Windows Agent 上的运行环境
.PARAMETER Workspace
    Jenkins 工作目录路径
#>
param(
    [string]$Workspace = $env:WORKSPACE
)

$ErrorActionPreference = "Stop"
$exitCode = 0

function Write-Status {
    param([string]$Message, [string]$Status = "INFO")
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$ts] [$Status] $Message"
}

function Test-Command {
    param([string]$Command)
    try {
        $null = Get-Command $Command -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# ============================================================
# 1. 检查 Python
# ============================================================
Write-Status "检查 Python 环境..."
if (-not (Test-Command "python")) {
    Write-Status "未找到 python 命令，请先在 Jenkins 节点上安装 Python 3.10+" "ERROR"
    exit 1
}

$pyVersion = python --version 2>&1
Write-Status "Python 版本: $pyVersion"

if (-not (Test-Command "pip")) {
    Write-Status "未找到 pip 命令" "ERROR"
    exit 1
}
Write-Status "pip 已就绪"

# ============================================================
# 2. 检查 VS Code
# ============================================================
Write-Status "检查 VS Code..."

$vsCodePaths = @(
    "E:\Microsoft VS Code\bin\code.cmd",
    "E:\Microsoft VS Code\Code.exe",
    "$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin\code.cmd",
    "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe",
    "C:\Program Files\Microsoft VS Code\bin\code.cmd",
    "C:\Program Files\Microsoft VS Code\Code.exe",
    "C:\Program Files (x86)\Microsoft VS Code\bin\code.cmd",
    "C:\Program Files (x86)\Microsoft VS Code\Code.exe"
)

$codeCmd = $null
foreach ($p in $vsCodePaths) {
    if (Test-Path $p) {
        $codeCmd = $p
        break
    }
}

if (-not $codeCmd) {
    if (Test-Command "code") {
        $codeCmd = "code"
    }
}

if (-not $codeCmd) {
    Write-Status "未找到 VS Code" "ERROR"
    exit 1
}

Write-Status "VS Code 已找到: $codeCmd"

$codeVersion = & $codeCmd --version 2>$null | Select-Object -First 1
Write-Status "VS Code 版本: $codeVersion"

# ============================================================
# 3. 检查智量通插件
# ============================================================
Write-Status "检查智量通插件..."

$extensions = & $codeCmd --list-extensions 2>$null
$pluginKeywords = @("zltyang.ly-beta-plugin", "zhiliangtong", "zlt", "ZLT")
$pluginFound = $false
$matchedPlugin = $null

foreach ($ext in $extensions) {
    foreach ($kw in $pluginKeywords) {
        if ($ext -match $kw) {
            $pluginFound = $true
            $matchedPlugin = $ext
            break
        }
    }
    if ($pluginFound) { break }
}

if ($pluginFound) {
    Write-Status "智量通插件已安装: $matchedPlugin" "OK"
} else {
    Write-Status "智量通插件未找到" "WARNING"
    $extensions | ForEach-Object { Write-Status "  - $_" }
    $exitCode = 1
}

# ============================================================
# 4. 检查 Tesseract OCR
# ============================================================
Write-Status "检查 Tesseract OCR 引擎..."

$tesseractPaths = @(
    "E:\ui_test\ocr\tesseract.exe",
    "C:\Program Files\Tesseract-OCR\tesseract.exe",
    "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
)

$tesseractFound = $false
foreach ($p in $tesseractPaths) {
    if (Test-Path $p) {
        $tesseractFound = $true
        Write-Status "Tesseract 已找到: $p" "OK"
        break
    }
}

if (-not $tesseractFound) {
    if (Test-Command "tesseract") {
        $tesseractFound = $true
        Write-Status "Tesseract 已在 PATH 中" "OK"
    }
}

if (-not $tesseractFound) {
    Write-Status "未找到 Tesseract OCR 引擎" "ERROR"
    exit 1
}

# ============================================================
# 5. 检查工作目录
# ============================================================
if (-not $Workspace) {
    Write-Status "未指定 Workspace 参数" "ERROR"
    exit 1
}

if (-not (Test-Path $Workspace)) {
    New-Item -ItemType Directory -Path $Workspace -Force | Out-Null
}
Write-Status "工作目录: $Workspace"

# ============================================================
# 6. 汇总
# ============================================================
Write-Status "=========================="
Write-Status "环境检查结果汇总:"
Write-Status "  Python:   OK"
Write-Status "  VS Code:  OK ($codeCmd)"
Write-Status "  智量通插件: $(if ($pluginFound) {'OK (' + $matchedPlugin + ')'} else {'MISSING'})"
Write-Status "  Tesseract OCR: $(if ($tesseractFound) {'OK'} else {'MISSING'})"
Write-Status "=========================="

exit $exitCode
