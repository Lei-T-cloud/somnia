import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .database import Base, SessionLocal, engine
from .hotel import tick_hotel
from .routers import auth, guests, rooms
from .seed import seed_if_empty


async def simulation_loop() -> None:
    while True:
        db = SessionLocal()
        try:
            tick_hotel(db)
        finally:
            db.close()
        await asyncio.sleep(1.2)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    task = asyncio.create_task(simulation_loop())
    yield
    task.cancel()


app = FastAPI(title="眠栖 Somnia API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix="/api")
app.include_router(guests.router, prefix="/api")
app.include_router(rooms.router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>眠栖 Somnia API</title>
  <style>
    body { margin: 0; font-family: sans-serif; background: #070b12; color: #e8eef6; }
    main { max-width: 720px; margin: 12vh auto; padding: 0 24px; }
    a { color: #3ec7ff; }
    code { color: #f0b429; }
    p { color: #8b97a8; line-height: 1.6; }
  </style>
</head>
<body>
  <main>
    <p>眠栖 Somnia · 后端已启动</p>
    <h1>这是 API 服务，不是前端页面</h1>
    <p>界面请打开前端：<a href="http://127.0.0.1:5174/">http://127.0.0.1:5174/</a>（若 5173 可用则用 5173）</p>
    <p>接口文档：<a href="/docs">/docs</a>　·　健康检查：<a href="/api/health">/api/health</a></p>
    <p>请通过前台页面注册或登录后使用。</p>
  </main>
</body>
</html>"""


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "service": "somnia"}
