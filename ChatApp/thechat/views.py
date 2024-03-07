from django.shortcuts import render
from .models import Room , Message
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirige al usuario a la página de inicio de sesión
    else:
        form = UserRegistrationForm()
    return render(request, 'registro.html', {'form': form})


# Create your views here.
def rooms(request):
    rooms = Room.objects.all()
    return render(request, "rooms.html",{
        "rooms":rooms
    })

def room(request, slug):
    room = Room.objects.get(slug=slug)
    messages = Message.objects.filter(room=room)
    context = {"slug": slug, "room_name": room.name, "messages": messages}
    return render(request, "room.html", context)

