# Win11 搭建 Jenkins CI/CD 全流程文档

## 一、环境准备

### 1.1 必备软件清单

| 软件 | 版本要求 | 下载/安装方式 | 用途 |
|------|---------|-------------|------|
| Java JDK | 17+ | https://adoptium.net | Jenkins 运行依赖 |
| Python | 3.10+ | https://python.org | 测试脚本运行环境 |
| VS Code | 最新版 | https://code.visualstudio.com | 被测目标应用（智量通插件载体） |
| Tesseract | 5.5+ | https://github.com/UB-Mannheim/tesseract/wiki | OCR 图像识别 |
| Git | 2.40+ | https://git-scm.com | 代码拉取 |
| Allure CLI | 2.24+ | 可选（Jenkins Allure 插件已内置） | 报告生成 |

### 1.2 Python 依赖安装

```powershell
pip install -r requirements.txt
python -m playwright install chromium
```

requirements.txt 内容：
```
faker>=37.0.0
playwright>=1.40.0
pyautogui>=0.9.54
pyperclip>=1.8.2
requests>=2.31.0
pytesseract>=0.3.10
Pillow>=10.0.0
```

---

## 二、Jenkins Master 部署

### 2.1 下载并启动 Jenkins

```powershell
# 1. 下载 war 包到 E 盘
# 2. 设置主目录环境变量（将 Jenkins 数据放到 E 盘）
$env:JENKINS_HOME="E:\JenkinsHome"

# 3. 启动 Jenkins
java -Dfile.encoding=UTF-8 -jar jenkins.war --httpPort=8080
```

> **为什么要加 `-Dfile.encoding=UTF-8`？**
> 不加这个参数，Jenkins 控制台日志中的中文会显示为乱码（GBK 解码 UTF-8 字节）。

### 2.2 初始化配置

1. 浏览器打开 `http://localhost:8080`
2. 输入初始密码（控制台输出或 `E:\JenkinsHome\secrets\initialAdminPassword`）
3. 安装推荐插件，确保以下插件已安装：
   - **Pipeline**（流水线）
   - **Allure Jenkins Plugin**（Allure 报告）
   - **Timestamper**（时间戳）
   - **Workspace Cleanup**（工作区清理）

---

## 三、Jenkins Agent（Windows 节点）配置

### 3.1 创建 Agent 节点

1. Jenkins 页面 → Manage Jenkins → Nodes → New Node
2. 节点名称：`windows-agent`
3. 类型：Permanent Agent
4. 配置：
   - **远程根目录**：`C:\Jenkins`（或 `E:\Jenkins`，迁移时改这里）
   - **标签**：`windows`
   - **启动方式**：Launch agent by connecting it to the controller
   - **用法**：Only build jobs with label expressions matching this node

### 3.2 启动 Agent（关键：编码参数）

在 Agent 服务器上，用 **PowerShell** 执行：

```powershell
cd C:\Users\zltweb   # 放 agent.jar 的目录
java --% -Dfile.encoding=UTF-8 -Dsun.stdout.encoding=UTF-8 -Dsun.stderr.encoding=UTF-8 -jar agent.jar -url http://localhost:8080/ -secret <你的secret> -name "windows-agent" -webSocket -workDir "C:\Jenkins"
```

> **注意**：
> - `--%` 是 PowerShell 的停止解析标记，防止 `-D` 参数被误解
> - 三个编码参数缺一不可，否则 Jenkins 控制台中文乱码
> - 建议把命令保存为 `start-agent.bat`，方便以后启动

### 3.3 持久化启动脚本

创建 `C:\start-agent.bat`：

```bat
@echo off
chcp 65001 >nul
cd /d C:\Users\zltweb
java -Dfile.encoding=UTF-8 -Dsun.stdout.encoding=UTF-8 -Dsun.stderr.encoding=UTF-8 -jar agent.jar -url http://localhost:8080/ -secret <你的secret> -name "windows-agent" -webSocket -workDir "C:\Jenkins"
```

---

## 四、Jenkins 凭据配置（关键）

Jenkinsfile 中引用了三个凭据，必须在 Jenkins 中提前创建：

### 4.1 添加凭据路径

**Manage Jenkins → Manage Credentials → (global) → Add Credentials**

### 4.2 三个凭据详情

| 凭据类型 | ID（严格匹配） | Secret 内容 | 用途 |
|---------|--------------|------------|------|
| Secret text | `zlt-phone` | 登录手机号 | 智量通账号登录 |
| Secret text | `zlt-password` | 登录密码 | 智量通账号登录 |
| Secret text | `zlt-feishu-webhook` | 飞书机器人 Webhook URL | 构建失败通知 |

> **类型必须是 Secret text**，不能选 Username with password。因为 Jenkinsfile 中使用的是 `string(credentialsId: '...', variable: '...')`，与 Secret text 对应。

---

## 五、Jenkinsfile 说明

当前项目使用声明式 Pipeline，核心配置：

```groovy
pipeline {
    agent { label 'windows' }

    triggers {
        cron('0 16 * * *')   // 每天北京时间 16:00 自动执行
    }

    environment {
        PYTHONIOENCODING = 'utf-8'
        ALLURE_RESULTS   = 'reports/allure_results'
        TZ               = 'Asia/Shanghai'
        JAVA_TOOL_OPTIONS = '-Dfile.encoding=UTF-8'
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
        timestamps()
    }

    stages {
        stage('检出代码')      { ... }
        stage('环境准备')      { ... }
        stage('安装 Python 依赖') { ... }
        stage('运行测试')      { ... }   // 核心：执行 python main.py
    }

    post {
        always {
            allure([...])           // Allure 插件自动生成报告
            archiveArtifacts(...)   // 归档日志和截图
        }
        failure {
            // 飞书通知（仅失败时）
        }
    }
}
```

### 5.1 定时触发说明

- `cron('0 16 * * *')` — 每天 16:00 执行
- 配合 `TZ = 'Asia/Shanghai'`，时间是北京时间
- 如需改为其他时间：
  - 每天 9:00：`cron('0 9 * * *')`
  - 每小时：`cron('0 * * * *')`
  - 工作日 10:00：`cron('0 10 * * 1-5')`

---

## 六、项目配置（settings.py）

运行前检查 `config/settings.py` 中的路径配置：

```python
# VS Code 路径（根据实际安装位置修改）
VS_CODE_PATH = _env("ZLT_VS_CODE_PATH", r"E:\Microsoft VS Code\Code.exe")

# 登录信息（Jenkins 环境中通过环境变量覆盖）
PHONE = _env("ZLT_PHONE", "18162428572")
PASSWORD = _env("ZLT_PASSWORD", "111111")
```

Jenkins 运行时，凭据会通过环境变量注入，本地调试可直接改默认值。

---

## 七、常见问题与解决方案

### 问题 1：Could not find credentials entry with ID 'zlt-phone'

**原因**：Jenkins 凭据管理中缺少对应 ID 的凭据。

**解决**：按第 4 章添加三个 Secret text 凭据，ID 必须严格匹配。

---

### 问题 2：Jenkins 控制台中文乱码

**现象**：`自动化测试开始` 显示为 `鑷姩鍖栨祴璇曞紑濮�`

**原因**：Jenkins Agent 的 Java 进程使用 GBK 编码读取命令输出。

**解决**：启动 Agent 时必须加三个编码参数：
```
-Dfile.encoding=UTF-8 -Dsun.stdout.encoding=UTF-8 -Dsun.stderr.encoding=UTF-8
```

PowerShell 中用 `--%` 防止参数被解析：
```powershell
java --% -Dfile.encoding=UTF-8 -Dsun.stdout.encoding=UTF-8 -Dsun.stderr.encoding=UTF-8 -jar agent.jar ...
```

---

### 问题 3：Finished: FAILURE 但 Allure 报告已生成

**现象**：构建状态 FAILURE，但 Allure 报告页面正常显示。

**原因**：Jenkinsfile 的 `stage('生成 Allure 报告')` 中执行了 `allure generate` 命令，但系统 PATH 中没有 allure CLI，导致 exit code 1。而 `post` 中的 Allure 插件使用的是 Jenkins 内置的 allure.bat，能正常生成。

**解决**：删除 Jenkinsfile 中重复的 `stage('生成 Allure 报告')`，只保留 `post` 中的 Allure 插件调用。

---

### 问题 4：allure-cli not found

**现象**：`'allure' 不是内部或外部命令`

**解决**：不需要手动安装 allure-cli。Jenkins Allure 插件已内置 allure.bat，通过 `post { allure([...]) }` 即可生成报告。如需本地查看报告，可单独安装 Allure CLI。

---

### 问题 5：日志文件在哪里

| 类型 | 路径 |
|------|------|
| 构建日志 | Jenkins 构建页面 → Console Output |
| 测试日志文件 | `C:\Jenkins\workspace\zlt_vscode\logs\YYYYMMDD.log` |
| 页面截图 | `C:\Jenkins\workspace\zlt_vscode\screenshots\` |
| Allure 结果 | `C:\Jenkins\workspace\zlt_vscode\reports\allure_results\` |
| Allure HTML 报告 | `C:\Jenkins\workspace\zlt_vscode\allure-report\` |

---

## 八、迁移 Jenkins 到 E 盘

### 8.1 Master 主目录迁移

```powershell
# 1. 停止 Jenkins
taskkill /F /IM java.exe

# 2. 复制数据
robocopy "C:\Users\zltweb\.jenkins" "E:\JenkinsHome" /E /COPY:DAT

# 3. 以后用这个命令启动
$env:JENKINS_HOME="E:\JenkinsHome"
java -Dfile.encoding=UTF-8 -jar jenkins.war --httpPort=8080
```

### 8.2 Agent 工作目录迁移

修改启动命令中的 `-workDir`：
```powershell
java --% ... -workDir "E:\Jenkins"
```

同时修改 Jenkins 节点配置：
- Manage Jenkins → Nodes → windows-agent → Configure
- **远程根目录**：改为 `E:\Jenkins`

---

## 九、完整启动检查清单

首次搭建或重启后，按此清单检查：

- [ ] Java 已安装（`java -version`）
- [ ] Python 已安装（`python --version`）
- [ ] VS Code 已安装（`code --version`）
- [ ] Tesseract 已安装（`tesseract --version`）
- [ ] Jenkins Master 已启动（`http://localhost:8080` 可访问）
- [ ] Jenkins Agent 已连接（Nodes 页面显示在线）
- [ ] Agent 启动命令包含 UTF-8 编码参数
- [ ] 三个凭据（zlt-phone/zlt-password/zlt-feishu-webhook）已创建
- [ ] Allure Jenkins Plugin 已安装
- [ ] 项目代码已推送到 GitHub
- [ ] Jenkins Job 已创建并关联 Git 仓库
- [ ] 手动触发一次构建，确认通过
- [ ] 检查 Allure 报告页面正常显示
- [ ] 检查日志中文无乱码

---

## 十、相关文件位置

| 文件 | 路径 | 说明 |
|------|------|------|
| Jenkinsfile | 项目根目录 | 流水线定义 |
| requirements.txt | 项目根目录 | Python 依赖 |
| config/settings.py | `config/settings.py` | 项目配置 |
| core/logger.py | `core/logger.py` | 日志模块 |
| 测试用例 | `cases/` 目录 | 自动化测试用例 |
