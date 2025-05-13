from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from datetime import datetime
from .html_parser import fetch_articles
from .rewriter import rewrite_text
from .publisher import send_to_telegram
from .models import Article
from . import db
import os
import uuid
from .image_editor import process_image_from_prompt
import time

def start_scheduler(app):
    scheduler = BackgroundScheduler(timezone=pytz.timezone('Europe/Kiev'))

    @scheduler.scheduled_job('interval', minutes=120)
    def job():
        with app.app_context():
            print("🔄 Запуск: парсинг и публикация")
            fetch_articles()

            # Ensure images directory exists
            images_dir = os.path.join("static", "images")
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)

            now = datetime.now(pytz.timezone('Europe/Kiev'))
            articles = Article.query.filter(
                Article.is_posted == False,
                Article.publish_at != None,
                Article.publish_at <= now
            ).all()

            for idx, article in enumerate(articles):
                try:
                    # Задержка публикации между статьями
                    if idx > 0:
                        print(f"[LOG] ⏳ Ожидание 20 минут перед публикацией следующей статьи...")
                        time.sleep(20 * 60)  # 20 минут

                    rewritten = rewrite_text(article.original_text)
                    article.rewritten_text = rewritten

                    filename = f"img_{uuid.uuid4().hex}.jpg"
                    image_path = os.path.join("static", "images", filename)
                    article.image_path = process_image_from_prompt(rewritten, image_path)

                    send_to_telegram(rewritten, article.image_path)
                    article.is_posted = True
                    db.session.commit()
                except Exception as e:
                    print(f"[!] Ошибка обработки статьи: {e}")

    scheduler.start()
