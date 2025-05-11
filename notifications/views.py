from rest_framework import status
from rest_framework.generics import DestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .models import Notification
from .serializers import NotificationSerializer
from django.shortcuts import get_object_or_404


class NotificationListView(APIView):
    """
    API endpoint for retrieving user notifications.
    
    Lists all notifications for the currently authenticated user.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List user notifications",
        operation_description="Returns a list of all notifications for the current user",
        responses={
            200: NotificationSerializer(many=True),
            401: "Authentication credentials were not provided"
        },
        security=[{'Bearer': []}]
    )
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class NotificationUnreadCountView(APIView):
    """
    API endpoint for retrieving the number of unread notifications.
    
    Returns a count of unread notifications for the currently authenticated user.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get unread notification count",
        operation_description="Returns the count of unread notifications for the current user",
        responses={
            200: openapi.Response(
                description="Unread notification count",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'unread_count': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Number of unread notifications"
                        )
                    }
                )
            ),
            401: "Authentication credentials were not provided"
        },
        security=[{'Bearer': []}]
    )
    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread_count": count})


class MarkAllAsRead(APIView):
    """
    API endpoint for marking all notifications as read.
    
    Updates all unread notifications of the current user to be marked as read.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Mark all notifications as read",
        operation_description="Updates all unread notifications to be marked as read",
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
            401: "Authentication credentials were not provided"
        },
        security=[{'Bearer': []}]
    )
    def patch(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"status": "all marked as read"})


class DeleteNotification(DestroyAPIView):
    """
    API endpoint for deleting a notification.
    
    Removes a specific notification for the current user.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Delete notification",
        operation_description="Deletes a specific notification belonging to the current user",
        manual_parameters=[
            openapi.Parameter(
                'pk', 
                openapi.IN_PATH, 
                description="ID of the notification", 
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            204: "No content - Successfully deleted",
            401: "Authentication credentials were not provided",
            404: "Notification not found"
        },
        security=[{'Bearer': []}]
    )
    def delete(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk, user=request.user)
        notif.delete()
        return Response({"status": "deleted"}, status=status.HTTP_204_NO_CONTENT)
