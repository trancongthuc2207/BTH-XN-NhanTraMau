import os
import django
import uvicorn
from dotenv import load_dotenv

# Load environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

HOST = os.getenv("HOST_SERVER", "127.0.0.1")
PORT = int(os.getenv("PORT_SERVER", 8000))
WORKER = int(os.getenv("WORKER", 1))
IS_USE_SSL = os.getenv("IS_USE_SSL", "0") == "1"

SSL_KEYFILE = os.path.join(BASE_DIR, "key.pem")
SSL_CERTFILE = os.path.join(BASE_DIR, "cert.pem")

# Build Uvicorn config
uvicorn_config = {
    "app": "app.asgi:application",
    "host": HOST,
    "port": PORT,
}

if IS_USE_SSL:
    if os.path.exists(SSL_KEYFILE) and os.path.exists(SSL_CERTFILE):
        uvicorn_config.update({
            "ssl_keyfile": SSL_KEYFILE,
            "ssl_certfile": SSL_CERTFILE
        })
        print("🔐 Running with SSL (HTTPS)")
    else:
        print("⚠️ SSL requested but key.pem or cert.pem not found — running without SSL (HTTP)")
else:
    print("🌐 Running without SSL (HTTP)")

# Limit workers on Windows
if os.name != "nt" and WORKER > 1:
    uvicorn_config["workers"] = WORKER

# Run
if __name__ == "__main__":
    uvicorn.run(**uvicorn_config)
