from . import db
from datetime import datetime

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_text = db.Column(db.Text, nullable=False)
    rewritten_text = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(200), nullable=True)
    is_posted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    source_name = db.Column(db.String(120), nullable=True)
    publish_at = db.Column(db.DateTime, nullable=True)
