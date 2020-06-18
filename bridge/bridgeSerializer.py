from rest_framework import serializers
from rest_framework.serializers import CharField,MultipleChoiceField,ValidationError,TimeField,DateTimeField,IntegerField,FileField
from .models import *
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone


class MobilePrefixSerializer(serializers.ModelSerializer):
    class Meta:
        model=MobilePrefix
        fields=('id','name',)
