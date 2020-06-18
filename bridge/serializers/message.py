from rest_framework import serializers

from bridge.models.models import EmailMessage,MessageTemplates,MessagePolicyDays
from bridge.models.messages import *
from bridge.models.commonEnums import MessageTemplateEnum,MessageTypes
from rest_framework.response import Response
from rest_framework.views import APIView

class MessageSerializer(serializers.ModelSerializer):
    username =serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    def get_username(self,obj):
        if obj.user:
            return obj.user.username
        
        else:
            return None
    def get_email(self, obj):
        if obj.user:
            return obj.user.email
        else:
            return obj.contact.email

    def get_first_name(self,obj):
        if obj.user:
            return obj.user.first_name
        else:
            return obj.contact.first_name
    
    def get_last_name(self, obj):
        if obj.user:
            return obj.user.last_name
        else:
            return obj.contact.last_name

    def get_recipient(self,obj):
        if obj.recipient:
            return obj.recipient
        else:
            if obj.message_type == MessageTypes.email.value:
                return obj.contact.email
            elif obj.message_type == MessageTypes.phone.value:
                return obj.contact.phone

   

    class Meta:
        model = EmailMessage
        fields =('id','user','username','first_name','sms_error','gcm_error','email_error','senderid','recipient',
                 'last_name', 'email', 'message', 'subject', 'message_type', 'cc', 'delivery_report', 'date_sent', 'origin', 'sms_delivery_report', 'gcm_delivery_report',)


class MessageGroupSerializer(serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()

    def get_group(self,obj):
        return obj.id
    def get_creator_name(self,obj):
        if obj.creator:
            return obj.creator.username
        else:
            return None
    class Meta:
        model = MessageGroup
        fields =('name','creator','creator_name','id','group')


class MessagePolicyDaySerializer(serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField()
    def get_creator_name(self,obj):
        if obj.creator:
            return obj.creator.username
        else:
            return None
    class Meta:
        model = MessagePolicyDays
        fields =('days_passed','creator','creator_name','id',)
    

class SenderIdSerializer(serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField()

    def get_creator_name(self, obj):
        if obj.creator:
            return obj.creator.username
        else:
            return None
    class Meta:
        model = SenderId
        fields = ('id','name','creator','creator_name','id')


class MessageTemplateSerializer(serializers.ModelSerializer):
    is_message_policy = serializers.BooleanField()
    class Meta:
        model= MessageTemplates
        fields = ('id', 'typ', 'subject', 'message',
                  'is_message_policy', 'message_type', 'days_passed_from_borrow_date',)


class MessageTypesView(APIView):
    def get(self,request):
        data=[]
        for x in MessageTemplateEnum:
            data.append({"name":x.value})

        return Response(data=data)


class GroupContactSerializer(serializers.ModelSerializer):
    group_name = serializers.SerializerMethodField()
  
    def get_group_name(self,obj):
        if obj.group:
            return obj.group.name
        return None
    class Meta:
        model = Contact
        fields =('id','first_name','last_name','other_name','email','phone','group','user','group_name')

