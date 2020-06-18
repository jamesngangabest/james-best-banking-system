from rest_framework import serializers
from  administration.models.authorization import SecurityQuestions
class   SecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model= SecurityQuestions
        fields =('id','name',)
