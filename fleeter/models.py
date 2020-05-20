from fleeter import db


class Model(db.Model):

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class User(Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), nullable=False, unique=True)
    fleet = db.relationship('Fleet', backref='user',
                            cascade='all, delete-orphan')

    def __repr__(self):
        return f'<@{self.username}>'


class Fleet(Model):
    __tablename__ = 'fleets'

    id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.String(140), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)

    def __repr__(self):
        return f'<@{self.user.username} at {self.created_at}' \
               f' wrote "{self.post}">'
