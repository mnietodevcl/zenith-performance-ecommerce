from django.urls import path
from .views import *
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views 
 
urlpatterns = [
    path('', home, name="home"),
    path('login', LoginView.as_view(template_name='core/login.html', redirect_authenticated_user=True), name="login"),
    path('logout', logout, name="logout"),
    path('carro', carro, name="carro"),
    path('comprar', comprar, name="comprar"),
    path('addtocar/<codigo>', addtocar, name="addtocar"),
    path('eliminar/<codigo>', eliminar, name="eliminar"),
    path('sobrenosotros', sobreNosotros, name="about"),
    path('productos', productos, name="productos"),
    path('registro', registro, name="registro"),
    path('limpiar', limpiar, name="limpiar"),
    path('producto/<codigo>', detalleProducto, name='producto'),
    path('agregarCarroProducto/<str:codigo>/', addtocar, name='agregarCarroProducto'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='core/registration/password_reset_form.html',
        html_email_template_name='core/registration/password_reset_email.html',
        email_template_name='core/registration/password_reset_email.txt',
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='core/registration/password_reset_done.html',
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='core/registration/password_reset_confirm.html',
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='core/registration/password_reset_complete.html',
    ), name='password_reset_complete'),
    path('politicaCompra', politica, name="politica"),
    path('compromiso', compromiso, name="compromiso"),
    path('actualizar/<int:codigo>/', actualizar_cantidad, name='actualizar_cantidad'),
    path('perfil', perfil, name='perfil'),
    path('webpay/pagar/', iniciar_pago, name='iniciar_pago'),
    path('webpay/retorno/', retorno_pago, name='retorno_pago'),
    path('webpay/exitoso/', pago_exitoso, name='pago_exitoso'),
    path('webpay/fallido/', pago_fallido, name='pago_fallido'),
    path('admin-productos/', admin_productos, name='admin_productos'),
    path('admin-productos/agregar/', admin_agregar_producto, name='admin_agregar_producto'),
    path('admin-productos/editar/<int:codigo>/', admin_editar_producto, name='admin_editar_producto'),
    path('admin-productos/eliminar/<int:codigo>/', admin_eliminar_producto, name='admin_eliminar_producto'),
]