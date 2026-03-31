from django.urls import path
from .views import ConversationListView, ConversationDetailView, StartConversationView, GetMessagesView

urlpatterns = [
    path('messages/', ConversationListView.as_view(), name='conversation_list'),
    path('messages/<int:pk>/', ConversationDetailView.as_view(), name='conversation_detail'),
    path('messages/start/<int:ad_pk>/', StartConversationView.as_view(), name='start_conversation'),
    path('messages/<int:pk>/poll/', GetMessagesView.as_view(), name='get_messages'),
]
