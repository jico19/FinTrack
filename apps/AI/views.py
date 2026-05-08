from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .services import get_coach_response
from .models import ChatMessage
from django.utils.safestring import mark_safe
import markdown

@login_required
def chatbot_view(request):
    """
    Main chatbot interface view.
    """
    messages = ChatMessage.objects.filter(user=request.user).order_by('created_at')
    for msg in messages:
        msg.content_html = mark_safe(markdown.markdown(msg.content))
    return render(request, 'AI/chatbot_partial.html', {'messages': messages})

@login_required
def send_message(request):
    """
    Endpoint to handle sending a message and returning the AI response.
    """
    user_text = request.POST.get('message')
    if not user_text:
        return HttpResponse(status=400)
    
    ai_text = get_coach_response(request.user, user_text)
    
    messages = ChatMessage.objects.filter(user=request.user).order_by('created_at')
    for msg in messages:
        msg.content_html = mark_safe(markdown.markdown(msg.content))
        
    return render(request, 'AI/chat_messages_partial.html', {'messages': messages})

@login_required
def clear_chat(request):
    """
    Reset chat history.
    """
    ChatMessage.objects.filter(user=request.user).delete()
    return HttpResponse("", headers={"HX-Trigger": "chatCleared"})
