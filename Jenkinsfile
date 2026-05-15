pipeline {
    agent { label 'windows' }

    triggers {
        cron('25 18 * * *')
    }

    environment {
        PYTHONIOENCODING = 'utf-8'
        ALLURE_RESULTS   = 'reports/allure_results'
        TZ               = 'Asia/Shanghai'
        // 强制 Jenkins Java 进程使用 UTF-8 编码读取命令输出
        JAVA_TOOL_OPTIONS = '-Dfile.encoding=UTF-8'
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
                    bat 'if exist reports\\allure_results rmdir /s /q reports\\allure_results'
                    bat 'if exist reports\\allure_report rmdir /s /q reports\\allure_report'
                    bat 'if exist allure-report rmdir /s /q allure-report'

                    echo "Python:"
                    bat 'python --version'
                    echo "VS Code:"
                    bat 'code --version'
                    echo "Tesseract:"
                    bat 'tesseract --version || echo Tesseract not in PATH, will use full path'
                }
            }
        }

        stage('安装 Python 依赖') {
            steps {
                bat 'python -m pip install --upgrade pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com'
                bat 'python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com'
                bat 'python -m playwright install chromium'
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
