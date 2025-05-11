from rest_framework import generics, permissions
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied

from teams.models import Team
from .models import ThesisTopic
from .serializers import ThesisTopicSerializer


class ThesisTopicCreateView(generics.CreateAPIView):
    """
    API endpoint for creating a new thesis topic.
    
    Allows students and supervisors to create a thesis topic.
    Authentication is required.
    """
    queryset = ThesisTopic.objects.all()
    serializer_class = ThesisTopicSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Create thesis topic",
        operation_description="Create a new thesis topic. Available to authenticated students and supervisors.",
        request_body=ThesisTopicSerializer,
        responses={
            201: ThesisTopicSerializer,
            400: "Bad Request - Invalid data",
            401: "Authentication credentials were not provided"
        },
        security=[{'Bearer': []}]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ThesisTopicListView(generics.ListAPIView):
    """
    API endpoint for listing all thesis topics.
    
    Lists all thesis topics in the system. No authentication required.
    """
    queryset = ThesisTopic.objects.all()
    serializer_class = ThesisTopicSerializer
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_summary="List thesis topics",
        operation_description="Returns a list of all thesis topics in the system",
        responses={
            200: ThesisTopicSerializer(many=True)
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ThesisTopicDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a specific thesis topic.
    
    Retrieves detailed information about a single thesis topic by its ID.
    No authentication required.
    """
    queryset = ThesisTopic.objects.all()
    serializer_class = ThesisTopicSerializer
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Get thesis topic details",
        operation_description="Retrieve detailed information about a specific thesis topic",
        manual_parameters=[
            openapi.Parameter(
                'pk', 
                openapi.IN_PATH, 
                description="ID of the thesis topic", 
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: ThesisTopicSerializer,
            404: "Thesis topic not found"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ThesisTopicUpdateView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for updating a thesis topic.
    
    Allows team owners to update their thesis topics.
    Authentication required.
    """
    queryset = ThesisTopic.objects.all()
    serializer_class = ThesisTopicSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get thesis topic for editing",
        operation_description="Retrieve a thesis topic for editing. Only available to the team owner.",
        manual_parameters=[
            openapi.Parameter(
                'pk', 
                openapi.IN_PATH, 
                description="ID of the thesis topic", 
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: ThesisTopicSerializer,
            403: "You do not own this topic",
            404: "Thesis topic not found"
        },
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update thesis topic",
        operation_description="Update a thesis topic. Only available to the team owner.",
        manual_parameters=[
            openapi.Parameter(
                'pk', 
                openapi.IN_PATH, 
                description="ID of the thesis topic", 
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        request_body=ThesisTopicSerializer,
        responses={
            200: ThesisTopicSerializer,
            400: "Bad Request - Invalid data",
            403: "You do not own this topic",
            404: "Thesis topic not found"
        },
        security=[{'Bearer': []}]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
        
    @swagger_auto_schema(
        operation_summary="Partially update thesis topic",
        operation_description="Partially update a thesis topic. Only available to the team owner.",
        manual_parameters=[
            openapi.Parameter(
                'pk', 
                openapi.IN_PATH, 
                description="ID of the thesis topic", 
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        request_body=ThesisTopicSerializer,
        responses={
            200: ThesisTopicSerializer,
            400: "Bad Request - Invalid data",
            403: "You do not own this topic",
            404: "Thesis topic not found"
        },
        security=[{'Bearer': []}]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        team = Team.objects.filter(thesis_topic=obj).first()
        # Проверка, что только owner может редактировать
        if not team or team.owner != user:
            raise PermissionDenied("You do not own this topic.")
        return obj