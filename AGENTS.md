# 眠栖 Somnia · Agent Guide

给后续实现与维护用的项目说明书。更高约束以根目录 `CONSTITUTION.md` 为准；偏离先改 Constitution，再改代码。

用户若点名 `AGENT.md`，以本文件为准。

---

## 这是什么

酒店睡眠环境平台，不是真实物联网系统。要讲清的闭环：

**偏好采集 → 场景决策 → 环境执行 → 状态反馈**

住客填睡眠偏好，规则引擎生成可执行睡眠场景；酒店管理员在三维数字孪生中看见房间并调控。环境数据来自仿真器，禁止伪装已接真实传感器。

项目名：**眠栖 Somnia**。界面简体中文。术语固定：睡眠画像、睡眠场景、数字孪生、环境仿真。

---

## 仓库地图

```
CONSTITUTION.md          宪法（必须先读）
AGENTS.md                本文件
README.md                启动与账号
src/                     Vue 3 前台
  api/client.ts          Axios，baseURL=/api，带 Bearer
  stores/                auth / guest / hotel
  engine/                前台规则与着色（展示用）
  views/login            双角色入口
  views/guest            住客左导航：偏好 / 选房 / 服务
  views/manager          管理左导航：运维指挥舱 / 实景更新 / 用户需求
  components/manager     温度查询、快照、调控、总览、Three.js
backend/                 Django 后台
  .venv/                 必须使用的虚拟环境
  config/                Django 工程与 SimpleUI 配置
  hotel/                 模型、Admin、DRF 风格 /api
  app/engine/            服务端规则引擎与环境仿真（权威）
  manage.py / run.py
```

不要把演示数据写进 `backend/.venv`。不要提交 `*.db`、`node_modules`、`dist`。

---

## 技术栈（必须遵守）

**前台**

- Vue 3 + TypeScript + Vite
- Vue Router 4：`guest` / `manager` 守卫
- Pinia：会话、住客目录、房间状态（状态来自 API，不回退 localStorage 权威源）
- Three.js + TresJS：程序化 3 层 12 房，禁止把管理端主界面做成纯表格
- Element Plus + ECharts
- Axios 经 Vite 代理访问 `http://127.0.0.1:8000/api`

**后台**

- Python 3.11，**先激活/使用 `backend/.venv`，再装依赖或跑服务**
- Django + django-simpleui + Django REST Framework + SQLite
- SimpleUI 只做数据管理（`/admin/`），不是酒店管理端主界面
- 规则引擎与房间仿真以 `backend/app/engine/` 为准；前台 `src/engine/` 仅用于着色与展示

已废弃：FastAPI、SQLAlchemy、纯 localStorage 演示后端。不要把它们加回来，除非先改 Constitution。

---

## 界面与信息架构

**前台**

- `/login`：用户 / 酒店管理人员双入口
- 住客左侧导航：`/guest/preference` 用户偏好（确认上传，不展示生成睡眠画像）、`/guest/rooms` 房间选择、`/guest/services` 酒店服务
- 房间选择：右侧三维模型；选中后右上角实景图、右下角确认选择
- 管理端左侧导航：点「酒店运维」进 `/manager/twin` 三维指挥舱；点展开后才出现「实时温湿」「实时监控」。另有 `/manager/rooms` 房间实景更新、`/manager/requests` 用户需求
- 实时温湿指挥舱
  - 中：三维幕布（模型居中，可正视/斜视/俯视）
  - 左：温度查询列表 + 趋势/快照
  - 右：房间调控 + 运行总览
  - 底：仿真播放/暂停
- 实时监控：主区走廊实况墙（当前楼道大画面 + 1F/2F/3F 缩略）；点楼道或三维摄像机会切换焦点并高亮走廊范围；本机摄像头接到当前楼道。禁止客房内监控。
- 住客上传偏好后立即绑定已选房间，管理端轮询刷新

点选房间必须左右面板与三维高亮联动。房间调控不要盖住幕布中央模型。

**后台 SimpleUI**

- `/admin/`：住户偏好、客户选房、睡眠偏好、上传流水、服务需求、客房实景、服务目录、前台账号（客户账号 / 酒店管理员账号）、仿真状态
- 住户偏好只保留申请过的人、同一人只留最后一次；客户选房单独记录选房并标记已入住/已退房
- 不得用 SimpleUI 表格替代 `/manager/twin` 的三维主界面

酒店规模固定：1 栋 3 层 × 4 间 = 12 间（101–104、201–204、301–304）。

---

## API（前台依赖，路径不要改）

前缀 `/api`。需要登录的接口带 `Authorization: Bearer <token>`。错误体为 `{ "detail": "中文原因" }`。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/auth/captcha` | 登录图形验证码 |
| POST | `/auth/email-code` | `{ email, purpose }` 向真实邮箱发送验证码 |
| POST | `/auth/login` | `{ email, password, captchaId, captcha }` |
| POST | `/auth/register` | `{ email, password, nickname, role, emailCode }` |
| GET | `/hotel/staff` | 主管理员：数据后台账号审核 |
| POST | `/hotel/staff/{email}/review` | `{ approved }` 同意或拒绝数据后台账号 |
| GET | `/auth/me` | |
| POST | `/auth/logout` | |
| GET | `/guests` | |
| POST | `/guests/ensure` | |
| PUT | `/guests/{email}/preference` | 服务端静默生成画像，并立即绑定已选房间 |
| POST | `/guests/{email}/select-room` | `{ roomId }` 住客确认选房 |
| PUT | `/guests/{email}/services` | `{ serviceIds }` 提交酒店服务 |
| GET | `/services` | 酒店服务目录 |
| GET | `/rooms` | 含 `photoUrl` |
| PATCH | `/rooms/{id}/devices` | 管理员 |
| POST | `/rooms/{id}/bind` | `{ email }` 或空 |
| POST | `/rooms/{id}/apply-scene` | 一键应用睡眠场景 |
| POST | `/rooms/{id}/photo` | 管理员上传实景图（multipart `file`） |
| GET | `/hotel/overview` `/hotel/trend` | |
| GET | `/hotel/service-requests` | 管理员：按房间的服务需求（含完成状态） |
| POST | `/hotel/service-requests/{roomId}/complete` | `{ completed }` 标记该房服务完成与否 |
| POST | `/hotel/simulation` | `{ running }` |
| GET | `/health` | |

角色字段只有 `guest | manager | backend`。前端路由与后端都要校验。

---

## 账号

不预置演示账号。住客与酒店员工都通过 `/login` 用邮箱自行注册。

- 住客 / 酒店员工：真实邮箱注册，邮箱验证码；登录需图形验证码
- 数据后台：注册后须主管理员在 SimpleUI「数据后台账号」中同意
- 发信：SimpleUI「发信设置」填写 SMTP 授权码后才能寄出验证码
- 初始化：`backend/.venv/Scripts/python.exe manage.py init_hotel`

---

## 启动

```bash
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py init_hotel
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

```bash
npm install
npm run dev
```

前台默认 `http://127.0.0.1:5173/`（占用时可能是 5174）。后台 `http://127.0.0.1:8000/admin/`。

---

## 改代码时

- 先闭环，后扩张。新功能必须落在四步闭环之一。
- 智能决策用可解释规则引擎，首期不接大模型。
- 仿真器逐步逼近目标温度/湿度；文案写「环境仿真」，不写真实传感器/摄像头。
- 三维继续用程序化几何；`gltf` 只预留，不作为依赖。
- 中文 UI。正式注册登录，不预置演示账号。
- **首期不做**：真实支付、OTA 预订、工单、真实 MQTT、多酒店集团权限、原生 App。
- 不要更新 git config，不要在未要求时 commit / push。
- 不要编辑用户的 plan 文件。

产品叙事保持一句：住客填偏好并选房/服务 → 生成睡眠场景 → 管理员在三维酒店中看见并一键适配/微调。
