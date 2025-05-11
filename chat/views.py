from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from chat.models import Chat, Message, UserStatus
from users.models import CustomUser
from chat.serializers import ChatSerializer, MessageSerializer, UserStatusSerializer
from django.shortcuts import get_object_or_404
from datetime import timedelta
from django.utils import timezone

class ChatListView(generics.ListAPIView):
    """
    API endpoint for listing all user's chats.
    
    Returns a list of all chats where the current user is a participant.
    """
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List user's chats",
        operation_description="Returns a list of all chats where the current user is a participant",
        responses={
            200: ChatSerializer(many=True),
            401: "Authentication credentials were not provided"
        },
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Chat.objects.filter(participants=self.request.user)


class ChatDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving details of a specific chat.
    
    Returns details of a chat where the current user is a participant.
    """
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'chat_id'

    @swagger_auto_schema(
        operation_summary="Get chat details",
        operation_description="Retrieves details of a specific chat where the current user is a participant",
        manual_parameters=[
            openapi.Parameter(
                'chat_id', 
                openapi.IN_PATH, 
                description="ID of the chat", 
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: ChatSerializer,
            401: "Authentication credentials were not provided",
            404: "Chat not found"
        },
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Chat.objects.filter(participants=self.request.user)


class MessageListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating messages in a chat.
    
    Retrieves all messages in a chat or creates a new message.
    User must be a participant in the chat.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List chat messages",
        operation_description="Returns a list of all messages in a chat where the current user is a participant",
        manual_parameters=[
            openapi.Parameter(
                'chat_id', 
                openapi.IN_PATH, 
                description="ID of the chat", 
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: MessageSerializer(many=True),
            401: "Authentication credentials were not provided",
            404: "Chat not found"
        },
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a message",
        operation_description="Creates a new message in a chat where the current user is a participant",
        manual_parameters=[
            openapi.Parameter(
                'chat_id', 
                openapi.IN_PATH, 
                description="ID of the chat", 
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        request_body=MessageSerializer,
        responses={
            201: MessageSerializer,
            400: "Bad Request - Invalid data",
            401: "Authentication credentials were not provided",
            404: "Chat not found"
        },
        security=[{'Bearer': []}]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, id=chat_id, participants=self.request.user)
        return Message.objects.filter(chat=chat)

    def perform_create(self, serializer):
        chat = get_object_or_404(Chat, id=self.kwargs['chat_id'], participants=self.request.user)
        serializer.save(sender=self.request.user, chat=chat)


class MarkMessageReadView(APIView):
    """
    API endpoint for marking a message as read.
    
    Updates a specific message to be marked as read.
    User must be a participant in the chat containing the message.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Mark message as read",
        operation_description="Updates a message to be marked as read",
        manual_parameters=[
            openapi.Parameter(
                'id', 
                openapi.IN_PATH, 
                description="ID of the message", 
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Success response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Status message"
                        )
                    }
                )
            ),
            401: "Authentication credentials were not provided",
            404: "Message not found"
        },
        security=[{'Bearer': []}]
    )
    def patch(self, request, id):
        msg = get_object_or_404(Message, id=id, chat__participants=request.user)
        msg.is_read = True
        msg.save()
        return Response({"status": "marked as read"})


class UserStatusView(APIView):
    """
    API endpoint for retrieving a user's online status.
    
    Returns the online status of a specific user.
    """
    
    @swagger_auto_schema(
        operation_summary="Get user online status",
        operation_description="Returns whether a user is online based on their last activity",
        manual_parameters=[
            openapi.Parameter(
                'user_id', 
                openapi.IN_PATH, 
                description="ID of the user", 
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="User status",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'last_seen': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                        'is_online': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            404: "User status not found"
        }
    )
    def get(self, request, user_id):
        status = get_object_or_404(UserStatus, user__id=user_id)
        serializer = UserStatusSerializer(status)
        data = serializer.data

        now = timezone.now()
        last_seen = status.last_seen

        # Если прошло больше 60 секунд с момента последнего пинга
        if now - last_seen > timedelta(seconds=60):
            data["is_online"] = False
        else:
            data["is_online"] = True

        return Response(data)

@swagger_auto_schema(
    method='post',
    operation_summary="Start or get a chat",
    operation_description="Creates a new chat between the current user and another user, or returns an existing chat",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_id'],
        properties={
            'user_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="ID of the user to start a chat with"
            )
        }
    ),
    responses={
        200: ChatSerializer,
        201: ChatSerializer,
        400: "Bad Request - Missing user_id",
        401: "Authentication credentials were not provided",
        404: "User not found"
    },
    security=[{'Bearer': []}]
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_or_get_chat(request):
    """
    API endpoint for starting or retrieving a chat with another user.
    
    Creates a new chat between the current user and another user if one doesn't exist,
    or returns an existing chat if it does.
    """
    target_user_id = request.data.get("user_id")
    if not target_user_id:
        return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        target_user = CustomUser.objects.get(id=target_user_id)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    current_user = request.user

    # Поиск существующего чата с этими двумя участниками
    existing_chats = Chat.objects.filter(participants=current_user).filter(participants=target_user)
    for chat in existing_chats:
        if chat.participants.count() == 2:
            serializer = ChatSerializer(chat)
            return Response(serializer.data, status=status.HTTP_200_OK)

    # Чата нет — создаём новый
    new_chat = Chat.objects.create()
    new_chat.participants.set([current_user, target_user])
    new_chat.save()

    serializer = ChatSerializer(new_chat)
    return Response(serializer.data, status=status.HTTP_201_CREATED)