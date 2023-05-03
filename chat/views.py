from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


@login_required
def course_chat_room(request, course_pk):
    try:
        course = request.user.courses_joined.get(pk=course_pk)
    except:
        return HttpResponseForbidden()
    return render(request, 'chat/room.html', {'course': course})
