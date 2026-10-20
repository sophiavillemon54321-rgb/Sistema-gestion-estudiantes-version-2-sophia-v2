"""Crea el administrador inicial para un proyecto académico local."""
import bcrypt
from models import consultar, ejecutar

if __name__ == '__main__':
    if consultar('SELECT id FROM usuarios WHERE username=%s',('admin',),uno=True):
        print('El administrador ya existe. No se modificó su contraseña.')
    else:
        hashed = bcrypt.hashpw(b'admin123',bcrypt.gensalt()).decode()
        ejecutar('INSERT INTO usuarios(username,email,password_hash,rol) VALUES (%s,%s,%s,%s)',
                 ('admin','admin@universidad.edu',hashed,'admin'))
        print('Administrador creado: admin / admin123 (solo para pruebas locales)')
