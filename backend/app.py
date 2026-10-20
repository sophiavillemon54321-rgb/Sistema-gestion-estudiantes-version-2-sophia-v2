from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from routes.auth import auth_bp
from routes.estudiantes import est_bp
from models import consultar

app = Flask(__name__)
CORS(app,resources={r'/api/*':{'origins':[Config.FRONTEND_ORIGIN],
    'methods':['GET','POST','PUT','DELETE','OPTIONS'],
    'allow_headers':['Authorization','Content-Type']}})
app.register_blueprint(auth_bp)
app.register_blueprint(est_bp)

@app.get('/api/health')
def salud():
    consultar('SELECT 1 AS ok',uno=True)
    return jsonify(estado='ok',mensaje='Backend y MySQL conectados')

@app.errorhandler(404)
def sin_ruta(error):
    return jsonify(error='Ruta no encontrada'),404

if __name__=='__main__':
    app.run(host='127.0.0.1',port=5000,debug=True)
