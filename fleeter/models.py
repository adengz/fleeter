from sqlalchemy import func
from fleeter import db


class Follow(db.Model):
    __tablename__ = 'follow'

    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followee_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    created_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False,
                           server_default=func.now())


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), nullable=False, unique=True)
    fleet = db.relationship('Fleet', backref='user',
                            cascade='all, delete-orphan')
    following = db.relationship(
        'User', secondary='follow',
        primaryjoin=(Follow.follower_id == id),
        secondaryjoin=(Follow.followee_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        cascade='all', lazy='dynamic'
    )

    def __repr__(self):
        return f'<User @{self.username}>'

    def get_fleets(self, page=1, per_page=10):
        fleets = Fleet.query.filter_by(user_id=self.id). \
            order_by(Fleet.created_at.desc())
        return fleets.paginate(page=page, per_page=per_page).items


class Fleet(db.Model):
    __tablename__ = 'fleets'

    id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.String(140), nullable=False)
    created_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False,
                           server_default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Fleet "{self.post}" by ' \
               f'@{self.user.username} at {self.created_at}>'
