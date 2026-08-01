# 🚀 XianyuAgent - 智能闲鱼客服机器人系统

[Python Version](https://www.python.org/) [LLM Powered](https://platform.openai.com/)

专为闲鱼平台打造的AI值守解决方案，实现闲鱼平台7×24小时自动化值守，支持多专家协同决策、智能议价和上下文感知对话。 

## 🌟 核心特性

### 智能对话引擎


| 功能模块  | 技术实现            | 关键特性                                      |
| ----- | --------------- | ----------------------------------------- |
| 上下文感知 | 会话历史存储          | 轻量级对话记忆管理，完整对话历史作为LLM上下文输入                |
| 专家路由  | LLM prompt+规则路由 | 基于提示工程的意图识别 → 专家Agent动态分发，支持议价/技术/客服多场景切换 |


### 业务功能矩阵


| 模块   | 已实现               | 规划中                |
| ---- | ----------------- | ------------------ |
| 核心引擎 | ✅ LLM自动回复 ✅ 上下文管理 | 🔄 情感分析增强          |
| 议价系统 | ✅ 阶梯降价策略          | 🔄 市场比价功能          |
| 技术支持 | ✅ 网络搜索整合          | 🔄 RAG知识库增强        |
| 运维监控 | ✅ 基础日志            | 🔄 钉钉集成 🔄 Web管理界面 |


## 🎨效果图

  
*图1: 客服随叫随到*

  
*图2: 阶梯式议价*

  
*图3: 技术专家上场*

  
*图4: 后台log*

## 🚴 快速开始

### 环境要求

- Python 3.8+

### 安装步骤

```bash
1. 克隆仓库
git clone https://github.com/shaxiu/XianyuAutoAgent.git
cd XianyuAutoAgent

2. 安装依赖
pip install -r requirements.txt

3. 配置环境变量
创建一个 `.env` 文件，包含以下内容，也可直接重命名 `.env.example` ：
#必配配置
API_KEY=apikey通过模型平台获取
COOKIES_STR=填写网页端获取的cookie
MODEL_BASE_URL=模型地址
MODEL_NAME=模型名称
#可选配置
TOGGLE_KEYWORDS=接管模式切换关键词，默认为句号（输入句号切换为人工接管，再次输入则切换AI接管）
SIMULATE_HUMAN_TYPING=True/False #模拟人工回复延迟
DEVICE_ID=通常留空即可；仅在需要与网页请求使用同一设备标识时手动配置
CHROME_MAJOR_VERSION=可留空自动检测，也可以填写本机Chrome主版本（例如150）
BROWSER_USER_AGENT=可选，留空时根据Chrome主版本自动生成
BROWSER_ACCEPT_LANGUAGE=zh-CN,zh;q=0.9,en;q=0.8
RISK_CONTROL_RETRY_INTERVAL=1800 #遇到服务端用户校验后的暂停秒数

注意：默认使用的模型是通义千问，如需使用其他API，请自行修改.env文件中的模型地址和模型名称；
COOKIES_STR自行在闲鱼网页端获取cookies(网页端F12打开控制台，选择Network，点击Fetch/XHR,点击一个请求，查看cookies)
遇到 `FAIL_SYS_USER_VALIDATE` 时程序不会循环请求或自动处理验证码，而是按 `RISK_CONTROL_RETRY_INTERVAL` 暂停，避免短时间重试加重风控。

4. 创建提示词文件prompts/*_prompt.txt（也可以直接将模板名称中的_example去掉），否则默认读取四个提示词模板中的内容
```

### 使用方法

运行主程序：

```bash
python main.py
```

### 自定义提示词

可以通过编辑 `prompts` 目录下的文件来自定义各个专家的提示词：

- `classify_prompt.txt`: 意图分类提示词
- `price_prompt.txt`: 价格专家提示词
- `tech_prompt.txt`: 技术专家提示词
- `default_prompt.txt`: 默认回复提示词

