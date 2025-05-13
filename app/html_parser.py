import requests
from bs4 import BeautifulSoup
from .models import Article
from . import db
from datetime import datetime
import pytz
import time

SPA_TOWNS_URL = 'https://en.wikipedia.org/wiki/List_of_spa_towns'

def fetch_soup(url):
    """Fetch a URL and return a BeautifulSoup object."""
    resp = requests.get(url)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, 'html.parser')

def parse_spa_towns():
    """
    Parse the Wikipedia "List of spa towns" page and return
    a deduplicated list of (name, url) tuples for spa towns.
    """
    soup = fetch_soup(SPA_TOWNS_URL)
    content = soup.find('div', id='mw-content-text')
    spa_towns = []
    for ul in content.find_all('ul'):
        for li in ul.find_all('li', recursive=False):
            a = li.find('a', href=True)
            if a and a['href'].startswith('/wiki/') and not a['href'].startswith('/wiki/List_of_'):
                name = a.get_text(strip=True)
                url = 'https://en.wikipedia.org' + a['href']
                if name:
                    spa_towns.append((name, url))
    # Deduplicate while preserving order
    seen = set()
    unique_towns = []
    for name, url in spa_towns:
        if name not in seen:
            seen.add(name)
            unique_towns.append((name, url))
    return unique_towns

def parse_town_intro(town_name):
    """
    Given a spa town name, fetch its Wikipedia page and return
    the first non-empty paragraph of the introduction.
    """
    town_url = 'https://en.wikipedia.org/wiki/' + town_name.replace(' ', '_')
    try:
        soup = fetch_soup(town_url)
    except requests.HTTPError:
        return ''

    content = soup.find('div', id='mw-content-text')
    if not content:
        return ''

    for p in content.find_all('p'):
        text = p.get_text().strip()
        if text:
            return text

    return ''

def fetch_articles():
    """
    Парсит spa-города с Википедии и сохраняет их introduction в базу Article.
    Вызывается шедулером.
    """
    print("[LOG] 🔍 Парсинг spa-курортов с Википедии...")
    towns = parse_spa_towns()
    print(f"[LOG] Найдено {len(towns)} городов.")
    for idx, (town, url) in enumerate(towns, 1):
        print(f"[{idx}/{len(towns)}] {town}")
        intro = parse_town_intro(town)
        if len(intro) < 50:
            print(f"[LOG] ✂️ Пропущено (слишком короткое вступление): {town}")
            continue
        content = f"{town}\n\n{intro}"
        if Article.query.filter_by(original_text=content).first():
            print(f"[LOG] 🔁 Уже есть в БД: {town}")
            continue
        article = Article(
            original_text=content,
            source_name="Wikipedia",
            publish_at=datetime.now(pytz.timezone("Europe/Kiev"))
        )
        db.session.add(article)
        print(f"[LOG] ✅ Добавлено в БД: {town}")
        time.sleep(1)
    db.session.commit()
    print("[LOG] ✅ Парсинг завершён и все новые статьи сохранены.")

if __name__ == '__main__':
    fetch_articles()
