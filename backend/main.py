import hashlib
import hmac
import os
from urllib.parse import unquote, parse_qs
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from models import (
    init_db,
    TaskCreate,
    TaskEdit,
    create_task_db,
    get_tasks_db,
    complete_task_db,
    edit_task_db,
    delete_task_db,
)
from notifier import send_completion_notification

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

app = FastAPI(title="To-Do Telegram Mini App API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files (from dist/)
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist")

if os.path.isdir(FRONTEND_DIR):
    @app.get("/todo")
    async def serve_todo():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    # Mount assets if any
    assets_dir = os.path.join(FRONTEND_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


def verify_telegram_init_data(init_data: str) -> dict:
    """Verify Telegram WebApp initData signature."""
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        # Dev mode: skip verification
        parsed = parse_qs(init_data)
        user_raw = parsed.get("user", [None])[0]
        if user_raw:
            import json
            try:
                return json.loads(user_raw)
            except json.JSONDecodeError:
                pass
        return {"id": "dev_user", "first_name": "Developer"}

    # Parse init data
    parsed = parse_qs(init_data)
    received_hash = parsed.pop("hash", [None])[0]
    if not received_hash:
        raise HTTPException(status_code=401, detail="Missing hash in initData")

    # Build data check string
    data_check_string = "\n".join(
        f"{k}={v[0]}" for k, v in sorted(parsed.items())
    )

    # Compute secret key
    secret_key = hmac.new(
        b"WebAppData",
        BOT_TOKEN.encode(),
        hashlib.sha256,
    ).digest()

    # Compute hash
    computed_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    if computed_hash != received_hash:
        raise HTTPException(status_code=401, detail="Invalid initData signature")

    # Return user data
    import json
    user_raw = parsed.get("user", [None])[0]
    if user_raw:
        return json.loads(user_raw)
    return {"id": "unknown"}


def get_user_id_from_init_data(init_data: str) -> str:
    """Extract user ID from initData."""
    user = verify_telegram_init_data(init_data)
    return str(user.get("id", "unknown"))


@app.on_event("startup")
async def startup():
    init_db()
    print("✅ Database initialized")


# --- Health check ---
@app.get("/")
async def root():
    return {"status": "ok", "app": "To-Do Telegram Mini App API"}


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# --- Task endpoints ---

@app.post("/create_task")
async def api_create_task(task: TaskCreate, request: Request):
    init_data = request.headers.get("X-Telegram-InitData", "")
    user_id = get_user_id_from_init_data(init_data)
    return create_task_db(user_id, task.text, task.reminder_date)


@app.get("/get_tasks")
async def api_get_tasks(request: Request):
    init_data = request.headers.get("X-Telegram-InitData", "")
    user_id = get_user_id_from_init_data(init_data)
    return get_tasks_db(user_id)


@app.post("/complete_task/{task_id}")
async def api_complete_task(task_id: int, request: Request):
    init_data = request.headers.get("X-Telegram-InitData", "")
    user_id = get_user_id_from_init_data(init_data)
    result = complete_task_db(task_id, user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    # If task was just completed (not uncompleted), send notification
    if result.completed:
        import asyncio
        asyncio.create_task(send_completion_notification(user_id, result.text))
    return result


@app.put("/edit_task/{task_id}")
async def api_edit_task(task_id: int, updates: TaskEdit, request: Request):
    init_data = request.headers.get("X-Telegram-InitData", "")
    user_id = get_user_id_from_init_data(init_data)
    result = edit_task_db(task_id, user_id, updates)
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return result


@app.delete("/delete_task/{task_id}")
async def api_delete_task(task_id: int, request: Request):
    init_data = request.headers.get("X-Telegram-InitData", "")
    user_id = get_user_id_from_init_data(init_data)
    ok = delete_task_db(task_id, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
