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
    if (-not (Test-Command "python3")) {
        Write-Status "未找到 python / python3 命令，请先在 Jenkins 节点上安装 Python 3.10+" "ERROR"
        exit 1
    }
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
    Write-Status "未找到 VS Code，常见路径均不存在" "ERROR"
    Write-Status "请管理员在 Jenkins 节点上安装 VS Code: https://code.visualstudio.com/download" "ERROR"
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
    Write-Status "已安装的扩展列表:" "INFO"
    $extensions | ForEach-Object { Write-Status "  - $_" }
    Write-Status "请在已安装智量通插件的机器上执行 'code --list-extensions' 获取准确的插件 ID" "WARNING"
    Write-Status "获取插件 ID 后，在 Jenkins 节点上手动安装: code --install-extension <publisher.name>" "WARNING"
    $exitCode = 1
}

# ============================================================
# 4. 检查 Tesseract OCR
# ============================================================
Write-Status "检查 Tesseract OCR 引擎..."

$tesseractPaths = @(
    "E:\ocr\tesseract.exe",
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
    Write-Status "请管理员在 Jenkins 节点上安装:" "ERROR"
    Write-Status "  下载地址: https://github.com/UB-Mannheim/tesseract/wiki" "ERROR"
    Write-Status "  安装后添加 bin 目录到系统 PATH，或安装到以下路径之一:" "ERROR"
    $tesseractPaths | ForEach-Object { Write-Status "    $_" }
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
Write-Status "  智量通插件: $(if ($pluginFound) {'OK (' + $matchedPlugin + ')'} else {'MISSING (需手动安装)'})"
Write-Status "  Tesseract OCR: $(if ($tesseractFound) {'OK'} else {'MISSING'})"
Write-Status "=========================="

exit $exitCode
