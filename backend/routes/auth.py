import re
import uuid
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
import mysql.connector
from flask import Blueprint, request, jsonify, g
from config import Config
from models import consultar, ejecutar, json_seguro
from middleware import autenticacion_requerida

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.post('/registro')
def registro():
    data = request.get_json(silent=True) or {}
    username = str(data.get('username', '')).strip()
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))
    if not re.fullmatch(r'[A-Za-z0-9_]{3,30}', username):
        return jsonify(error='Usuario: entre 3 y 30 caracteres (letras, números y _)'), 400
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email) or len(email)>120:
        return jsonify(error='Correo inválido'), 400
    if len(password)<6 or len(password)>72:
        return jsonify(error='Contraseña de 6 a 72 caracteres'), 400
    hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        id_nuevo = ejecutar('INSERT INTO usuarios(username,email,password_hash,rol) VALUES (%s,%s,%s,%s)', (username,email,hash_password,'usuario'))
    except mysql.connector.IntegrityError:
        return jsonify(error='Nombre de usuario o correo ya registrado'), 409
    return jsonify(mensaje='Usuario registrado exitosamente', usuario={'id':id_nuevo,'username':username,'email':email}), 201

@auth_bp.post('/login')
def login():
    data = request.get_json(silent=True) or {}
    username = str(data.get('username',''))
    password = str(data.get('password',''))
    usuario = consultar('SELECT * FROM usuarios WHERE username=%s', (username,), uno=True)
    if not usuario or not bcrypt.checkpw(password.encode(), usuario['password_hash'].encode()):
        return jsonify(error='Usuario o contraseña incorrectos'), 401
    ejecutar('UPDATE usuarios SET ultimo_acceso=NOW() WHERE id=%s', (usuario['id'],))
    ahora = datetime.now(timezone.utc)
    claims = {'usuario_id':usuario['id'],'username':usuario['username'],'rol':usuario['rol'],
              'iat':ahora,'exp':ahora + timedelta(hours=Config.JWT_HOURS),'jti':str(uuid.uuid4())}
    token = jwt.encode(claims, Config.JWT_SECRET, algorithm='HS256')
    return jsonify(mensaje='Login exitoso', token=token, usuario={'id':usuario['id'],'username':usuario['username'],'email':usuario['email'],'rol':usuario['rol']})

@auth_bp.post('/logout')
@autenticacion_requerida
def logout():
    ejecutar('INSERT IGNORE INTO tokens_revocados (jti, expiracion) VALUES (%s,%s)',
             (g.token['jti'], datetime.fromtimestamp(g.token['exp'],timezone.utc).replace(tzinfo=None)))
    return jsonify(mensaje='Logout exitoso')

@auth_bp.get('/perfil')
@autenticacion_requerida
def perfil():
    return jsonify(usuario=json_seguro(g.usuario))
