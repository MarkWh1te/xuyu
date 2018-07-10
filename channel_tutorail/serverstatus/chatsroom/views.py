import json
from django.shortcuts import render
from django.utils.safestring import mark_safe

from .models import Room


def index(request):
    return render(request, 'chatsroom/index.html', {})


def room(request, room_name):
    return render(request, 'chatsroom/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })


def chat_room(request, label):
    # If the room with the given label doesn't exist, automatically create it
    # upon first visit (a la etherpad).
    room, created = Room.objects.get_or_create(label=label)

    # We want to show the last 50 messages, ordered most-recent-last
    messages = reversed(room.messages.order_by('-timestamp')[:50])

    return render(request, "chatsroom/room.html", {
        'room': room,
        'messages': messages,
    })
