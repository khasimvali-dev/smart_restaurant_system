"""
Local entry point.

    python run.py                 -> Flask dev server on http://127.0.0.1:5000
    flask run                     -> same, via the Flask CLI (needs FLASK_APP=run.py)
    waitress-serve --port=8000 run:app   -> a slightly more "production-like" local server
"""
import os
import socket
from app import create_app

app = create_app(os.getenv("FLASK_ENV", "development"))


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    if is_port_in_use(port):
        fallback_port = 5001 if port == 5000 else port + 1
        print(f"Port {port} is currently occupied; starting on http://127.0.0.1:{fallback_port}")
        port = fallback_port
    app.run(host="127.0.0.1", port=port, debug=app.config.get("DEBUG", True))
