import uvicorn

from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    print("Run using 'gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker' in production.")
    uvicorn.run(app, host="127.0.0.1", port=8000)
