from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(100), unique=True, nullable=True) # for wechat users
    nickname = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(500), nullable=True)
    username = db.Column(db.String(100), unique=True, nullable=True) # for admin
    password_hash = db.Column(db.String(255), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Record(db.Model):
    __tablename__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    hospital_no = db.Column(db.String(50), nullable=False)
    postop_skin = db.Column(db.Integer) # 1:压红, 2:一期, 3:二期, 4:其他

    position = db.Column(db.Integer)
    surgery_level = db.Column(db.Integer)
    surgery_method = db.Column(db.Integer)
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    bmi = db.Column(db.Float)
    hypothermia = db.Column(db.Integer)
    glucose_abnormal = db.Column(db.Integer)
    albumin_abnormal = db.Column(db.Integer)
    surgery_time = db.Column(db.Integer)

    p_value = db.Column(db.Float)
    risk_level = db.Column(db.String(20)) # 低风险, 中风险, 高风险

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('records', lazy=True))

class Config(db.Model):
    __tablename__ = 'configs'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value_float = db.Column(db.Float, nullable=True)
    value_text = db.Column(db.Text, nullable=True)
