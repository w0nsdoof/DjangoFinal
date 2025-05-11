from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from teams.models import Team
from teams.serializers import TeamSerializer
from .models import StudentProfile, SupervisorProfile, DeanOfficeProfile, Skill
from .serializers import (
    StudentProfileSerializer,
    SupervisorProfileSerializer,
    DeanOfficeProfileSerializer,
    SkillSerializer
)

User = get_user_model()


class SkillListView(generics.ListAPIView):
    """
    API endpoint to list all available skills.
    
    Returns a list of all skills that can be associated with profiles.
    """
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="List all skills",
        operation_description="Returns a list of all available skills",
        responses={
            200: SkillSerializer(many=True),
            401: "Authentication credentials were not provided"
        },
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProfileCompletionView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to retrieve and update user profile (Student, Supervisor, Dean Office).
    
    - Users can only access their own profile
    - Returns and updates the specific profile type based on the user's role
    - Ensures profile completion status is updated
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get current user's profile",
        operation_description="Retrieves the profile for the current authenticated user based on their role",
        responses={
            200: "User profile based on role (Student, Supervisor, or Dean Office)",
            400: "Invalid role",
            401: "Authentication credentials were not provided"
        },
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
        
    @swagger_auto_schema(
        operation_summary="Update current user's profile",
        operation_description="Updates the profile for the current authenticated user based on their role",
        responses={
            200: openapi.Response(
                description="Profile updated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'is_profile_completed': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            400: "Invalid data or role",
            401: "Authentication credentials were not provided"
        },
        security=[{'Bearer': []}]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
        
    @swagger_auto_schema(
        operation_summary="Partially update current user's profile",
        operation_description="Partially updates the profile for the current authenticated user based on their role",
        responses={
            200: openapi.Response(
                description="Profile updated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'is_profile_completed': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            400: "Invalid data or role",
            401: "Authentication credentials were not provided"
        },
        security=[{'Bearer': []}]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_serializer_class(self):
        """ Returns the correct serializer based on user role """
        user = self.request.user
        if user.role == "Student":
            return StudentProfileSerializer
        elif user.role == "Supervisor":
            return SupervisorProfileSerializer
        elif user.role == "Dean Office":
            return DeanOfficeProfileSerializer
        return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        """ Return the appropriate profile based on user role """
        user = self.request.user
        if user.role == "Student":
            return user.student_profile
        elif user.role == "Supervisor":
            return user.supervisor_profile
        elif user.role == "Dean Office":
            return user.dean_office_profile
        return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """ Update the user profile and check if completed """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # This will trigger the profile completion check

        return Response({"message": "Profile updated successfully", "is_profile_completed": instance.user.is_profile_completed})

class StudentProfileDetailView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve details of a specific student profile.
    
    Returns student's profile information along with their team information if available.
    """
    queryset = StudentProfile.objects.all()
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Get student profile",
        operation_description="Retrieves detailed information about a student's profile including team information if available",
        manual_parameters=[
            openapi.Parameter(
                'pk', 
                openapi.IN_PATH, 
                description="Student profile ID", 
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: StudentProfileSerializer,
            404: "Student not found"
        }
    )
    def get(self, request, pk):
        try:
            profile = StudentProfile.objects.get(pk=pk)
        except StudentProfile.DoesNotExist:
            return Response({"detail": "Student not found."}, status=404)

        serializer = StudentProfileSerializer(profile)
        data = serializer.data

        # ✅ Импортируем TeamSerializer внутри метода, чтобы избежать цикличности
        team = profile.teams.first()
        if team:
            from teams.serializers import TeamSerializer
            team_serializer = TeamSerializer(team, context={"request": request})
            data['team'] = team_serializer.data
        else:
            data['team'] = None

        return Response(data)

class SupervisorListView(generics.ListAPIView):
    """
    API endpoint to list all supervisors with their profiles and skills.
    
    Returns a list of all supervisors in the system.
    """
    queryset = SupervisorProfile.objects.all()
    serializer_class = SupervisorProfileSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List all supervisors",
        operation_description="Returns a list of all supervisors with their profiles and skills",
        responses={
            200: SupervisorProfileSerializer(many=True),
            401: "Authentication credentials were not provided"
        },
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class SupervisorProfileDetailView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve a supervisor's profile details.
    
    Publicly accessible endpoint to view a supervisor's profile information.
    """
    queryset = SupervisorProfile.objects.all()
    serializer_class = SupervisorProfileSerializer
    permission_classes = [permissions.AllowAny]  # Публичный доступ

    @swagger_auto_schema(
        operation_summary="Get supervisor profile",
        operation_description="Retrieves detailed information about a supervisor's profile",
        manual_parameters=[
            openapi.Parameter(
                'pk', 
                openapi.IN_PATH, 
                description="Supervisor profile ID", 
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: SupervisorProfileSerializer,
            404: "Supervisor not found"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

