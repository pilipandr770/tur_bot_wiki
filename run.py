import logging
from app import create_app
from app.scheduler import start_scheduler

logging.basicConfig(level=logging.INFO)
app = create_app()
start_scheduler(app)

logging.info("🤖 Бот запущен. Ждём публикации...")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
