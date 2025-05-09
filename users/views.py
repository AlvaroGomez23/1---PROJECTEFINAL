from django.shortcuts import render, redirect, get_object_or_404
from .forms import Login, Register, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login as _login, logout as _logout
from django.contrib.auth.models import User
from .models import UserProfile, Notification, Wishlist, Conversation, Review
from books.models import Book
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
import json
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Avg
from users.utils import send_user_notification, send_user_email
from cities_light.models import City
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# Create your views here.

def login(request):
    if request.method == 'GET':
        form = Login()
        # Retornar vista amb el formulari
        return render(request, 'login.html', {
            'form': form
        })
    else:
        # Enviar dades de l'usuari i logar-lo
        form = Login(request.POST)
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Buscar el seu mail
        user = User.objects.filter(email=email).first()

        if user is None:
            return render(request, 'login.html', {
                'form': form,
                'errors': "L'usuari no existeix"
            })

        # Autenticar l'usuari
        user = authenticate(request, username=user.username, password=password)

        # Mostrar error si no s'ha pogut autenticar
        if user is None:
            return render(request, 'login.html', {
                'form': form,
                'errors': "Correu electrònic o contrasenya incorrectes"
            })

        # Log in and redirect
        _login(request, user)
        return redirect('dashboard')
    

def register(request):
    if request.method == 'GET':
        form = Register()
        # Retornar vista amb el formulari
        return render(request, 'register.html', {
            'form': form
        })
    
    else:
        # Enviar dades de l'usuari i crear-li un compte
        form = Register(request.POST)
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Verificacions per enregistrar-lo
        if password != password2:
            return render(request, 'register.html', {
                'form': form,
                'errors': "Les contrasenyes no coincideixen"
            })

        # Validar la seguretat de la contrasenya
        try:
            validate_password(password)
        except ValidationError as e:
            return render(request, 'register.html', {
                'form': form,
                'errors': e.messages  # Mostrar els errors de validació
            })

        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {
                'form': form,
                'errors': "Aquest correu electrònic ja està registrat"
            })

        # Crear l'usuari
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name
        user.save()

        UserProfile.objects.create(user_id=user.pk)
        return render(request, 'register.html', {
            'form': form,
            'success': "Usuari registrat correctament"
        })
    

# Tancar la sessió
def logout(request):
    _logout(request)
    return redirect('index')


def view_profile(request, user_id):
    user = User.objects.filter(pk=user_id).first()
    profile_info = UserProfile.objects.filter(user=user).first()
    
    if profile_info.veto:
        veto = True
    else:
        veto = False
    # Si no troba un usuari, mostra les dades del usuari logat
    if user_id is None or user_id == request.user.id:
        user_to_view = request.user
    else:
        # Obtenir perfil de l'altre usuari
        user_to_view = get_object_or_404(User, id=user_id)
        
    reviews = user.user_reviews_received.all()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    return render(request, 'view_profile.html', {
        'user': user,
        'profile_info': profile_info,
        'other_user': user_to_view,
        'reviews': reviews,
        'average_rating': average_rating,
        'veto': veto,
        
    })



@login_required
def edit_profile(request):
    if request.method == 'GET':
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)
    else:
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=request.user.userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            user_profile = profile_form.save(commit=False)

            # Actualizar las coordenadas según la ciudad seleccionada
            if user_profile.city:
                user_profile.latitude = user_profile.city.latitude
                user_profile.longitude = user_profile.city.longitude

            user_profile.save()
            return redirect('view_profile', user_id=request.user.pk)

    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


# Funció per mostrar les notificacions de l'usuari
@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).select_related('exchange').order_by('-created_at')
    return render(request, 'notifications.html', {
        'notifications': notifications,
    })

# Funció per marcar una notificació com a llegida
@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')

# Funció per mostrar la llista de llibres desitjats de l'usuari 
@login_required
def wishlist(request):
    wishlist = Wishlist.objects.filter(user=request.user).first()

    # Obtener los libros de la relación many-to-many
    books = wishlist.books.all() if wishlist else []

    # Obtener los parámetros de búsqueda
    search_query = request.GET.get('search', '').strip()

    # Filtrar los libros por nombre o ISBN
    if search_query:
        books = books.filter(title__icontains=search_query) | books.filter(isbn__icontains=search_query)

    return render(request, 'wishlist.html', {
        'books': books,
        'search_query': search_query,
        'user_wishlist': wishlist,  # Asegúrate de pasar la wishlist del usuario
    })


# Funció per afegir o eliminar llibres de la llista de desitjos
@login_required
def toggle_wishlist(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            book_id = data.get('book_id')

            if not book_id:
                return JsonResponse({'error': 'Missing book_id'}, status=400)

            book = get_object_or_404(Book, pk=book_id)

            # Obtenir o crear la wishlist de l'usuari
            wishlist, created = Wishlist.objects.get_or_create(user=request.user)

            if book in wishlist.books.all():
                # Si el llibre ja està a la wishlist, eliminar-lo
                wishlist.books.remove(book)

                # Eliminar el ISBN de la llista de desitjos
                isbns = wishlist.get_isbns()
                if book.isbn in isbns:
                    isbns.remove(book.isbn)
                    wishlist.desired_isbns = ','.join(isbns) if isbns else None  # Si no té cap llibre com a desitjat, posarà un None a la bd
                wishlist.save()

                return JsonResponse({'status': 'removed'})
            else:
                # En cas contrari, afegir el llibre
                wishlist.books.add(book)

                # Afegir el ISBN
                wishlist.add_isbn(book.isbn)

                return JsonResponse({'status': 'added'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def chat_room(request, conversation_id):
    # Obtener la conversación
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Verificar que el usuario actual sea parte de la conversación
    if request.user not in conversation.participants.all():
        return redirect('view_profile', user_id=request.user.id)

    # Obtener el otro participante (remitente)
    other_user = conversation.participants.exclude(id=request.user.id).first()

    return render(request, 'chat.html', {
        'conversation_id': conversation.id,
        'other_user': other_user,
    })


@login_required
def private_chat(request, user_id):
    # Obtener el usuario con el que se quiere chatear
    other_user = get_object_or_404(User, id=user_id)

    # Verificar que el usuario no está intentando chatear consigo mismo
    if request.user == other_user:
        return redirect('view_profile', user_id=request.user.id)

    # Buscar o crear una conversación entre los dos usuarios
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=other_user).first()
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
        send_user_notification(
            other_user, 
            request.user, 
            f"{request.user.username} ha començat una conversa amb tu", 
            "Probablement tinguis missatges nous, revisa-ho!", 
            None
            )

        send_user_email(
            other_user,
            f"{request.user.username} ha començat una conversa amb tu",
            "Probablement tinguis missatges nous, revisa-ho!",
        )


    # Redirigir al puerto 8000 para el chat
    chat_url = f"/users/chat/{conversation.id}/"
    return HttpResponseRedirect(chat_url)


@login_required
def inbox(request):
    conversations = Conversation.objects.filter(participants=request.user)
    conversation_items = []

    for conversation in conversations:
        other_user = conversation.participants.exclude(id=request.user.id).first()

        item = {
            "conversation": conversation,
            "other_user_id": other_user.id if other_user else None,
            "other_user_name": other_user.username if other_user else "Desconegut",
        }

        conversation_items.append(item)

    return render(request, 'inbox.html', {
        'conversations': conversation_items,
    })

# views.py
@login_required
def view_map(request, user_id=None):
    # Si no se proporciona un user_id, usar el usuario actual
    if user_id is None:
        user_profile = request.user.userprofile
    else:
        # Obtener el perfil del usuario especificado
        user = get_object_or_404(User, pk=user_id)
        user_profile = user.userprofile

    context = {
        'lat': user_profile.latitude,
        'lng': user_profile.longitude,
        'radius': user_profile.movement_radius_km,
        'user': user_profile.user,  # Pasar el usuario al contexto
    }
    return render(request, 'map_view.html', context)


def city_autocomplete(request):
    term = request.GET.get('term', '')
    if term:
        cities = City.objects.filter(name__icontains=term).values('id', 'name')[:10]
        return JsonResponse(list(cities), safe=False)
    return JsonResponse([], safe=False)


@login_required
def add_review_user(request, user_id):
    user_to_review = get_object_or_404(User, id=user_id)
    existing_review = Review.objects.filter(reviewer=request.user, reviewed_user=user_to_review).first()

    user_profile = request.user.userprofile
    if user_profile.veto:
        messages.error(request, "No pots fer valoracions amb el teu perfil actual ja que has sigut vetat.")
        return redirect('view_profile', user_id=user_to_review.id,)

    user_reviewed = user_to_review.userprofile
    if user_reviewed.veto:
        messages.warning(request, "No pots fer valoracions a aquest usuari ja que ha sigut vetat.")
        return redirect('view_profile', user_id=user_to_review.id,)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        if not rating:
            messages.error(request, "La puntuació és obligatòria.")
            return redirect('add_review_user', user_id=user_to_review.id,)

        if existing_review:
            # Actualizar la valoración existente
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
            messages.success(request, "La teva valoració s'ha actualitzat correctament.")
        else:
            # Crear una nueva valoración
            Review.objects.create(
                reviewer=request.user,
                reviewed_user=user_to_review,
                rating=rating,
                comment=comment
            )
            messages.success(request, "La teva valoració s'ha afegit correctament.")

        return redirect('view_profile', user_id=user_to_review.id)

    context = {
        'user_to_review': user_to_review,
        'existing_review': existing_review,
    }
    return render(request, 'add_review_user.html', context)


@login_required
def delete_review_user(request, review_id):
    review = get_object_or_404(Review, id=review_id, reviewer=request.user)


    if request.method == "POST":
        review.delete()
        messages.success(request, "La valoració s'ha eliminat correctament.")

    return redirect('view_profile', user_id=review.reviewed_user.id)