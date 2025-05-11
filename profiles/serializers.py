from rest_framework import serializers

from .models import StudentProfile, SupervisorProfile, DeanOfficeProfile, Skill
from profiles.serializers_shared import SkillSerializer

class StudentProfileSerializer(serializers.ModelSerializer):
    """ Serializer for Student Profile """
    skills = SkillSerializer(many=True, read_only=True)
    skill_ids = serializers.PrimaryKeyRelatedField(queryset=Skill.objects.all(), many=True, write_only=True, source='skills')
    is_profile_completed = serializers.BooleanField(source="user.is_profile_completed", read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = StudentProfile
        fields = '__all__'

    def validate_skill_ids(self, value):
        if len(value) > 5:
            raise serializers.ValidationError("Students can select a maximum of 5 skills.")
        return value

    def update(self, instance, validated_data):
        skills = validated_data.pop('skills', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if skills is not None:
            instance.skills.set(skills)
        instance.update_profile_completion()
        return instance


class SupervisorProfileSerializer(serializers.ModelSerializer):
    """ Serializer for Supervisor Profile """
    skills = SkillSerializer(many=True, read_only=True)
    skill_ids = serializers.PrimaryKeyRelatedField(queryset=Skill.objects.all(), many=True, write_only=True, source='skills')
    is_profile_completed = serializers.BooleanField(source="user.is_profile_completed", read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    projects = serializers.SerializerMethodField()

    class Meta:
        model = SupervisorProfile
        fields = '__all__'

    def get_projects(self, obj):
        from teams.models import Team
        from teams.serializers import TeamSerializer  # 👈 Lazy import to avoid circular
        teams = Team.objects.filter(supervisor=obj)
        return TeamSerializer(teams, many=True).data

    def validate_skill_ids(self, value):
        if len(value) > 10:
            raise serializers.ValidationError("Supervisors can select a maximum of 10 skills.")
        return value

    def update(self, instance, validated_data):
        skills = validated_data.pop('skills', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if skills is not None:
            instance.skills.set(skills)
        instance.update_profile_completion()
        return instance

class SupervisorShortSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    """ Лёгкий сериализатор супервизора без проектов """
    class Meta:
        model = SupervisorProfile
        fields = ['id', 'first_name', 'last_name', 'photo']

class DeanOfficeProfileSerializer(serializers.ModelSerializer):
    """ Serializer for Dean Office Profile """
    is_profile_completed = serializers.BooleanField(source="user.is_profile_completed", read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = DeanOfficeProfile
        fields = '__all__'

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.update_profile_completion()
        return instance
