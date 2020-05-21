from fleeter import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), nullable=False, unique=True)
    fleet = db.relationship('Fleet', backref='user',
                            cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User @{self.username}>'


class Fleet(db.Model):
    __tablename__ = 'fleets'

    id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.String(140), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Fleet "{self.post}" by ' \
               f'@{self.user.username} at {self.created_at}>'
