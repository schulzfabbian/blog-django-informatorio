from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# 1. Modelo Categoría
class Categoria(models.Model):
    nombre = models.CharField(max_length=30)

    def __str__(self):
        return self.nombre


# 2. Modelo Post
class Post(models.Model):
    titulo = models.CharField(max_length=50)
    subtitulo = models.CharField(max_length=100, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    texto = models.TextField()
    activo = models.BooleanField(default=True)

    # Relación con Categoría (1 a N). Si se borra la categoría, el post queda sin categoría.
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)

    # Imagen del post (requiere Pillow). Es opcional: sin imagen, las plantillas no muestran nada.
    imagen = models.ImageField(null=True, blank=True, upload_to='imagenes')

    publicado = models.DateTimeField(default=timezone.now)

    autor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ('-publicado',)  # Más recientes primero

    def __str__(self):
        return self.titulo

    # Borra el archivo de imagen del disco cuando se borra el post de la base de datos
    def delete(self, using=None, keep_parents=False):
        if self.imagen:
            self.imagen.delete(save=False)
        return super().delete(using=using, keep_parents=keep_parents)


# 3. Modelo Comentario
class Comentario(models.Model):
    posts = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentarios')
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.texto[:50]
