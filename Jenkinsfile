pipeline {
    agent { label 'windows' }

    triggers {
        cron('H 2 * * *')
    }

    environment {
        PYTHONIOENCODING = 'utf-8'
        ALLURE_RESULTS   = 'reports/allure_results'
        TZ               = 'Asia/Shanghai'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '30'))
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Environment Setup') {
            steps {
                script {
                    def workspace = pwd()
                    // 使用内联 PowerShell 脚本，避免 .ps1 文件编码/换行符问题
                    powershell """
                        \$ErrorActionPreference = "Stop"
                        \$exitCode = 0

                        function Write-Status {
                            param([string]\$Message, [string]\$Status = "INFO")
                            \$ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                            Write-Host "[\$ts] [\$Status] \$Message"
                        }

                        function Test-Command {
                            param([string]\$Command)
                            try {
                                \$null = Get-Command \$Command -ErrorAction Stop
                                return \$true
                            } catch {
                                return \$false
                            }
                        }

                        # 1. Check Python
                        Write-Status "Checking Python..."
                        if (-not (Test-Command "python")) {
                            if (-not (Test-Command "python3")) {
                                Write-Status "python / python3 not found" "ERROR"
                                exit 1
                            }
                        }
                        \$pyVersion = python --version 2>&1
                        Write-Status "Python version: \$pyVersion"

                        if (-not (Test-Command "pip")) {
                            Write-Status "pip not found" "ERROR"
                            exit 1
                        }
                        Write-Status "pip ready"

                        # 2. Check VS Code
                        Write-Status "Checking VS Code..."
                        \$vsCodePaths = @(
                            "\$env:LOCALAPPDATA\\Programs\\Microsoft VS Code\\bin\\code.cmd",
                            "\$env:LOCALAPPDATA\\Programs\\Microsoft VS Code\\Code.exe",
                            "C:\\Program Files\\Microsoft VS Code\\bin\\code.cmd",
                            "C:\\Program Files\\Microsoft VS Code\\Code.exe",
                            "C:\\Program Files (x86)\\Microsoft VS Code\\bin\\code.cmd",
                            "C:\\Program Files (x86)\\Microsoft VS Code\\Code.exe"
                        )

                        \$codeCmd = \$null
                        foreach (\$p in \$vsCodePaths) {
                            if (Test-Path \$p) {
                                \$codeCmd = \$p
                                break
                            }
                        }

                        if (-not \$codeCmd) {
                            if (Test-Command "code") {
                                \$codeCmd = "code"
                            }
                        }

                        if (-not \$codeCmd) {
                            Write-Status "VS Code not found" "ERROR"
                            exit 1
                        }

                        Write-Status "VS Code found: \$codeCmd"
                        \$codeVersion = & \$codeCmd --version 2>\$null | Select-Object -First 1
                        Write-Status "VS Code version: \$codeVersion"

                        # 3. Check plugin
                        Write-Status "Checking ZLT plugin..."
                        \$extensions = & \$codeCmd --list-extensions 2>\$null
                        \$pluginKeywords = @("zltyang.ly-beta-plugin", "zhiliangtong", "zlt", "ZLT")
                        \$pluginFound = \$false
                        \$matchedPlugin = \$null

                        foreach (\$ext in \$extensions) {
                            foreach (\$kw in \$pluginKeywords) {
                                if (\$ext -match \$kw) {
                                    \$pluginFound = \$true
                                    \$matchedPlugin = \$ext
                                    break
                                }
                            }
                            if (\$pluginFound) { break }
                        }

                        if (\$pluginFound) {
                            Write-Status "ZLT plugin installed: \$matchedPlugin" "OK"
                        } else {
                            Write-Status "ZLT plugin not found" "WARNING"
                            \$extensions | ForEach-Object { Write-Status "  - \$_" }
                            \$exitCode = 1
                        }

                        # 4. Check Tesseract
                        Write-Status "Checking Tesseract OCR..."
                        \$tesseractPaths = @(
                            "E:\\ocr\\tesseract.exe",
                            "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
                            "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
                        )

                        \$tesseractFound = \$false
                        foreach (\$p in \$tesseractPaths) {
                            if (Test-Path \$p) {
                                \$tesseractFound = \$true
                                Write-Status "Tesseract found: \$p" "OK"
                                break
                            }
                        }

                        if (-not \$tesseractFound) {
                            if (Test-Command "tesseract") {
                                \$tesseractFound = \$true
                                Write-Status "Tesseract in PATH" "OK"
                            }
                        }

                        if (-not \$tesseractFound) {
                            Write-Status "Tesseract not found" "ERROR"
                            exit 1
                        }

                        # 5. Check workspace
                        \$ws = "${workspace}"
                        if (-not \$ws) {
                            Write-Status "Workspace not set" "ERROR"
                            exit 1
                        }
                        if (-not (Test-Path \$ws)) {
                            New-Item -ItemType Directory -Path \$ws -Force | Out-Null
                        }
                        Write-Status "Workspace: \$ws"

                        # 6. Summary
                        Write-Status "=========================="
                        Write-Status "Summary:"
                        Write-Status "  Python:    OK"
                        Write-Status "  VS Code:   OK"
                        Write-Status "  ZLT Plugin: $(if (\$pluginFound) {'OK'} else {'MISSING'})"
                        Write-Status "  Tesseract: $(if (\$tesseractFound) {'OK'} else {'MISSING'})"
                        Write-Status "=========================="

                        exit \$exitCode
                    """
                }
            }
        }

        stage('Install Python Dependencies') {
            steps {
                bat 'pip install -r requirements.txt'
                bat 'playwright install chromium'
            }
        }

        stage('Run Tests') {
            steps {
                withCredentials([
                    string(credentialsId: 'zlt-phone', variable: 'ZLT_PHONE'),
                    string(credentialsId: 'zlt-password', variable: 'ZLT_PASSWORD'),
                    string(credentialsId: 'zlt-feishu-webhook', variable: 'ZLT_FEISHU_WEBHOOK')
                ]) {
                    bat 'python main.py'
                }
            }
        }

        stage('Generate Allure Report') {
            steps {
                bat 'allure generate reports/allure_results -o reports/allure_report --clean || echo allure-cli not found, skipping html generation'
            }
        }
    }

    post {
        always {
            // 注意：不要在这里加 node()，否则当前构建占着 executor 又等新的 executor，会导致死锁
            allure([
                includeProperties: false,
                jdk: '',
                properties: [],
                reportBuildPolicy: 'ALWAYS',
                results: [[path: 'reports/allure_results']]
            ])
            archiveArtifacts artifacts: 'reports/allure_report/**,logs/*.log,screenshots/*.png', allowEmptyArchive: true
        }
        failure {
            script {
                def feishuWebhook = env.ZLT_FEISHU_WEBHOOK ?: ''
                if (feishuWebhook) {
                    powershell """
                        \$body = @{
                            msg_type = 'text'
                            content  = @{ text = "[Jenkins] ZLT automation test failed\nBuild: ${env.BUILD_URL}\nBranch: ${env.BRANCH_NAME}\nTime: ${new Date()}" }
                        } | ConvertTo-Json -Depth 3
                        Invoke-RestMethod -Uri '${feishuWebhook}' -Method Post -ContentType 'application/json; charset=utf-8' -Body \$body
                    """
                }
            }
        }
    }
}
