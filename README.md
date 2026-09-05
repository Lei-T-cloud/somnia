# 眠栖 Somnia

睡眠偏好采集 + 酒店数字孪生调控平台。服从仓库根目录 `CONSTITUTION.md`。

## 桌面版（Windows）

在项目根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build-exe.ps1
```

生成文件：`release\眠栖Somnia\眠栖Somnia.exe`。双击即可，首次启动会自动建库并初始化 12 间空房。

数据目录：`%LOCALAPPDATA%\Somnia`

请在登录页用邮箱自行注册。首位酒店员工可直接注册，之后加入的员工需要邀请码（管理端右上角可复制）。该员工邮箱也可登录 SimpleUI 数据后台。

## 网页版

源码与 GitHub Pages 工作流在本仓库。Pages 只托管静态前台。登录、选房、三维调控等完整闭环请用 exe，或按下面本地启动前后端。

## 本地开发

先启动后端（必须使用 `backend/.venv`）：

```bash
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py init_hotel
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

再启动前端：

```bash
npm install
npm run dev
```

- 前台：`http://127.0.0.1:5173/`（占用时可能是 5174）
- 后台 SimpleUI：`http://127.0.0.1:8000/admin/`

## 技术栈

- 前端：Vue 3 + Vite + Pinia + Three.js / TresJS
- 后端：Django + django-simpleui + Django REST Framework + SQLite
- 桌面：Waitress + pywebview，PyInstaller 打包
