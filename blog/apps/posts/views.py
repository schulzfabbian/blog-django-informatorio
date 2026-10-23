from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ComentarioForm, PostForm
from .models import Categoria, Comentario, Post


# Vista del inicio (Index): solo muestra posts activos
def index(request):
    posts = Post.objects.filter(activo=True).select_related('categoria')
    return render(request, 'index.html', {'posts': posts})


# Vista del detalle del post + comentarios
def detalle_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Un post inactivo solo lo pueden ver quienes tienen permiso para editar posts
    if not post.activo and not request.user.has_perm('posts.change_post'):
        raise Http404('El artículo no existe.')

    comentarios = post.comentarios.select_related('usuario').order_by('fecha')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.posts = post
            comentario.usuario = request.user
            comentario.save()
            return redirect('detalle', pk=post.pk)
    else:
        form = ComentarioForm()

    ctx = {
        'post': post,
        'comentarios': comentarios,
        'form': form,
    }
    return render(request, 'detalle_post.html', ctx)


# Vista para CREAR POST (solo Colaboradores o Root)
@login_required
@permission_required('posts.add_post', raise_exception=True)
def crear_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user  # Guardamos al autor
            post.save()
            messages.success(request, '¡Post creado exitosamente!')
            return redirect('index')
    else:
        form = PostForm()

    return render(request, 'crear_post.html', {'form': form})


# Vista para BORRAR POST (solo Colaboradores o Root). Solo acepta POST.
@login_required
@permission_required('posts.delete_post', raise_exception=True)
@require_POST
def borrar_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    messages.success(request, 'El artículo ha sido eliminado.')
    return redirect('index')


# Vista para BORRAR COMENTARIO (dueño del comentario o quien tenga el permiso). Solo acepta POST.
@login_required
@require_POST
def borrar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id)
    post_pk = comentario.posts_id

    if comentario.usuario_id == request.user.id or request.user.has_perm('posts.delete_comentario'):
        comentario.delete()
        messages.success(request, 'Comentario eliminado.')
    else:
        messages.error(request, 'No tenés permiso para borrar este comentario.')

    return redirect('detalle', pk=post_pk)


# Vista de registro
def registrar_usuario(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'¡Bienvenido {username}!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})


# Vista para filtrar por categoría
def posts_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    posts = Post.objects.filter(categoria=categoria, activo=True).select_related('categoria')

    ctx = {
        'posts': posts,
        'categoria_seleccionada': categoria,
    }
    return render(request, 'index.html', ctx)


# Páginas estáticas
def acerca_de(request):
    return render(request, 'acerca_de.html')


def contacto(request):
    if request.method == 'POST':
        email_usuario = request.POST.get('email_usuario', '').strip()
        # Se quitan saltos de línea del asunto para evitar inyección de cabeceras
        asunto = ' '.join(request.POST.get('asunto', '').split())[:100]
        mensaje = request.POST.get('mensaje', '').strip()

        if not (email_usuario and asunto and mensaje):
            messages.error(request, 'Completá todos los campos para enviar el mensaje.')
            return render(request, 'contacto.html')

        send_mail(
            asunto,
            f'{mensaje}\n\nEmail del usuario: {email_usuario}',
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACTO_DESTINO],
            fail_silently=False,
        )
        return render(request, 'contacto.html', {'mensaje_enviado': True})

    return render(request, 'contacto.html')


# Vista para EDITAR POST (solo Colaborador/Root)
@login_required
@permission_required('posts.change_post', raise_exception=True)
def editar_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Artículo actualizado correctamente!')
            return redirect('detalle', pk=pk)
    else:
        form = PostForm(instance=post)  # Carga los datos actuales en el form

    return render(request, 'crear_post.html', {'form': form, 'es_edicion': True})


# Vista para EDITAR COMENTARIO (solo el dueño)
@login_required
def editar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id)

    if comentario.usuario_id != request.user.id:
        messages.error(request, 'No tenés permiso para editar este comentario.')
        return redirect('detalle', pk=comentario.posts_id)

    if request.method == 'POST':
        form = ComentarioForm(request.POST, instance=comentario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comentario actualizado.')
            return redirect('detalle', pk=comentario.posts_id)
    else:
        form = ComentarioForm(instance=comentario)

    return render(request, 'editar_comentario.html', {'form': form})
