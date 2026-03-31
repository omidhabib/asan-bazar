import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from .models import Conversation, Message
from ads.models import Ad
from django.conf import settings


class ConversationListView(LoginRequiredMixin, View):
    """Show all conversations for the logged-in user."""
    def get(self, request):
        conversations = (
            request.user.conversations
            .prefetch_related('participants', 'messages')
            .select_related('ad')
            .order_by('-created_at')
        )
        # Annotate with last message
        conv_data = []
        for conv in conversations:
            last_msg = conv.messages.last()
            other = conv.other_participant(request.user)
            conv_data.append({
                'conversation': conv,
                'last_message': last_msg,
                'other_user': other,
                'unread': conv.messages.filter(is_read=False).exclude(sender=request.user).count(),
            })
        return render(request, 'chat/conversation_list.html', {'conv_data': conv_data})


class ConversationDetailView(LoginRequiredMixin, View):
    """Show messages inside a conversation."""
    def get(self, request, pk):
        conv = get_object_or_404(Conversation, pk=pk, participants=request.user)
        # Mark messages as read
        conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        messages_qs = conv.messages.select_related('sender').all()
        other = conv.other_participant(request.user)
        return render(request, 'chat/chat.html', {
            'conversation': conv,
            'messages': messages_qs,
            'other_user': other,
        })

    def post(self, request, pk):
        conv = get_object_or_404(Conversation, pk=pk, participants=request.user)
        content = request.POST.get('content', '').strip()
        if content:
            msg = Message.objects.create(conversation=conv, sender=request.user, content=content)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'id': msg.pk,
                    'sender': msg.sender.full_name,
                    'content': msg.content,
                    'timestamp': msg.timestamp.strftime('%H:%M'),
                    'is_self': True,
                })
        return redirect('conversation_detail', pk=pk)


class StartConversationView(LoginRequiredMixin, View):
    """Start or get existing conversation with an ad's seller."""
    def post(self, request, ad_pk):
        ad = get_object_or_404(Ad, pk=ad_pk, is_active=True)
        seller = ad.user

        if seller == request.user:
            return redirect('ad_detail', pk=ad_pk)

        # Find existing conversation or create
        existing = Conversation.objects.filter(
            participants=request.user, ad=ad
        ).filter(participants=seller).first()

        if existing:
            return redirect('conversation_detail', pk=existing.pk)

        conv = Conversation.objects.create(ad=ad)
        conv.participants.add(request.user, seller)
        return redirect('conversation_detail', pk=conv.pk)


class GetMessagesView(LoginRequiredMixin, View):
    """AJAX endpoint: poll for new messages after a given message ID."""
    def get(self, request, pk):
        conv = get_object_or_404(Conversation, pk=pk, participants=request.user)
        after_id = request.GET.get('after', 0)
        msgs = conv.messages.filter(pk__gt=after_id).select_related('sender')
        # Mark as read
        msgs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        data = [{
            'id': m.pk,
            'sender': m.sender.full_name,
            'content': m.content,
            'timestamp': m.timestamp.strftime('%H:%M'),
            'is_self': m.sender == request.user,
        } for m in msgs]
        return JsonResponse({'messages': data})
