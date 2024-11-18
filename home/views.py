from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib import messages
from home.models import Blog
import random
import re

# Página principal
def index(request):
    # Posts para el slider
    posts = Blog.objects.filter(thumbnail_img__isnull=False).order_by('-time')[:5]

    # Si no hay posts con imágenes, usa imágenes estáticas genéricas
    if not posts.exists():
        posts = [
            {
                "title": "Ejemplo 1",
                "thumbnail_img": None,
                "url": "/static/images/default1.jpg",
            },
            {
                "title": "Ejemplo 2",
                "thumbnail_img": None,
                "url": "/static/images/default2.jpg",
            },
        ]

    # Blogs aleatorios
    blogs = Blog.objects.all()
    random_blogs = random.sample(list(blogs), min(3, len(blogs))) if blogs else []

    # Contexto
    context = {
        'posts': posts,           # Posts para el slider
        'random_blogs': random_blogs,  # Publicaciones aleatorias
    }
    return render(request, 'index.html', context)



# Página "Sobre Nosotros"
def about(request):
    return render(request, 'about.html')

# Página de agradecimiento
def thanks(request):
    return render(request, 'thanks.html')

# Página de contacto
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        if not all([name.strip(), email.strip(), phone.strip(), message.strip()]):
            messages.error(request, 'Por favor, completa todos los campos.')
        else:
            email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            phone_pattern = re.compile(r'^[0-9]{10}$')

            if email_pattern.match(email) and phone_pattern.match(phone):
                # Enviar correo
                formatted_message = f"De: {name}\nMensaje: {message}\nCorreo: {email}\nTeléfono: {phone}"
                send_mail('Nuevo mensaje de contacto', formatted_message, '', ['your_email@example.com'])
                messages.success(request, 'Tu mensaje fue enviado con éxito.')
            else:
                messages.error(request, 'El correo o el teléfono son inválidos.')
    return render(request, 'contact.html')

# Página de proyectos
def projects(request):
    return render(request, 'projects.html')

# Página de blog con paginación
def blog(request):
    blogs = Blog.objects.all().order_by('-time')
    paginator = Paginator(blogs, 3)
    page = request.GET.get('page')
    blogs = paginator.get_page(page)
    return render(request, 'blog.html', {'blogs': blogs})

# Página de categorías específicas
def category(request, category):
    category_posts = Blog.objects.filter(category=category).order_by('-time')
    if not category_posts:
        return render(request, "category.html", {"message": f"No se encontraron publicaciones en la categoría: {category}"})
    paginator = Paginator(category_posts, 3)
    page = request.GET.get('page')
    category_posts = paginator.get_page(page)
    return render(request, "category.html", {"category": category, "category_posts": category_posts})

# Página de todas las categorías
def categories(request):
    all_categories = Blog.objects.values('category').distinct().order_by('category')
    return render(request, "categories.html", {'all_categories': all_categories})

# Página de búsqueda con almacenamiento de búsquedas recientes
def search(request):
    query = request.GET.get('q', '').strip()
    if query:
        # Guardar búsqueda en sesión (hasta 5 búsquedas recientes)
        recent_searches = request.session.get('recent_searches', [])
        if query not in recent_searches:
            recent_searches = [query] + recent_searches[:4]
            request.session['recent_searches'] = recent_searches

        # Realizar búsqueda en el modelo Blog
        results = Blog.objects.filter(Q(title__icontains=query) | Q(content__icontains=query)).order_by('-time')
    else:
        results = Blog.objects.none()

    return render(request, 'search.html', {
        'results': results,
        'query': query,
        'message': "Sin resultados" if not results else "",
        'recent_searches': request.session.get('recent_searches', []),
    })

# Página de una publicación específica
def blogpost(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    return render(request, 'blogpost.html', {'blog': blog})
