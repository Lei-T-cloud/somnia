import os
import socket
import sys
import threading
from pathlib import Path


def _root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def _backend() -> Path:
    if getattr(sys, "frozen", False):
        return _root()
    return _root() / "backend"


def _frontend() -> Path:
    if getattr(sys, "frozen", False):
        return _root() / "frontend"
    return _root() / "dist"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _prepare() -> None:
    backend = _backend()
    if str(backend) not in sys.path:
        sys.path.insert(0, str(backend))
    if getattr(sys, "frozen", False):
        data = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "Somnia"
        data.mkdir(parents=True, exist_ok=True)
        os.environ["SOMNIA_DATA"] = str(data)
        os.chdir(data)
    else:
        os.chdir(backend)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    os.environ["SOMNIA_DESKTOP"] = "1"
    os.environ["SOMNIA_FRONTEND"] = str(_frontend())
    import django
    from django.contrib.auth.models import User
    from django.core.management import call_command

    django.setup()
    call_command("migrate", interactive=False, verbosity=0)
    if not User.objects.filter(username="admin").exists():
        call_command("seed_demo", verbosity=0)


def _serve(port: int) -> None:
    from waitress import serve
    from config.wsgi import application

    serve(application, host="127.0.0.1", port=port, threads=8, ident="somnia")


def main() -> None:
    _prepare()
    port = _free_port()
    threading.Thread(target=_serve, args=(port,), daemon=True).start()
    url = f"http://127.0.0.1:{port}/login"
    try:
        import webview

        webview.create_window("眠栖 Somnia", url, width=1440, height=900, min_size=(1100, 720))
        webview.start()
    except Exception:
        import webbrowser

        webbrowser.open(url)
        print(f"眠栖已启动：{url}")
        threading.Event().wait()


if __name__ == "__main__":
    main()
