from __future__ import annotations

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
    username = db.Column(db.String(30), index=True,
                         nullable=False, unique=True)
    auth0_id = db.Column(db.String(60), index=True, unique=True)
    fleets = db.relationship('Fleet', order_by='Fleet.created_at.desc()',
                             backref='user', cascade='all, delete-orphan',
                             lazy='dynamic')
    following = db.relationship(
        'User', secondary='follow',
        primaryjoin=(Follow.follower_id == id),
        secondaryjoin=(Follow.followee_id == id),
        order_by=Follow.created_at.desc(),
        backref=db.backref('followers', order_by=Follow.created_at.desc(),
                           lazy='dynamic'),
        cascade='all', lazy='dynamic'
    )

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {'id': self.id, 'username': self.username,
                'total_fleets': self.fleets.count(),
                'total_following': self.following.count(),
                'total_followers': self.followers.count()}

    @property
    def newsfeed(self):
        """Fetches fleets of a user's own and other users being followed."""
        others = Fleet.query.\
            join(Follow, (Follow.followee_id == Fleet.user_id))\
            .filter(Follow.follower_id == self.id)
        return self.fleets.union(others).order_by(Fleet.created_at.desc())

    def is_following(self, other: User) -> bool:
        """Checks whether current user is following the other user."""
        assert self != other
        follow = self.following.filter_by(id=other.id).one_or_none()
        return follow is not None

    def follow(self, other: User) -> None:
        """Follows the other user if not currently following"""
        if not self.is_following(other):
            self.following.append(other)

    def unfollow(self, other: User) -> None:
        """Unfollows the other user if currently following"""
        if self.is_following(other):
            self.following.remove(other)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Fleet(db.Model):
    __tablename__ = 'fleets'

    id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.String(280), nullable=False)
    created_at = db.Column(db.TIMESTAMP(timezone=True), index=True,
                           nullable=False, server_default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Fleet "{self.post}" by ' \
               f'{self.user.username} at {self.created_at}>'

    def to_dict(self):
        return {'id': self.id, 'post': self.post,
                'username': self.user.username,
                'created_at': str(self.created_at)}

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
