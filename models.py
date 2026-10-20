import re
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from config import Config


def conexion():
    return mysql.connector.connect(host=Config.DB_HOST, user=Config.DB_USER,
        password=Config.DB_PASSWORD, database=Config.DB_NAME)


def consultar(sql, valores=(), uno=False):
    conn = conexion()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, valores)
        return cur.fetchone() if uno else cur.fetchall()
    finally:
        cur.close()
        conn.close()


def ejecutar(sql, valores=()):
    conn = conexion()
    cur = conn.cursor()
    try:
        cur.execute(sql, valores)
        conn.commit()
        return cur.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def validar_estudiante(datos, parcial=False):
    errores = {}
    campos = ['nombre', 'apellido', 'edad', 'carrera', 'email', 'telefono']
    for campo in campos:
        if not parcial and campo not in datos:
            errores[campo] = 'Campo obligatorio'
    for campo in ['nombre', 'apellido']:
        if campo in datos and (not isinstance(datos[campo], str) or not re.fullmatch(r'[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]{2,80}', datos[campo].strip())):
            errores[campo] = 'Solo letras y espacios, entre 2 y 80 caracteres'
    if 'edad' in datos:
        try:
            edad = int(datos['edad'])
            if edad < 15 or edad > 100:
                raise ValueError()
        except (ValueError, TypeError):
            errores['edad'] = 'La edad debe estar entre 15 y 100'
    if 'carrera' in datos and (not isinstance(datos['carrera'], str) or not 2 <= len(datos['carrera'].strip()) <= 120):
        errores['carrera'] = 'La carrera debe tener entre 2 y 120 caracteres'
    if 'email' in datos and (not isinstance(datos['email'], str) or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', datos['email']) or len(datos['email']) > 120):
        errores['email'] = 'Correo electrónico inválido'
    if 'telefono' in datos and datos['telefono'] not in (None, '') and (not isinstance(datos['telefono'], str) or not re.fullmatch(r'[+0-9 ()-]{7,25}', datos['telefono'])):
        errores['telefono'] = 'Teléfono inválido'
    if parcial and not any(c in datos for c in campos):
        errores['general'] = 'No hay campos para actualizar'
    return errores


def json_seguro(obj):
    if isinstance(obj, dict):
        return {k: json_seguro(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [json_seguro(i) for i in obj]
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj
