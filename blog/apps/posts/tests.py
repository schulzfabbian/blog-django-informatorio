from io import StringIO

from django.contrib.auth.models import Group, User
from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Categoria, Comentario, Post


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('crear_roles', stdout=StringIO())
        cls.categoria = Categoria.objects.create(nombre='Tecnologia')
        cls.post = Post.objects.create(
            titulo='Post de prueba', texto='Contenido de prueba', categoria=cls.categoria
        )
        cls.miembro = User.objects.create_user('miembro', password='clave-de-prueba-1')
        cls.otro = User.objects.create_user('otro', password='clave-de-prueba-2')
        cls.colaborador = User.objects.create_user('colab', password='clave-de-prueba-3')
        cls.colaborador.groups.add(Group.objects.get(name='Colaborador'))
        cls.comentario = Comentario.objects.create(
            posts=cls.post, usuario=cls.miembro, texto='Mi comentario'
        )


class LecturaTests(BaseTestCase):
    def test_index_muestra_posts_activos_y_oculta_inactivos(self):
        Post.objects.create(titulo='Oculto', texto='x', categoria=self.categoria, activo=False)
        respuesta = self.client.get(reverse('index'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Post de prueba')
        self.assertNotContains(respuesta, 'Oculto')

    def test_post_sin_categoria_no_rompe_el_index(self):
        Post.objects.create(titulo='Sin categoria', texto='x')
        respuesta = self.client.get(reverse('index'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Sin categoria')

    def test_post_inactivo_da_404_a_visitantes_y_200_a_colaboradores(self):
        inactivo = Post.objects.create(titulo='Borrador', texto='x', categoria=self.categoria, activo=False)
        url = reverse('detalle', kwargs={'pk': inactivo.pk})
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_login(self.colaborador)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_filtro_por_categoria(self):
        respuesta = self.client.get(reverse('posts_por_categoria', kwargs={'categoria_id': self.categoria.pk}))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Post de prueba')


class PermisosDePostsTests(BaseTestCase):
    def test_visitante_es_redirigido_al_login_al_crear_post(self):
        respuesta = self.client.get(reverse('crear_post'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('/accounts/login/', respuesta.url)

    def test_miembro_no_puede_crear_posts(self):
        self.client.force_login(self.miembro)
        self.assertEqual(self.client.get(reverse('crear_post')).status_code, 403)

    def test_colaborador_puede_abrir_el_formulario_de_crear_post(self):
        self.client.force_login(self.colaborador)
        self.assertEqual(self.client.get(reverse('crear_post')).status_code, 200)

    def test_borrar_post_no_acepta_get(self):
        self.client.force_login(self.colaborador)
        respuesta = self.client.get(reverse('borrar_post', kwargs={'pk': self.post.pk}))
        self.assertEqual(respuesta.status_code, 405)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_colaborador_borra_post_por_post(self):
        self.client.force_login(self.colaborador)
        respuesta = self.client.post(reverse('borrar_post', kwargs={'pk': self.post.pk}))
        self.assertRedirects(respuesta, reverse('index'))
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_miembro_no_puede_borrar_posts(self):
        self.client.force_login(self.miembro)
        respuesta = self.client.post(reverse('borrar_post', kwargs={'pk': self.post.pk}))
        self.assertEqual(respuesta.status_code, 403)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())


class ComentariosTests(BaseTestCase):
    def test_visitante_no_puede_comentar(self):
        url = reverse('detalle', kwargs={'pk': self.post.pk})
        respuesta = self.client.post(url, {'texto': 'Hola'})
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('/accounts/login/', respuesta.url)
        self.assertEqual(Comentario.objects.count(), 1)

    def test_miembro_puede_comentar(self):
        self.client.force_login(self.otro)
        url = reverse('detalle', kwargs={'pk': self.post.pk})
        self.client.post(url, {'texto': 'Hola'})
        self.assertEqual(Comentario.objects.count(), 2)

    def test_borrar_comentario_no_acepta_get(self):
        self.client.force_login(self.miembro)
        respuesta = self.client.get(reverse('borrar_comentario', kwargs={'comentario_id': self.comentario.pk}))
        self.assertEqual(respuesta.status_code, 405)
        self.assertTrue(Comentario.objects.filter(pk=self.comentario.pk).exists())

    def test_el_duenio_borra_su_comentario(self):
        self.client.force_login(self.miembro)
        respuesta = self.client.post(reverse('borrar_comentario', kwargs={'comentario_id': self.comentario.pk}))
        self.assertRedirects(respuesta, reverse('detalle', kwargs={'pk': self.post.pk}))
        self.assertFalse(Comentario.objects.filter(pk=self.comentario.pk).exists())

    def test_otro_miembro_no_puede_borrar_comentarios_ajenos(self):
        self.client.force_login(self.otro)
        self.client.post(reverse('borrar_comentario', kwargs={'comentario_id': self.comentario.pk}))
        self.assertTrue(Comentario.objects.filter(pk=self.comentario.pk).exists())

    def test_colaborador_puede_moderar_cualquier_comentario(self):
        self.client.force_login(self.colaborador)
        self.client.post(reverse('borrar_comentario', kwargs={'comentario_id': self.comentario.pk}))
        self.assertFalse(Comentario.objects.filter(pk=self.comentario.pk).exists())

    def test_solo_el_duenio_edita_su_comentario(self):
        url = reverse('editar_comentario', kwargs={'comentario_id': self.comentario.pk})

        self.client.force_login(self.otro)
        self.client.post(url, {'texto': 'Intento ajeno'})
        self.comentario.refresh_from_db()
        self.assertEqual(self.comentario.texto, 'Mi comentario')

        self.client.force_login(self.miembro)
        self.client.post(url, {'texto': 'Editado por su dueño'})
        self.comentario.refresh_from_db()
        self.assertEqual(self.comentario.texto, 'Editado por su dueño')


class ContactoTests(TestCase):
    def test_envia_el_mensaje_con_datos_completos(self):
        respuesta = self.client.post(reverse('contacto'), {
            'email_usuario': 'alguien@example.com',
            'asunto': 'Consulta',
            'mensaje': 'Hola, tengo una consulta.',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('alguien@example.com', mail.outbox[0].body)

    def test_no_envia_si_faltan_datos(self):
        respuesta = self.client.post(reverse('contacto'), {'email_usuario': 'alguien@example.com'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
