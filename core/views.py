from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import logout_then_login, PasswordResetConfirmView, PasswordResetView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.template.loader import render_to_string
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType
import uuid
import random

# =========================
# HELPERS
# =========================

def es_admin(user):
    return user.is_staff

def admin_required(view_func):
    return user_passes_test(es_admin, login_url='home')(view_func)

# =========================
# HOME
# =========================

def home(request):
    return render(request, 'core/index.html')

# =========================
# PERFIL
# =========================

@login_required
def perfil(request):
    ventas = Venta.objects.filter(cliente=request.user).order_by('-fecha')
    return render(request, 'core/perfil.html', {'ventas': ventas})

# =========================
# PRODUCTOS
# =========================

def productos(request):
    productos = Producto.objects.all()
    return render(request, 'core/productos.html', {'productos': productos, "carro": request.session.get("carro", [])})

def detalleProducto(request, codigo):
    producto = Producto.objects.get(codigo=codigo)
    productos_relacionados = list(Producto.objects.exclude(codigo=codigo))
    productos_relacionados = random.sample(productos_relacionados, min(len(productos_relacionados), 3))
    context = {
        'producto': producto,
        'productos': productos_relacionados,
    }
    return render(request, 'core/producto.html', context)

def producto(request):
    return render(request, "core/producto.html")

# =========================
# ADMIN PRODUCTOS
# =========================

@login_required
@admin_required
def admin_productos(request):
    productos = Producto.objects.all()
    return render(request, 'core/admin_productos.html', {'productos': productos})

@login_required
@admin_required
def admin_agregar_producto(request):
    categorias = Categoria.objects.all()
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = max(0, int(request.POST.get('precio', 0)))
        stock = max(0, int(request.POST.get('stock', 0)))
        imagen = request.POST.get('imagen')
        categoria_id = request.POST.get('categoria')
        categoria = get_object_or_404(Categoria, id=categoria_id)
        Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            imagen=imagen,
            Categoria=categoria
        )
        return redirect('admin_productos')
    return render(request, 'core/admin_form_producto.html', {'categorias': categorias, 'accion': 'Agregar'})

@login_required
@admin_required
def admin_editar_producto(request, codigo):
    producto = get_object_or_404(Producto, codigo=codigo)
    categorias = Categoria.objects.all()
    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.descripcion = request.POST.get('descripcion')
        producto.precio = max(0, int(request.POST.get('precio', 0)))
        producto.stock = max(0, int(request.POST.get('stock', 0)))
        producto.imagen = request.POST.get('imagen')
        categoria_id = request.POST.get('categoria')
        producto.Categoria = get_object_or_404(Categoria, id=categoria_id)
        producto.save()
        return redirect('admin_productos')
    return render(request, 'core/admin_form_producto.html', {
        'producto': producto,
        'categorias': categorias,
        'accion': 'Editar'
    })

@login_required
@admin_required
def admin_eliminar_producto(request, codigo):
    producto = get_object_or_404(Producto, codigo=codigo)
    if request.method == 'POST':
        producto.delete()
        return redirect('admin_productos')
    return render(request, 'core/admin_confirmar_eliminar.html', {'producto': producto})

# =========================
# CARRO
# =========================

def addtocar(request, codigo):
    producto = Producto.objects.get(codigo=codigo)
    cantidad = int(request.POST.get('quantity', 1))
    carro = request.session.get("carro", [])

    if producto.stock >= cantidad:
        for item in carro:
            if item[0] == codigo:
                item[4] += cantidad
                item[5] = item[3] * item[4]
                producto.stock -= cantidad
                producto.save()
                break
        else:
            carro.append([codigo, producto.nombre, producto.imagen, producto.precio, cantidad, producto.precio * cantidad])
            producto.stock -= cantidad
            producto.save()
        request.session["carro"] = carro
        return redirect(to="productos")

def carro(request):
    carro = request.session.get("carro", [])
    total = sum(item[5] for item in carro)
    superTotal = total + 3490
    carro_vacio = len(carro) == 0
    return render(request, 'core/carro.html', {"total": total, "carro": carro, "superTotal": superTotal, "carro_vacio": carro_vacio})

def eliminar(request, codigo):
    producto = get_object_or_404(Producto, codigo=codigo)
    carro = request.session.get("carro", [])
    for item in carro:
        if item[0] == codigo:
            producto.stock += item[4]
            carro.remove(item)
            producto.save()
            break
    request.session["carro"] = carro
    return redirect(to="carro")

def actualizar_cantidad(request, codigo):
    if request.method == 'POST':
        nueva_cantidad = int(request.POST.get('cantidad', 1))
        if nueva_cantidad < 1:
            nueva_cantidad = 1

        carro = request.session.get("carro", [])

        for item in carro:
            if int(item[0]) == int(codigo):
                producto = get_object_or_404(Producto, codigo=codigo)
                diferencia = nueva_cantidad - item[4]

                if diferencia > 0 and producto.stock < diferencia:
                    break

                producto.stock -= diferencia
                producto.save()
                item[4] = nueva_cantidad
                item[5] = item[3] * nueva_cantidad
                break

        request.session["carro"] = carro
        request.session.modified = True

    return redirect('carro')

def comprar(request):
    carro = request.session.get("carro", [])
    total = 0
    for item in carro:
        total += item[5]
    venta = Venta()
    venta.cliente = request.user
    venta.total = total
    venta.save()

    for item in carro:
        detalle = Detalle()
        detalle.producto = Producto.objects.get(codigo=item[0])
        detalle.precio = item[3]
        detalle.cantidad = item[4]
        detalle.venta = venta
        detalle.save()
    request.session["carro"] = []
    return redirect(to="carro")

def limpiar(request):
    request.session.flush()
    return redirect(to="home")

# =========================
# WEBPAY
# =========================

def iniciar_pago(request):
    carro = request.session.get("carro", [])
    if not carro:
        return redirect('carro')

    total = sum(item[5] for item in carro) + 3490
    orden = str(uuid.uuid4())[:10]
    session_id = str(request.user.id)
    return_url = request.build_absolute_uri('/webpay/retorno/')

    tx = Transaction(WebpayOptions(
        commerce_code='597055555532',
        api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
        integration_type=IntegrationType.TEST
    ))

    response = tx.create(orden, session_id, total, return_url)
    return redirect(response['url'] + '?token_ws=' + response['token'])

def retorno_pago(request):
    token = request.GET.get('token_ws') or request.POST.get('token_ws')

    if not token:
        return redirect('carro')

    tx = Transaction(WebpayOptions(
        commerce_code='597055555532',
        api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
        integration_type=IntegrationType.TEST
    ))

    response = tx.commit(token)

    if response['status'] == 'AUTHORIZED':
        carro = request.session.get("carro", [])
        total = sum(item[5] for item in carro)

        venta = Venta()
        venta.cliente = request.user
        venta.total = total + 3490
        venta.save()

        for item in carro:
            detalle = Detalle()
            detalle.producto = Producto.objects.get(codigo=item[0])
            detalle.precio = item[3]
            detalle.cantidad = item[4]
            detalle.venta = venta
            detalle.save()

        request.session["carro"] = []
        return redirect('pago_exitoso')
    else:
        return redirect('pago_fallido')

def pago_exitoso(request):
    return render(request, 'core/pago_exitoso.html')

def pago_fallido(request):
    return render(request, 'core/pago_fallido.html')

# =========================
# AUTH
# =========================

def registro(request):
    if request.method == "POST":
        registro = Registro(request.POST)
        if registro.is_valid():
            user = registro.save()
            html_message = render_to_string('core/registration/bienvenida_email.html', {
                'username': user.username,
                'email': user.email,
            })
            send_mail(
                subject='¡Bienvenido a ZENITH PERFORMANCE!',
                message=f'Hola {user.username}, bienvenido a ZENITH PERFORMANCE.',
                from_email='noreply@zenithperformance.cl',
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=True,
            )
            return redirect(to="login")
    else:
        registro = Registro()
    return render(request, 'core/registro.html', {'form': registro})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout(request):
    return logout_then_login(request, login_url="login")

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('login')

# =========================
# PAGINAS ESTATICAS
# =========================

def sobreNosotros(request):
    return render(request, 'core/sobrenosotros.html')

def politica(request):
    return render(request, "core/politicaCompra.html")

def compromiso(request):
    return render(request, "core/compromiso.html")