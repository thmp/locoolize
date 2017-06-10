import datetime

from app import db, Post

post = Post(
    author="Thomas",
    photo_url="3077f6b411aefedcdd309f21b859b487.jpg",
    valid_until=datetime.datetime.utcnow() + datetime.timedelta(days=1),
    latitude=0.0,
    longitude=0.0,
    message="First post"
)

db.session.add(post)
db.session.commit()