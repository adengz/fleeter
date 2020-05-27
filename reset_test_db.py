from pathlib import Path
import csv
from datetime import datetime
from fleeter import create_app, db
from fleeter.models import User, Fleet, Follow

DATA_ROOT = Path('data')
CSV_FILE = 'lifeinvader_by_timeline.csv'

app = create_app('config.TestingConfig')
context = app.app_context()
context.push()
db.init_app(app)
db.drop_all()
db.create_all()

users = {}
with open(DATA_ROOT / CSV_FILE) as f:
    reader = csv.reader(f)
    for row in reader:
        poster, post, wall, _, _, timestamp = row

        if wall not in users:
            users[wall] = User(username=wall)
            db.session.add(users[wall])
        if poster not in users:
            users[poster] = User(username=poster)
            db.session.add(users[poster])
        db.session.commit()

        time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        if poster == wall:  # status posted on one's own page
            db.session.add(Fleet(post=post, user=users[wall], created_at=time))
            db.session.commit()
        else:  # message posted on someone else's page, used to find relationship
            follow = Follow.query.filter_by(follower_id=users[poster].id,
                                            followee_id=users[wall].id)
            if follow.one_or_none() is None:
                db.session.add(Follow(follower_id=users[poster].id,
                                      followee_id=users[wall].id,
                                      created_at=time))
                db.session.commit()

db.session.close()
context.pop()
