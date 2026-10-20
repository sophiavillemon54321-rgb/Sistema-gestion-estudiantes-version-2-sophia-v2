from functools import wraps
from flask import request, jsonify, g
import jwt
from config import Config
from models import consultar


def autenticacion_requerida(fn):
    @wraps(fn)
    def decorador(*args, **kwargs):
        header = request.headers.get('Authorization', '')
        if not header.startswith('Bearer '):
            return jsonify(error='Token requerido'), 401
        token = header[7:]
        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
            revocado = consultar('SELECT jti FROM tokens_revocados WHERE jti=%s', (payload['jti'],), uno=True)
            if revocado:
                return jsonify(error='Token revocado'), 401
            usuario = consultar('SELECT id, username, email, rol, fecha_creacion, ultimo_acceso FROM usuarios WHERE id=%s', (payload['usuario_id'],), uno=True)
            if not usuario:
                return jsonify(error='Usuario no encontrado'), 401
            g.usuario = usuario
            g.token = payload
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError):
            return jsonify(error='Token inválido o expirado'), 401
        return fn(*args, **kwargs)
    return decorador


def admin_requerido(fn):
    @wraps(fn)
    @autenticacion_requerida
    def decorador(*args, **kwargs):
        if g.usuario['rol'] != 'admin':
            return jsonify(error='Solo los administradores tienen permiso'), 403
        return fn(*args, **kwargs)
    return decorador
