from django.shortcuts import render, redirect, get_object_or_404
from .forms import Login, Register, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login as _login, logout as _logout
from django.contrib.auth.models import User
from .models import UserProfile, Notification, Wishlist, Conversation
from books.models import Book
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
import json
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Create your views here.

def login(request):
    if request.method == 'GET':
        form = Login()
        return render(request, 'login.html', {
            'form': form
        })
    else:
        form = Login(request.POST)
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Search user by email
        user = User.objects.filter(email=email).first()

        if user is None:
            return render(request, 'login.html', {
                'form': form,
                'errors': "L'usuari no existeix"
            })

        # Autenticate user by username and password
        user = authenticate(request, username=user.username, password=password)

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
        return render(request, 'register.html', {
            'form': form
        })
    
    else:
        form = Register(request.POST)
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')


        # Verify if both passwords match
        if password != password2:
            return render(request, 'register.html', {
                'form': form,
                'errors': "Les contrasenyes no coincideixen"
            })

        # Verify that the email is not already in use
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {
                'form': form,
                'errors': "Aquest correu electrònic ja està registrat"
            })

        # Create user and save it
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name
        user.save()

        UserProfile.objects.create(user_id=user.pk)
        return render(request, 'register.html', {
            'form': form,
            'success': "Usuari registrat correctament"
        })
    

def logout(request):
    _logout(request)
    return redirect('index')


def view_profile(request, user_id):
    user = User.objects.filter(pk=user_id).first()
    profile_info = UserProfile.objects.filter(user=user).first()
    

    if user_id is None or user_id == request.user.id:
        user_to_view = request.user
    else:
        # Obtener el perfil de otro usuario
        user_to_view = get_object_or_404(User, id=user_id)

    return render(request, 'view_profile.html', {
        'user': user,
        'profile_info': profile_info,
        'other_user': user_to_view,
    })



@login_required
def edit_profile(request):
    if request.method == 'GET':
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)
    else:
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('view_profile', user_id=request.user.pk)

    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).select_related('exchange').order_by('-created_at')
    return render(request, 'notifications.html', {
        'notifications': notifications,
    })

@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')



@login_required
def wishlist(request):
    wishlist = Wishlist.objects.filter(user=request.user).first()

    # Obtenir els llibres de la relació many to many
    books = wishlist.books.all() if wishlist else []

    return render(request, 'wishlist.html', {'books': books})


@login_required
def toggle_wishlist(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            book_id = data.get('book_id')

            if not book_id:
                return JsonResponse({'error': 'Missing book_id'}, status=400)

            book = get_object_or_404(Book, pk=book_id)

            # Obtener o crear la wishlist del usuario
            wishlist, created = Wishlist.objects.get_or_create(user=request.user)

            if book in wishlist.books.all():
                # Si el libro ya está en la wishlist, eliminarlo
                wishlist.books.remove(book)

                # También eliminar su ISBN de la lista
                isbns = wishlist.get_isbns()
                if book.isbn in isbns:
                    isbns.remove(book.isbn)
                    wishlist.desired_isbns = ','.join(isbns) if isbns else None  # Evitar strings vacíos
                wishlist.save()

                return JsonResponse({'status': 'removed'})
            else:
                # Si el libro no está en la wishlist, agregarlo
                wishlist.books.add(book)

                # Agregar el ISBN
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

    # Redirigir al puerto 8000 para el chat
    chat_url = f"http://127.0.0.1:8000/users/chat/{conversation.id}/"
    return HttpResponseRedirect(chat_url)





