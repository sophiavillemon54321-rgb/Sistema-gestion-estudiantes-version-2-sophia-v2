# Sistema de Gestión de Estudiantes — Versión 2
Proyecto académico: Universidad Libre, Programación II — Sistemas Distribuidos.

## 1. Archivos
- backend: API REST Flask, JWT, bcrypt y MySQL.
- frontend: HTML/CSS/JavaScript.
- universidad_db.sql: base de datos (ejecutar al final de la preparación).

## 2. Configurar backend (Windows PowerShell)
Desde la carpeta proyecto-crud:
```powershell
cd backend
py -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```
Edita `.env`: escribe tu contraseña de MySQL en `DB_PASSWORD`. Cambia `JWT_SECRET` por una frase secreta larga. No compartas ni subas `.env`.

## 3. BASE DE DATOS: ÚLTIMO PASO
Con MySQL 8 instalado, abre MySQL Workbench, entra a tu conexión y ejecuta `universidad_db.sql` con el botón de rayo. Alternativamente, desde la carpeta raíz del proyecto en la terminal:
```powershell
mysql -u root -p < universidad_db.sql
```
**Nota:** esa redirección funciona en CMD, no siempre en PowerShell. Si usas PowerShell, ejecuta `mysql -u root -p`, luego escribe `source RUTA_COMPLETA/universidad_db.sql;`.

## 4. Crear el usuario demo
Desde `backend`:
```powershell
.\venv\Scripts\python.exe crear_admin.py
```
Usuario `admin`, clave `admin123` solo para desarrollo local. Debes cambiarlos antes de desplegar.

## 5. Arrancar el backend
Desde backend:
```powershell
.\venv\Scripts\python.exe app.py
```
Abre `http://localhost:5000/api/health`: debe indicar que backend y MySQL están conectados.

## 6. Arrancar frontend en otra terminal
Desde la carpeta raíz del proyecto:
```powershell
cd frontend
py -m http.server 8000
```
Navega a `http://localhost:8000` y entra con admin/admin123.

## 7. Pruebas rápidas
- Crear usuario (tendrá rol usuario; no puede eliminar).
- Login admin y crear estudiante.
- Editar, buscar, ordenar, cambiar páginas, ver estadísticas.
- Eliminar solo como admin, cerrar sesión.

## Seguridad
JWT dura una hora. Se revoca por JTI en la tabla tokens_revocados. Consultas SQL parametrizadas; nombres de columna ordenados mediante listas de permitidos. Credenciales de demostración **no aptas para producción**. SessionStorage para JWT en esta demo; una app productiva debería revisar cookies seguras, CSRF y mitigaciones XSS.
