# 🚀 Blog Informatorio 2025

Proyecto final del curso de Desarrollo Web de **Informatorio Chaco**. Es un blog con Django: los visitantes leen artículos, los usuarios registrados comentan y un equipo de colaboradores publica y modera el contenido.

## ✨ Funcionalidades

- Listado de artículos con imagen, categoría y fecha, y filtro por categoría.
- Registro, inicio y cierre de sesión.
- Comentarios: crear, editar y borrar los propios.
- Panel de colaboradores: crear, editar y borrar artículos, y moderar comentarios de cualquier usuario.
- Formulario de contacto (en desarrollo los correos se imprimen en la consola).
- Mensajes de confirmación y error en pantalla.

## 👥 Roles y permisos

| Rol | Qué puede hacer |
| :--- | :--- |
| **Visitante** | Leer artículos y comentarios, filtrar por categoría, registrarse. |
| **Miembro** (usuario registrado) | Todo lo anterior, más comentar y editar o borrar **sus propios** comentarios. |
| **Colaborador** (grupo `Colaborador`) | Todo lo anterior, más crear, editar y borrar artículos y borrar comentarios de cualquier usuario. |
| **Superusuario** | Acceso total, incluido el panel `/admin`. |

Los artículos inactivos solo los ven quienes pueden editar artículos. Borrar artículos y comentarios se hace únicamente con peticiones `POST` protegidas por CSRF.

## 🛠️ Tecnologías

- Python 3 y Django (desarrollado con Django 6.0)
- SQLite
- HTML, Bootstrap 5.3 (CDN) y plantillas de Django con herencia (`base.html`)
- Git y GitHub

## ▶️ Cómo ejecutarlo (Windows, PowerShell)

```powershell
git clone https://github.com/schulzfabbian/blog-django-informatorio.git
cd blog-django-informatorio

python -m venv entorno
entorno\Scripts\activate
pip install -r requirements.txt

cd blog
python manage.py migrate
python manage.py crear_roles
python manage.py createsuperuser
python manage.py runserver
```

Después abrí http://127.0.0.1:8000/. Para crear un colaborador, entrá a `/admin` con el superusuario, creá el usuario y agregalo al grupo **Colaborador**.

## 🧪 Pruebas automáticas

```powershell
cd blog
python manage.py test
```

Las pruebas cubren permisos por rol, borrado solo por `POST`, moderación de comentarios, artículos inactivos y el formulario de contacto.

## 🔐 Configuración (variables de entorno)

En desarrollo no hace falta definir nada. Para publicar el sitio:

| Variable | Descripción |
| :--- | :--- |
| `DJANGO_DEBUG` | `False` en producción. Por defecto `True`. |
| `DJANGO_SECRET_KEY` | Clave secreta. Obligatoria si `DJANGO_DEBUG` es `False`. |
| `DJANGO_ALLOWED_HOSTS` | Dominios permitidos, separados por coma. |
| `CONTACTO_DESTINO` | Correo que recibe los mensajes del formulario de contacto. |
| `DEFAULT_FROM_EMAIL` | Remitente de esos mensajes. |

> La base de datos (`db.sqlite3`) y las imágenes subidas (`media/`) no se incluyen en el repositorio. No hay usuarios ni contraseñas de ejemplo: creá los tuyos con los comandos de arriba.

## 🗺️ Próximos pasos

- Paginación en el listado de artículos.
- Configurar el envío real de correos y el despliegue.
- Ampliar las pruebas a formularios y vistas de edición.

---
*Proyecto realizado para el curso de Desarrollo Web - Informatorio Chaco.*
