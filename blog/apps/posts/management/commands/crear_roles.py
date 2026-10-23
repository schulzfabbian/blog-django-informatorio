from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

NOMBRE_GRUPO = 'Colaborador'
PERMISOS_COLABORADOR = ['add_post', 'change_post', 'delete_post', 'delete_comentario']


class Command(BaseCommand):
    help = 'Crea el grupo "Colaborador" (gestiona artículos y modera comentarios).'

    def handle(self, *args, **options):
        grupo, creado = Group.objects.get_or_create(name=NOMBRE_GRUPO)
        permisos = Permission.objects.filter(
            content_type__app_label='posts',
            codename__in=PERMISOS_COLABORADOR,
        )
        grupo.permissions.set(permisos)

        if permisos.count() != len(PERMISOS_COLABORADOR):
            self.stdout.write(self.style.WARNING(
                'Faltan permisos: ejecutá primero "python manage.py migrate".'
            ))

        accion = 'creado' if creado else 'actualizado'
        self.stdout.write(self.style.SUCCESS(
            f'Grupo "{NOMBRE_GRUPO}" {accion} con {permisos.count()} permisos.'
        ))
