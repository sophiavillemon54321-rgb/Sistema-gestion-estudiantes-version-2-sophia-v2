import math
import mysql.connector
from flask import Blueprint, request, jsonify, g
from middleware import autenticacion_requerida, admin_requerido
from models import consultar, ejecutar, validar_estudiante, json_seguro

est_bp = Blueprint('estudiantes', __name__, url_prefix='/api/estudiantes')
COLUMNAS = {'nombre','apellido','edad','carrera','email','telefono'}
ORDENES = {'id','nombre','apellido','edad','carrera'}

@est_bp.get('')
@autenticacion_requerida
def listar():
    try:
        page = max(1,int(request.args.get('page',1)))
        per_page = min(50,max(1,int(request.args.get('per_page',5))))
    except ValueError:
        return jsonify(error='Paginación inválida'),400
    search = request.args.get('search','').strip()[:100]
    orden = request.args.get('orden','id')
    direccion = request.args.get('direccion','asc').lower()
    if orden not in ORDENES or direccion not in ('asc','desc'):
        return jsonify(error='Orden inválido'),400
    where = ' WHERE nombre LIKE %s OR apellido LIKE %s OR carrera LIKE %s' if search else ''
    params = (f'%{search}%',)*3 if search else ()
    total = consultar('SELECT COUNT(*) AS total FROM estudiantes'+where,params,uno=True)['total']
    sql = f'SELECT * FROM estudiantes{where} ORDER BY {orden} {direccion.upper()} LIMIT %s OFFSET %s'
    registros = consultar(sql,params+(per_page,(page-1)*per_page))
    paginas = math.ceil(total/per_page)
    return jsonify(estudiantes=json_seguro(registros),paginacion={'page':page,'per_page':per_page,'total_items':total,
        'total_pages':paginas,'has_prev':page>1,'has_next':page<paginas})

@est_bp.get('/stats/general')
@autenticacion_requerida
def estadisticas():
    resumen = consultar('SELECT COUNT(*) AS total_estudiantes, ROUND(AVG(edad),1) AS promedio_edad, MIN(edad) AS edad_minima, MAX(edad) AS edad_maxima FROM estudiantes',uno=True)
    resumen['estudiantes_por_carrera'] = consultar('SELECT carrera, COUNT(*) AS cantidad FROM estudiantes GROUP BY carrera ORDER BY cantidad DESC')
    return jsonify(json_seguro(resumen))

@est_bp.get('/<int:estudiante_id>')
@autenticacion_requerida
def obtener(estudiante_id):
    registro = consultar('SELECT * FROM estudiantes WHERE id=%s',(estudiante_id,),uno=True)
    return (jsonify(json_seguro(registro)),200) if registro else (jsonify(error='Estudiante no encontrado'),404)

@est_bp.post('')
@autenticacion_requerida
def crear():
    datos = request.get_json(silent=True) or {}
    errores = validar_estudiante(datos)
    if errores:
        return jsonify(error='Validación fallida', campos=errores),400
    try:
        nuevo_id = ejecutar('INSERT INTO estudiantes(nombre,apellido,edad,carrera,email,telefono) VALUES (%s,%s,%s,%s,%s,%s)',
            (datos['nombre'].strip(),datos['apellido'].strip(),int(datos['edad']),datos['carrera'].strip(),datos['email'].strip().lower(),datos.get('telefono','')))
    except mysql.connector.IntegrityError:
        return jsonify(error='Ya existe un estudiante con ese email'),409
    return jsonify(mensaje='Estudiante creado exitosamente',id=nuevo_id,creado_por=g.usuario['username']),201

@est_bp.put('/<int:estudiante_id>')
@autenticacion_requerida
def actualizar(estudiante_id):
    datos = request.get_json(silent=True) or {}
    errores = validar_estudiante(datos,parcial=True)
    if errores:
        return jsonify(error='Validación fallida',campos=errores),400
    if not consultar('SELECT id FROM estudiantes WHERE id=%s',(estudiante_id,),uno=True):
        return jsonify(error='Estudiante no encontrado'),404
    cambios = {k:datos[k] for k in COLUMNAS if k in datos}
    if 'edad' in cambios:
        cambios['edad']=int(cambios['edad'])
    if 'email' in cambios:
        cambios['email']=cambios['email'].lower()
    sql = 'UPDATE estudiantes SET '+', '.join(f'{k}=%s' for k in cambios)+' WHERE id=%s'
    try:
        ejecutar(sql,tuple(cambios.values())+(estudiante_id,))
    except mysql.connector.IntegrityError:
        return jsonify(error='Email ya registrado'),409
    return jsonify(mensaje='Estudiante actualizado exitosamente',actualizado_por=g.usuario['username'])

@est_bp.delete('/<int:estudiante_id>')
@admin_requerido
def eliminar(estudiante_id):
    if not consultar('SELECT id FROM estudiantes WHERE id=%s',(estudiante_id,),uno=True):
        return jsonify(error='Estudiante no encontrado'),404
    ejecutar('DELETE FROM estudiantes WHERE id=%s',(estudiante_id,))
    return jsonify(mensaje='Estudiante eliminado exitosamente',eliminado_por=g.usuario['username'])
