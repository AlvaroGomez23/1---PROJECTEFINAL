from django.shortcuts import render, redirect, get_object_or_404
from .forms import Login, Register, CombinedUserProfileForm, RecoveryPassword, ChangeRecoveryPassword
from django.contrib.auth import authenticate, login as _login, logout as _logout
from django.contrib.auth.models import User
from .models import UserProfile, Notification, Wishlist, Conversation, Review
from books.models import Book
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Avg
from users.utils import send_user_notification, send_user_email, check_veto, search_cities
from cities_light.models import City
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import uuid

# Create your views here.

def login(request):

    if request.user.is_authenticated:
        return redirect('dashboard')
    
    form = Login(request.POST or None)

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        profile = UserProfile.get_user_profile_by_email(email)

        if not profile:
            messages.error(request, "L'usuari no existeix")
        else:
            user = authenticate(request, email=email, password=password)
            if user is not None:
                _login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Correu electrònic o contrasenya incorrectes")

    return render(request, 'login.html', {'form': form})
    

def register(request):

    if request.user.is_authenticated:
        return redirect('dashboard')


    if request.method == 'GET':
        form = Register()
        return render(request, 'register.html', {'form': form})
    
    form = Register(request.POST)
    if not form.is_valid():
        return render(request, 'register.html', {'form': form})

    name = form.cleaned_data['name']
    email = form.cleaned_data['email']
    password = form.cleaned_data['password']
    password2 = form.cleaned_data['password2']

    try:
        # Validar seguretat de la contrasenya
        validate_password(password)
        
        UserProfile.register_user(name, email, password, password2)
        user = authenticate(username=email, password=password)

        if user is None:
            return render(request, 'register.html', {
                'form': form,
                'errors': "Error al registrar l'usuari"
            })

        _login(request, user)
        return redirect('dashboard')

    except ValidationError as ve:
        return render(request, 'register.html', {
            'form': form,
            'errors': "La contrasenya no és segura. Ha de contenir mínim 8 caràcters, majúscules, minúscules i números."
        })

    except ValueError as e:
        return render(request, 'register.html', {
            'form': form,
            'errors': e
        })
    

# Tancar la sessió
def logout(request):
    _logout(request)
    return redirect('index')


def view_profile(request, user_id=None):
    context = UserProfile.obtain_user(user_id, request.user)
    return render(request, 'view_profile.html', context)



@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CombinedUserProfileForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('view_profile', user_id=request.user.pk)
    else:
        form = CombinedUserProfileForm(user=request.user)

    return render(request, 'edit_profile.html', {'form': form})

# Funció per mostrar les notificacions de l'usuari
@login_required
def notifications(request):
    notifications = Notification.get_noti_user(request.user)
    return render(request, 'notifications.html', {
        'notifications': notifications,
    })

# Funció per marcar una notificació com a llegida
@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.mark_as_read()
    return redirect('notifications')

# Funció per mostrar la llista de llibres desitjats de l'usuari 
@login_required
def wishlist(request):
    wishlist = Wishlist.get_or_create_for_user(request.user)

    search_query = request.GET.get('search', '').strip()

    books = wishlist.get_books(search_query) if wishlist else []

    return render(request, 'wishlist.html', {
        'books': books,
        'search_query': search_query,
        'user_wishlist': wishlist,
    })


# Funció per afegir o eliminar llibres de la llista de desitjos
@login_required
def toggle_wishlist(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        book_id = data.get('book_id')
        book = get_object_or_404(Book, pk=book_id)

        wishlist = Wishlist.get_or_create_for_user(request.user)

        status = wishlist.toggle_book(book)  # Método que deberías tener en el modelo

        return JsonResponse({'status': status})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def chat_room(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    if not conversation.has_participant(request.user):
        return redirect('view_profile', user_id=request.user.id)

    other_user = conversation.get_other_participant(request.user)

    return render(request, 'chat.html', {
        'conversation_id': conversation.id,
        'other_user': other_user,
    })


@login_required
def private_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    if request.user == other_user:
        return redirect('view_profile', user_id=request.user.id)

    conversation, created = Conversation.get_or_create_between_users(request.user, other_user)

    if created:
        other_user = conversation.get_other_participant(request.user)
        if other_user:
            send_user_notification(
                other_user, 
                request.user, 
                f"{request.user.first_name} ha començat una conversa amb tu", 
                "Probablement tinguis missatges nous, revisa-ho!", 
                None
            )
            send_user_email(
                other_user,
                f"{request.user.first_name} ha començat una conversa amb tu",
                "Probablement tinguis missatges nous, revisa-ho!",
            )

    return redirect('chat_room', conversation_id=conversation.id)


@login_required
def inbox(request):
    conversation_items = Conversation.get_conversations_for_user(request.user)

    return render(request, 'inbox.html', {
        'conversations': conversation_items,
    })


@login_required
def view_map(request, user_id=None):
    if user_id is None:
        user_profile = request.user.userprofile
    else:
        user_profile = UserProfile.get_profile_for_map(user_id=user_id, current_user=request.user)
        context = user_profile.get_map_context()
        return render(request, 'map_view.html', context)


@require_GET
def city_autocomplete(request):
    term = request.GET.get('term', '').strip()
    if term:
        cities = search_cities(term)
        return JsonResponse(list(cities), safe=False)
    return JsonResponse([], safe=False)


@login_required
def add_review_user(request, user_id):
    user_to_review = get_object_or_404(User, id=user_id)
    veto_response = check_veto(request, user_to_review)
    if veto_response:
        return veto_response

    existing_review = Review.get_review(request.user, user_to_review)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        if not rating:
            messages.error(request, "La puntuació és obligatòria.")
            return redirect('add_review_user', user_id=user_to_review.id)

        review, created = Review.add_or_update_review(
            reviewer=request.user,
            reviewed_user=user_to_review,
            rating=rating,
            comment=comment
        )

        if created:
            messages.success(request, "La teva valoració s'ha afegit correctament.")
        else:
            messages.success(request, "La teva valoració s'ha actualitzat correctament.")

        return redirect('view_profile', user_id=user_to_review.id)

    context = {
        'user_to_review': user_to_review,
        'existing_review': existing_review,
    }
    return render(request, 'add_review_user.html', context)


@login_required
def delete_review_user(request, review_id):
    reviewed_user_id = None

    if request.method == "POST":
        deleted, reviewed_user_id = Review.delete_review(review_id, request.user)
        if deleted:
            messages.success(request, "La valoració s'ha eliminat correctament.")
        else:
            messages.error(request, "No tens permís per eliminar aquesta valoració.")

    return redirect('view_profile', user_id=reviewed_user_id or request.user.id)


def recovery_password(request):
    if request.method == 'POST':
        form = RecoveryPassword(request.POST)  # <-- aquí defines form
        if form.is_valid():
            email = form.cleaned_data['email'].strip()
            user = UserProfile.get_user(email)

            if user:
                recovery_token = uuid.uuid4()

                # Guardar token y enviar email
                user.userprofile.save_token(recovery_token)
                send_user_email(
                    user,
                    "Restablir contrasenya",
                    f"Fes clic aquí per restablir la teva contrasenya: <a href='https://one-projectefinal.onrender.com/users/change_recovery_password/{recovery_token}/'>Clica aquí</a>"
                )

                messages.success(request, "S'ha enviat un correu electrònic a " + email + " per restablir la contrasenya.")
                return redirect('login')
            else:
                messages.error(request, "No s'ha trobat cap usuari amb aquest correu electrònic.")
    else:
        form = RecoveryPassword()

    return render(request, 'recovery_password.html', {'form': form})

def change_recovery_password(request, token):
    if request.method == 'GET':
        form = ChangeRecoveryPassword()
        return render(request, 'change_recovery_password.html', {'form': form})

    form = ChangeRecoveryPassword(request.POST)
    if not form.is_valid():
        return render(request, 'change_recovery_password.html', {'form': form})

    password = form.cleaned_data['password']
    password2 = form.cleaned_data['password2']

    if password != password2:
        messages.error(request, "Les contrasenyes no coincideixen.")
        return render(request, 'change_recovery_password.html', {'form': form})

    try:
        validate_password(password)
    except ValidationError as e:
        messages.error(request, e.messages)
        return render(request, 'change_recovery_password.html', {'form': form})

    user_profile = UserProfile.get_by_token(token)
    if not user_profile:
        messages.error(request, "Token invàlid o caducat.")
        return render(request, 'change_recovery_password.html', {'form': form})

    user_profile.change_password(password)
    messages.success(request, "La contrasenya s'ha canviat correctament.")
    return redirect('login')


def redirect_accounts_login(request):
    if request.method == "GET" and not request.META.get("HTTP_REFERER", "").startswith(request.build_absolute_uri('/accounts/')):
        messages.error(request, "Has estat redirigit al formulari de login.")
        return redirect('login')
    

def redirect_signup_to_login_with_message(request):

    if request.method == "GET":
        messages.error(
            request,
            "No és possible registrar-se amb un compte de tercers. Si ja tens un compte, inicia sessió."
        )
        return redirect('/users/login')