from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect, get_object_or_404
from django.http import Http404
from home.models import Blog
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.db.models import Q
import random
import re

# Create your views here.
def index(request):
    blogs = Blog.objects.all()
    numero_blogs = blogs.count()
    numero_a_seleccionar = min(3, numero_blogs)
    random_blogs = random.sample(list(blogs), numero_a_seleccionar)
    context = {'random_blogs': random_blogs}
    return render(request, 'index.html', context)

def about(request):
    return render(request, 'about.html')

def thanks(request):
    return render(request, 'thanks.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        invalid_imput = ['', ' ']
        if name in invalid_imput or email in invalid_imput or phone in invalid_imput or message in invalid_imput:
            messages.error(request, 'One or more fields are empty!')
        else:
            email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            phone_pattern = re.compile(r'^[0-9]{10}$')

            if email_pattern.match(email) and phone_pattern.match(phone):
                form_data = {
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'message': message,
                }
                message = '''
                From:\n\t\t{}\n
                Message:\n\t\t{}\n
                Email:\n\t\t{}\n
                Phone:\n\t\t{}\n
                '''.format(form_data['name'], form_data['message'], form_data['email'], form_data['phone'])
                send_mail('You got a mail!', message, '', ['dev.ash.py@gmail.com'])
                messages.success(request, 'Your message was sent.')
            else:
                messages.error(request, 'Email or Phone is Invalid!')
    return render(request, 'contact.html', {})

def projects(request):
    return render(request, 'projects.html')

def blog(request):
    blogs = Blog.objects.all().order_by('-time')
    paginator = Paginator(blogs, 3)
    page = request.GET.get('page')
    blogs = paginator.get_page(page)
    context = {'blogs': blogs}
    return render(request, 'blog.html', context)

def category(request, category):
    category_posts = Blog.objects.filter(category=category).order_by('-time')
    if not category_posts:
        message = f"No posts found in category: '{category}'"
        return render(request, "category.html", {"message": message})
    paginator = Paginator(category_posts, 3)
    page = request.GET.get('page')
    category_posts = paginator.get_page(page)
    return render(request, "category.html", {"category": category, 'category_posts': category_posts})

def categories(request):
    all_categories = Blog.objects.values('category').distinct().order_by('category')
    return render(request, "categories.html", {'all_categories': all_categories})

def search(request):
    query = request.GET.get('q', '').strip()
    if query:
        # Guardar la búsqueda en la sesión
        if 'recent_searches' not in request.session:
            request.session['recent_searches'] = []
        if query not in request.session['recent_searches']:
            request.session['recent_searches'] = [query] + request.session['recent_searches'][:4]  # Limitar a 5 búsquedas recientes
            request.session.modified = True

        # Realizar la búsqueda
        results = Blog.objects.filter(Q(title__icontains=query) | Q(content__icontains=query)).order_by('-time')
    else:
        results = Blog.objects.none()

    message = "Sin resultados" if not results else ""
    context = {
        'results': results,
        'query': query,
        'message': message,
    }
    return render(request, 'search.html', context)

def blogpost(request, slug):
    try:
        blog = Blog.objects.get(slug=slug)
        context = {'blog': blog}
        return render(request, 'blogpost.html', context)
    except Blog.DoesNotExist:
        context = {'message': 'Blog post not found'}
        return render(request, '404.html', context, status=404)