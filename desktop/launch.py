import os
import socket
import sys
import threading
import traceback
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


def _data_dir() -> Path:
    root = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "Somnia"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _attach_stdio(log_file: Path) -> None:
    stream = open(log_file, "a", encoding="utf-8")
    if sys.stdout is None:
        sys.stdout = stream
    if sys.stderr is None:
        sys.stderr = stream


def _alert(title: str, message: str) -> None:
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(None, message, title, 0x10)
    except Exception:
        print(message)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _prepare() -> Path:
    data = _data_dir()
    log_file = data / "startup.log"
    _attach_stdio(log_file)
    log_file.write_text("starting\n", encoding="utf-8")

    backend = _backend()
    if str(backend) not in sys.path:
        sys.path.insert(0, str(backend))

    secret = data / "secret.key"
    if secret.exists():
        os.environ["SOMNIA_SECRET_KEY"] = secret.read_text(encoding="utf-8").strip()
    else:
        import secrets

        token = secrets.token_urlsafe(48)
        secret.write_text(token, encoding="utf-8")
        os.environ["SOMNIA_SECRET_KEY"] = token

    if getattr(sys, "frozen", False):
        os.environ["SOMNIA_DATA"] = str(data)
        os.chdir(data)
    else:
        os.chdir(_backend())

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    os.environ["SOMNIA_DESKTOP"] = "1"
    os.environ["SOMNIA_FRONTEND"] = str(_frontend())

    import django
    from django.core.management import call_command

    django.setup()
    call_command("migrate", interactive=False, verbosity=0)
    call_command("init_hotel", verbosity=0)
    log_file.write_text("ready\n", encoding="utf-8")
    return data


def _serve(port: int) -> None:
    from waitress import serve
    from config.wsgi import application

    serve(application, host="127.0.0.1", port=port, threads=8, ident="somnia")


def main() -> None:
    try:
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
    except Exception:
        text = traceback.format_exc()
        try:
            (_data_dir() / "startup.log").write_text(text, encoding="utf-8")
        except Exception:
            pass
        _alert("眠栖无法启动", text[-1200:])
        raise


if __name__ == "__main__":
    main()
