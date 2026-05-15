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

    // 解决 Windows 节点中文乱码：整体设置 UTF-8 代码页
    // 在 Jenkins 节点系统环境变量中添加：JAVA_TOOL_OPTIONS = -Dfile.encoding=UTF-8
    // 或者在每个 bat/powershell 步骤前手动执行 chcp 65001

    stages {
        stage('检出代码') {
            steps {
                checkout scm
            }
        }

        stage('环境准备') {
            steps {
                script {
                    def workspace = pwd()
                    bat "powershell -ExecutionPolicy Bypass -File scripts/setup_env.ps1 -Workspace \"${workspace}\""
                }
            }
        }

        stage('安装 Python 依赖') {
            steps {
                bat 'pip install -r requirements.txt'
                bat 'playwright install chromium'
            }
        }

        stage('运行测试') {
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

        stage('生成 Allure 报告') {
            steps {
                bat 'allure generate reports/allure_results -o reports/allure_report --clean || echo allure-cli not found, skipping html generation'
            }
        }
    }

    post {
        always {
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
                            content  = @{ text = "[Jenkins] 智量通自动化测试失败\n构建: ${env.BUILD_URL}\n分支: ${env.BRANCH_NAME}\n时间: ${new Date()}" }
                        } | ConvertTo-Json -Depth 3
                        Invoke-RestMethod -Uri '${feishuWebhook}' -Method Post -ContentType 'application/json; charset=utf-8' -Body \$body
                    """
                }
            }
        }
    }
}
