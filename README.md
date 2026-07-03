# AI 招聘提效助手

这是一个面向群面作业要求设计的全新 AI 应用 Demo，目标是在最小成本下解决 HR 在企业微信、企业微信群和腾讯在线文档之间手动记录招聘数据的问题。

Demo 聚焦一条可演示闭环：

```text
企业微信群消息 -> AI 结构化抽取 -> 招聘数据入库 -> 腾讯文档镜像同步 -> 招聘看板更新
```

## 为什么做这个项目

招聘协作中大量关键信息散落在企业微信群里，例如候选人姓名、岗位、阶段、面试时间、面试官和负责人。HR 需要把这些消息手工整理到腾讯在线文档中，容易出现录入慢、漏填、更新不及时和统计口径不一致。

本项目用 AI 将非结构化群聊消息转成结构化招聘数据，并自动同步到文档镜像表和看板，从而减少重复录入。

## 核心功能

- 企业微信群消息模拟输入
- AI 抽取候选人、岗位、学历、年限、阶段、面试时间、负责人
- 无模型 Key 时自动使用规则兜底解析，保证 Demo 可运行
- 自动同步到腾讯在线文档镜像表
- 工作台展示今日自动采集、同步总数、需人工确认数和同步动态
- 拓展能力：简历解析、智能筛选、录音转写、面试摘要与评价

## 技术栈

- 前端：Vue 3、Vite、Element Plus、ECharts
- 后端：FastAPI、SQLAlchemy、MySQL
- AI：Qwen / DashScope，规则兜底解析
- 存储拓展：MinIO、Milvus
- 文档同步：Demo 使用数据库镜像表模拟腾讯在线文档，正式落地可替换为腾讯文档 API

## 快速演示

1. 打开系统登录页。
2. 点击“演示模式登录”。
3. 进入“数据采集”页面。
4. 选择一条企业微信群示例消息。
5. 点击“AI 解析并同步”。
6. 查看 AI 抽取结果和腾讯文档镜像表新增行。
7. 回到“工作台”，查看自动采集统计和最近同步动态。

## 本地启动

### 1. 启动中间件

```powershell
docker compose up -d
```

### 2. 配置后端环境变量

复制 `backend/.env.example` 为 `backend/.env`，填写数据库配置和模型 Key。

`QWEN_API_KEY` 可以留空。留空时，数据采集 Demo 会自动使用规则兜底解析，并标记为“需人工确认”。

### 3. 启动后端

```powershell
cd backend
python -m venv venv
.\venv\Scripts\pip.exe install -r requirements.txt
cd app
..\venv\Scripts\uvicorn.exe main:app --reload --host 0.0.0.0 --port 8000
```

接口文档：`http://localhost:8000/docs`

### 4. 启动前端

```powershell
cd front
npm install
npm.cmd run dev -- --host 0.0.0.0
```

前端地址：`http://localhost:5173`

## API 示例

```http
POST /api/v1/intake/messages/parse
Content-Type: application/json
```

```json
{
  "raw_message": "@HR 张三 Java后端 3年经验 本科，简历已收，约周三14:00初面，面试官王经理",
  "source_channel": "企业微信-招聘群",
  "sender": "招聘助理"
}
```

返回结构化招聘数据，并同步到腾讯文档镜像表。

## 作业提交材料

- 方案文档：`docs/AI招聘提效落地方案.md`
- 演示讲稿：`docs/演示讲稿.md`
- 提交检查清单：`docs/提交前检查清单.md`
- 建议补充：2-3 分钟录屏或 GIF

## 正式落地方式

Demo 阶段用页面输入模拟企业微信群消息，用数据库表模拟腾讯在线文档。正式落地时：

- 企业微信侧接入群机器人 Webhook、审批回调或消息转发服务
- 腾讯文档侧替换为腾讯文档开放 API
- 用候选人手机号、简历 ID 或候选人姓名做幂等更新
- 对低置信度字段保留人工确认机制

这个方案不要求 HR 更换工作系统，只在现有企业微信和腾讯文档流程之间增加 AI 自动化同步层。
