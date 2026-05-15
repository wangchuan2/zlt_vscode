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
        stage('检出代码') {
            steps {
                checkout scm
            }
        }

        stage('环境准备') {
            steps {
                script {
                    def workspace = pwd()
                    echo "Workspace: ${workspace}"

                    echo "清理旧报告数据..."
                    bat 'chcp 65001 >nul && if exist reports\\allure_results rmdir /s /q reports\\allure_results'
                    bat 'chcp 65001 >nul && if exist reports\\allure_report rmdir /s /q reports\\allure_report'
                    bat 'chcp 65001 >nul && if exist allure-report rmdir /s /q allure-report'

                    echo "Python:"
                    bat 'chcp 65001 >nul && python --version'
                    echo "VS Code:"
                    bat 'chcp 65001 >nul && code --version'
                    echo "Tesseract:"
                    bat 'chcp 65001 >nul && tesseract --version || echo Tesseract not in PATH, will use full path'
                }
            }
        }

        stage('安装 Python 依赖') {
            steps {
                bat 'chcp 65001 >nul && python -m pip install --upgrade pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com'
                bat 'chcp 65001 >nul && python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com'
                bat 'chcp 65001 >nul && python -m playwright install chromium'
            }
        }

        stage('运行测试') {
            steps {
                withCredentials([
                    string(credentialsId: 'zlt-phone', variable: 'ZLT_PHONE'),
                    string(credentialsId: 'zlt-password', variable: 'ZLT_PASSWORD'),
                    string(credentialsId: 'zlt-feishu-webhook', variable: 'ZLT_FEISHU_WEBHOOK')
                ]) {
                    bat 'chcp 65001 >nul && python main.py'
                }
            }
        }

        stage('生成 Allure 报告') {
            steps {
                bat 'chcp 65001 >nul && allure generate reports/allure_results -o reports/allure_report --clean || echo allure-cli not found, skipping html generation'
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
