import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_post_autor'),
    ]

    operations = [
        # Se quita default='Sin categoría' (no es un id válido para una clave foránea).
        migrations.AlterField(
            model_name='post',
            name='categoria',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='posts.categoria'),
        ),
        # Se quita default='static/post_default.png' (ese archivo no existe).
        migrations.AlterField(
            model_name='post',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='imagenes'),
        ),
    ]
