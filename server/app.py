from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, Record, Config
import os
import requests
import math
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:root@localhost:3307/surgery_decision'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app)

# Default equation coefficients as per documentation
COEFFICIENTS = {
    "base": 5.3197,
    "position": -0.4604,
    "surgery_level": -0.6223,
    "surgery_method": -0.3634,
    "bmi": -0.0897,
    "hypothermia": 1.0467,
    "albumin_abnormal": 0.6037,
    "glucose_abnormal": 0.6432,
    "surgery_time": 0.0019
}

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

# WeChat Configuration
WX_APPID = 'wx447816e4e2d99865'
WX_SECRET = '8ea94a5f8449a80959bfead8a545a5ff'

# --- Middleware / Helpers ---
def validate_username(username):
    username = (username or '').strip()
    if len(username) < 3 or len(username) > 50:
        return None, "账号长度需为 3-50 个字符"
    return username, None

def validate_password(password):
    password = password or ''
    if len(password) < 6 or len(password) > 128:
        return "密码长度需为 6-128 个字符"
    return None

def verify_password(user, password):
    if not user or not user.password_hash or password is None:
        return False

    try:
        if check_password_hash(user.password_hash, password):
            return True
    except ValueError:
        # Legacy rows may contain plaintext passwords from older versions.
        pass

    if user.password_hash == password:
        user.password_hash = generate_password_hash(password)
        db.session.commit()
        return True

    return False

def serialize_user(user, include_admin_fields=False):
    data = {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "is_admin": user.is_admin,
        "created_at": user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None
    }
    if include_admin_fields:
        data["openid"] = user.openid
        data["record_count"] = Record.query.filter_by(user_id=user.id).count()
    return data

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Missing token"}), 401
        user = User.query.filter_by(id=token).first() # In production, use JWT. Simplified here using User ID as token
        if not user:
            return jsonify({"error": "Invalid token"}), 401
        return f(user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Missing token"}), 401
        user = User.query.filter_by(id=token, is_admin=True).first()
        if not user:
            return jsonify({"error": "Admin privileges required"}), 403
        return f(user, *args, **kwargs)
    return decorated

# --- Account Login / Register ---
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json or {}
    username, username_error = validate_username(data.get('username'))
    if username_error:
        return jsonify({"error": username_error}), 400

    password_error = validate_password(data.get('password'))
    if password_error:
        return jsonify({"error": password_error}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "账号已存在"}), 409

    user = User(
        username=username,
        password_hash=generate_password_hash(data.get('password')),
        nickname=(data.get('nickname') or username).strip(),
        is_admin=False
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "token": str(user.id),
        "user": serialize_user(user)
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json or {}
    username = (data.get('username') or '').strip()
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not verify_password(user, password):
        return jsonify({"error": "账号或密码错误"}), 401

    return jsonify({
        "token": str(user.id),
        "user": serialize_user(user)
    })

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    return jsonify(serialize_user(current_user))

# --- Wechat Login & Users ---
@app.route('/api/wechat/login', methods=['POST'])
def wechat_login():
    data = request.json
    code = data.get('code')
    if not code:
        return jsonify({"error": "Missing code"}), 400

    # Get access token and openid
    token_url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={WX_APPID}&secret={WX_SECRET}&code={code}&grant_type=authorization_code"
    token_res = requests.get(token_url).json()

    if "errcode" in token_res:
        return jsonify({"error": "WeChat login failed", "details": token_res}), 400

    access_token = token_res.get('access_token')
    openid = token_res.get('openid')

    # Get user info
    user_info_url = f"https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={openid}&lang=zh_CN"
    user_info_res = requests.get(user_info_url)
    user_info_res.encoding = 'utf-8'
    user_info = user_info_res.json()

    user = User.query.filter_by(openid=openid).first()
    if not user:
        user = User(
            openid=openid,
            nickname=user_info.get('nickname', 'WeChat User'),
            avatar=user_info.get('headimgurl', '')
        )
        db.session.add(user)
    else:
        user.nickname = user_info.get('nickname', user.nickname)
        user.avatar = user_info.get('headimgurl', user.avatar)

    db.session.commit()

    return jsonify({
        "token": str(user.id),
        "user": serialize_user(user)
    })

# --- Admin Login ---
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json or {}
    username = (data.get('username') or '').strip()
    password = data.get('password')

    user = User.query.filter_by(username=username, is_admin=True).first()
    if not verify_password(user, password):
        # For testing: auto create admin if none exists and trying to login with admin/admin
        if username == 'admin' and password == 'admin':
            if not User.query.filter_by(username='admin').first():
                user = User(
                    username='admin',
                    password_hash=generate_password_hash('admin'),
                    is_admin=True,
                    nickname='Administrator'
                )
                db.session.add(user)
                db.session.commit()
                return jsonify({"token": str(user.id), "user": serialize_user(user)})

        return jsonify({"error": "账号或密码错误"}), 401

    return jsonify({
        "token": str(user.id),
        "user": serialize_user(user)
    })

# --- Business Logic & APIs ---
def calculate_risk(data, configs):
    logit_p = configs['base'] \
            + configs['position'] * float(data.get('position', 0)) \
            + configs['surgery_level'] * float(data.get('surgery_level', 0)) \
            + configs['surgery_method'] * float(data.get('surgery_method', 0)) \
            + configs['bmi'] * float(data.get('bmi', 0)) \
            + configs['hypothermia'] * float(data.get('hypothermia', 0)) \
            + configs['albumin_abnormal'] * float(data.get('albumin_abnormal', 0)) \
            + configs['glucose_abnormal'] * float(data.get('glucose_abnormal', 0)) \
            + configs['surgery_time'] * float(data.get('surgery_time', 0))

    p = 1 / (1 + math.exp(-logit_p))

    p_percent = p * 100
    if p_percent < 30:
        level = "低风险"
        suggestion = configs.get('suggestion_low', '')
    elif p_percent <= 60:
        level = "中风险"
        suggestion = configs.get('suggestion_medium', '')
    else:
        level = "高风险"
        suggestion = configs.get('suggestion_high', '')

    return p, level, suggestion

@app.route('/api/records', methods=['POST'])
@token_required
def create_record(current_user):
    data = request.json

    # Load configs
    configs = {c.key: c.value_float if c.value_float is not None else c.value_text for c in Config.query.all()}

    # Calculate BMI
    weight = float(data.get('weight', 0))
    height = float(data.get('height', 0))
    bmi = weight / ((height / 100) ** 2) if height > 0 else 0
    data['bmi'] = bmi

    # Calculate indicators based on raw input
    temperature = data.get('temperature')
    if temperature is not None and str(temperature).strip() != '':
        temperature = float(temperature)
        data['hypothermia'] = 0 if temperature >= 36 else 1
    else:
        temperature = None
        data['hypothermia'] = 0

    glucose = data.get('glucose')
    if glucose is not None and str(glucose).strip() != '':
        glucose = float(glucose)
        data['glucose_abnormal'] = 0 if 3.88 <= glucose <= 6.11 else 1
    else:
        glucose = None
        data['glucose_abnormal'] = 0

    albumin = data.get('albumin')
    if albumin is not None and str(albumin).strip() != '':
        albumin = float(albumin)
        data['albumin_abnormal'] = 0 if 40 <= albumin <= 55 else 1
    else:
        albumin = None
        data['albumin_abnormal'] = 0

    # Calculate risk
    p_value, risk_level, suggestion = calculate_risk(data, configs)

    record = Record(
        user_id=current_user.id,
        hospital_no=data['hospital_no'],
        position=data.get('position'),
        surgery_level=data.get('surgery_level'),
        surgery_method=data.get('surgery_method'),
        height=height,
        weight=weight,
        bmi=bmi,
        hypothermia=data.get('hypothermia'),
        temperature=temperature,
        glucose_abnormal=data.get('glucose_abnormal'),
        glucose=glucose,
        albumin_abnormal=data.get('albumin_abnormal'),
        albumin=albumin,
        surgery_time=data.get('surgery_time'),
        p_value=p_value,
        risk_level=risk_level
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({
        "id": record.id,
        "risk_level": risk_level,
        "suggestion": suggestion,
        "p_value": p_value # Returning for testing, frontend shouldn't show it per requirements
    })

@app.route('/api/records/my', methods=['GET'])
@token_required
def get_my_records(current_user):
    records = Record.query.filter_by(user_id=current_user.id).order_by(Record.created_at.desc()).all()
    return jsonify([{
        "id": r.id,
        "hospital_no": r.hospital_no,
        "position": r.position,
        "surgery_level": r.surgery_level,
        "surgery_method": r.surgery_method,
        "height": r.height,
        "weight": r.weight,
        "bmi": r.bmi,
        "hypothermia": r.hypothermia,
        "temperature": r.temperature,
        "glucose_abnormal": r.glucose_abnormal,
        "glucose": r.glucose,
        "albumin_abnormal": r.albumin_abnormal,
        "albumin": r.albumin,
        "surgery_time": r.surgery_time,
        "p_value": r.p_value,
        "risk_level": r.risk_level,
        "created_at": r.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for r in records])

@app.route('/api/records/<int:record_id>', methods=['DELETE'])
@token_required
def delete_record(current_user, record_id):
    record = Record.query.filter_by(id=record_id, user_id=current_user.id).first()
    if not record:
        return jsonify({"error": "Record not found"}), 404
    db.session.delete(record)
    db.session.commit()
    return jsonify({"status": "success"})

# --- Admin APIs ---
@app.route('/api/admin/configs', methods=['GET'])
@admin_required
def get_configs(admin_user):
    configs = Config.query.all()
    return jsonify({c.key: c.value_float if c.value_float is not None else c.value_text for c in configs})

@app.route('/api/admin/configs', methods=['POST'])
@admin_required
def update_configs(admin_user):
    data = request.json
    for key, value in data.items():
        config = Config.query.filter_by(key=key).first()
        if config:
            if isinstance(value, float) or isinstance(value, int):
                config.value_float = float(value)
            elif isinstance(value, str):
                config.value_text = value
    db.session.commit()
    return jsonify({"status": "success"})

@app.route('/api/admin/records', methods=['GET'])
@admin_required
def get_all_records(admin_user):
    records = Record.query.order_by(Record.created_at.desc()).all()
    results = []
    for r in records:
        results.append({
            "id": r.id,
            "hospital_no": r.hospital_no,
            "position": r.position,
            "surgery_level": r.surgery_level,
            "surgery_method": r.surgery_method,
            "height": r.height,
            "weight": r.weight,
            "bmi": r.bmi,
            "hypothermia": r.hypothermia,
            "temperature": r.temperature,
            "glucose_abnormal": r.glucose_abnormal,
            "glucose": r.glucose,
            "albumin_abnormal": r.albumin_abnormal,
            "albumin": r.albumin,
            "surgery_time": r.surgery_time,
            "p_value": r.p_value,
            "risk_level": r.risk_level,
            "user": r.user.nickname if r.user else 'Unknown',
            "created_at": r.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(results)

@app.route('/api/admin/records/<int:record_id>', methods=['DELETE'])
@admin_required
def delete_admin_record(admin_user, record_id):
    record = Record.query.get(record_id)
    if not record:
        return jsonify({"error": "Record not found"}), 404
    db.session.delete(record)
    db.session.commit()
    return jsonify({"status": "success"})

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users(admin_user):
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([serialize_user(user, include_admin_fields=True) for user in users])

@app.route('/api/admin/users', methods=['POST'])
@admin_required
def create_user(admin_user):
    data = request.json or {}
    username, username_error = validate_username(data.get('username'))
    if username_error:
        return jsonify({"error": username_error}), 400

    password_error = validate_password(data.get('password'))
    if password_error:
        return jsonify({"error": password_error}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "账号已存在"}), 409

    user = User(
        username=username,
        password_hash=generate_password_hash(data.get('password')),
        nickname=(data.get('nickname') or username).strip(),
        is_admin=bool(data.get('is_admin'))
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(serialize_user(user, include_admin_fields=True))

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(admin_user, user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404

    data = request.json or {}
    if 'username' in data:
        username, username_error = validate_username(data.get('username'))
        if username_error:
            return jsonify({"error": username_error}), 400
        existing = User.query.filter(User.username == username, User.id != user.id).first()
        if existing:
            return jsonify({"error": "账号已存在"}), 409
        user.username = username

    if 'nickname' in data:
        user.nickname = (data.get('nickname') or user.username or '').strip()

    if 'is_admin' in data:
        next_is_admin = bool(data.get('is_admin'))
        if user.id == admin_user.id and not next_is_admin:
            return jsonify({"error": "不能取消当前登录管理员的管理员权限"}), 400
        user.is_admin = next_is_admin

    db.session.commit()
    return jsonify(serialize_user(user, include_admin_fields=True))

@app.route('/api/admin/users/<int:user_id>/password', methods=['PATCH'])
@admin_required
def reset_user_password(admin_user, user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404

    data = request.json or {}
    password_error = validate_password(data.get('password'))
    if password_error:
        return jsonify({"error": password_error}), 400

    user.password_hash = generate_password_hash(data.get('password'))
    db.session.commit()
    return jsonify({"status": "success"})

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(admin_user, user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    if user.id == admin_user.id:
        return jsonify({"error": "不能删除当前登录管理员"}), 400

    Record.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
