from rest_framework.response import Response
from rest_framework import generics, status
from bridge.errors import AppValidation
from bridge.models.models import EmailMessage
from rest_framework.views import APIView
from bridge.contrib.messaging import *
import datetime
import threading

from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from administration.models.resourceEnums import CompanyTypes, Perm, Resource
from administration.permissionsMod import HasAccessPermissions, AuthHelper
from functools import partial

from django.db.models import Q
from bridge.models.commonEnums import *
from bridge.serializers.message import *
from bridge.helpers import MyMessaging
from bridge.models.messages import *
from bridge.models.commonEnums import *
from django.contrib.auth import get_user_model
User = get_user_model()


class MessagesViews(generics.ListAPIView):
    serializer_class = MessageSerializer
    filter_backends = (SearchFilter, OrderingFilter)

    search_fields = ('cc', 'user__username', 'user__email',
                     'user__first_name', 'user__last_name', 'message', 'subject')
    ordering_fields = ('cc', 'user__username', 'user__email',
                       'user__first_name', 'user__last_name', 'message', 'subject')

    def get_queryset(self):
        return EmailMessage.objects.filter(Q(user__systemCompany=self.request.user.systemCompany) | Q(company=self.request.user.systemCompany)).order_by('-date_sent')


class MessageView(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    serializer_class = MessageSerializer
    queryset = EmailMessage.objects.all()
    lookup_field = "id"

    def perform_create(self, serializers):
        #hehe send message bro..watch mambo
        data = self.request.data
        msg = MyMessaging()
        # try:
        user = User.objects.get(id=data['user'])
        company = self.request.user.systemCompany
        data = self.request.data
        id = serializers.save(
            user=user, company=self.request.user.systemCompany,)
        store_id=None
        for x in data['channel_type']:
            if x == "email":
                store_id = msg.sendEmail({"to": user.email,
                                            "origin": company.support_email,
                                            "subject": data['subject'],
                                            "message": self.request.data['message'],
                                            "user": user,
                                            "id": id,
                                            
                                            })


            if x == "sms":
                msg.sendSMS({"to": user.username,
                                    "origin": company.phone,
                                    "message": self.request.data['message'],
                                    "user": user,
                                    "id": id,
                                    "senderid":data['senderid']
                                
                                    })
            if x == "gcm":
                if user.fcm_id:
                    msg.gcm({"token": user.fcm_id,
                                "message": self.request.data['message'],
                                "subject": self.request.data['subject'],
                                "user": user
                                })

                else:
                    raise AppValidation("The FCM token does not exist.Message Notification cannot be sent",status_code=400)


    def perform_update(self, serializers):
        msg = MyMessaging()
        data = self.request.data
        # try:
        user=None
        email=None
        company = self.request.user.systemCompany
        data = self.request.data
        id=serializers.save()



        store_id = None
        for x in data['channel_type']:
            if x == "email":
                if id.user:
                    email = id.user.email
                else:
                    raise AppValidation(
                        "Email not available.Please compose a new email or send as sms",status_code=400)

                store_id = msg.sendEmail({"to":email,
                                            "origin": company.support_email,
                                            "subject": data['subject'],
                                            "message": self.request.data['message'],
                                            "user": user,
                                            "id": id,
                                            
                                            })


            if x == "sms":
                recipient=None
                if "@" in id.recipient:
                    if id.user:
                        recipient =id.user.username
                    else:
                        raise AppValidation("Phone number not available",status_code=400)
                else: 
                    recipient=id.recipient


                msg.sendSMS({"to": recipient,
                                    "origin": company.phone,
                                    "message": self.request.data['message'],
                                    "user": user,
                                    "id": id,
                                    "senderid":data['senderid']
                                
                                    })
            if x == "gcm":
                if user:
                    msg.gcm({"token": user.fcm_id,
                                "message": self.request.data['message'],
                                "subject": self.request.data['subject'],
                                "user": user
                                })

                else:
                    raise AppValidation("The FCM token does not exist.Message Notification cannot be sent.Please send a new gcm message",status_code=400)

class SendGroupMessage(APIView):
   
        
    def post(self,request):
        data=request.data
        data['company']=self.request.user.systemCompany
        MessageHandler.groupMessage(data)
        # lp = threading.Thread(target=MessageHandler.groupMessage(), args=(data,))
        # lp.daemon = True
        # lp.start()
        return Response({})


class MessageGroupViews(generics.ListAPIView):
    serializer_class = MessageGroupSerializer
    filter_backends = (SearchFilter, OrderingFilter)

    search_fields = ('name','creator')
    ordering_fields = ('name', 'creator')

    def get_queryset(self):
        return MessageGroup.objects.filter(company=self.request.user.systemCompany)


class MessageGroupView(generics.RetrieveUpdateDestroyAPIView,generics.CreateAPIView):
    serializer_class = MessageGroupSerializer
    queryset = MessageGroup.objects.all()
    lookup_field = "id"


    def perform_create(self,serializers):
        serializers.save(creator=self.request.user,company=self.request.user.systemCompany)



class SenderIdViews(generics.ListAPIView):
    serializer_class = SenderIdSerializer
    filter_backends = (SearchFilter, OrderingFilter)

    search_fields = ('name',)
    ordering_fields = ('name',)

    def get_queryset(self):
        return SenderId.objects.filter(company=self.request.user.systemCompany)


class SenderIdView(generics.RetrieveUpdateDestroyAPIView,generics.CreateAPIView):
    serializer_class = SenderIdSerializer
    queryset = SenderId.objects.all()
    lookup_field = "id"

    def perform_create(self, serializers):
        serializers.save(company=self.request.user.systemCompany,creator=self.request.user)


class MessageTemplatesViews(generics.ListAPIView):
    serializer_class = MessageSerializer
    filter_backends = (SearchFilter, OrderingFilter)

    search_fields = ('typ', 'days_passed_from_borrow_date',
                     'message', 'subject')
    ordering_fields = ('typ', 'days_passed_from_borrow_date',
                       'message', 'subject')

    serializer_class = MessageTemplateSerializer
    
    def get_queryset(self):
        return MessageTemplates.objects.filter(company=self.request.user.systemCompany)

    def list(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)
        action_perms = {
            "canRead": AuthHelper.has_access(request, {Resource.MESSAGE_TEMPLATES.value: Perm.READ.value}),
            "canCancel": AuthHelper.has_access(request, {Resource.MESSAGE_TEMPLATES.value: Perm.CANCEL.value}),
                    }
        response.data["perms"] = action_perms
        return response

class MessageTemplateView(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    perms = {Resource.MESSAGE_TEMPLATES.value: Perm.READ.value | Perm.CREATE.value |
             Perm.UPDATE.value | Perm.CANCEL.value}
    permission_classes = (IsAuthenticated, partial(
        HasAccessPermissions, perms),)
    serializer_class = MessageTemplateSerializer
    queryset = MessageTemplates.objects.all()
    lookup_field = "id"

    def perform_create(self, serializers):
        serializers.save(company=self.request.user.systemCompany,
                         )

class GroupContactViews(generics.ListAPIView):
    filter_backends = (SearchFilter, OrderingFilter)

    search_fields = ('first_name', 'last_name','other_name', 'email', 'phone', 'group__name',)
    ordering_fields = ('first_name', 'last_name', 'other_name', 'email', 'phone', 'group__name')

    perms = {Resource.GROUPS.value: Perm.READ.value | Perm.CREATE.value |
             Perm.UPDATE.value | Perm.CANCEL.value}
    permission_classes = (IsAuthenticated, partial(
        HasAccessPermissions, perms),)
    serializer_class = GroupContactSerializer
    
    def get_queryset(self):
        return Contact.objects.filter(group=self.kwargs['group'])



class GroupContactView(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    perms = {Resource.GROUPS.value: Perm.READ.value | Perm.CREATE.value |
             Perm.UPDATE.value | Perm.CANCEL.value}
    permission_classes = (IsAuthenticated, partial(
        HasAccessPermissions, perms),)
    serializer_class = GroupContactSerializer
    queryset = Contact.objects.all()
    lookup_field = "id"

    def perform_create(self, serializers):
        data = self.request.data
        c = Contact.objects.filter(phone=data['phone'], group=data['group'])
        if not c.exists():
            serializers.save(company=self.request.user.systemCompany,
                            group=MessageGroup.objects.get(id=data['group'])
                            )
        else:
            raise AppValidation("Contact already exists",status_code=400)

    def perform_update(self,serializers):
        serializers.save()

class GroupContactUploadView(APIView):

    def uploader(self,file_data,data):
        lines = file_data.split("\n")
        existing = []
        
        for index, line in enumerate(lines, start=1):
            print("ndani", line)
            if index == 1:
                continue
            fields = line.split(",")

            # if not fields[0]:  # first cell has nothing...lets skipp
            #     existing.append(fields)
            #     continue
            
            try:
                first_name=fields[0]
                last_name=fields[1]
                other_name = fields[2]
                try:
                    phone = PhoneNumber.from_string(
                        phone_number=str(fields[3]), region='KE').as_e164
                except:
                    ErrorLogger("INCORRECT PHONE NUMBER","the phone format was not parsed correctly",fields,self.request.user)
                    continue
                email = fields[4]
            except Exception:
               continue


            c=Contact.objects.filter(phone=phone,group=data['group'])
            if not c.exists():
                
                Contact.objects.create(first_name=first_name,last_name=last_name,other_name=other_name,phone=phone,email=email,
                                       company=self.request.user.systemCompany,
                                       group=MessageGroup.objects.get(
                                           id=data['group'])
                )
            else:
                continue

    def post(self,request):
        data=self.request.data
        group = data['group']
        try:
            file_obj = request.FILES['csv_file']
        except:
            raise AppValidation("Empty file is unacceptable",status_code=0)
        if not file_obj.name.endswith('.csv'):
                raise AppValidation(
                    "Unacceptable file format.Please upload a csv file", "File Format", status_code=400)
        if file_obj.multiple_chunks():
            raise AppValidation(
                "Uploaded file is too big " + str(file_obj.size/(1000*1000))+" Mb", "File size", status_code=400)
        print(":walal")
        file_data = file_obj.read().decode("utf-8")
        lp = threading.Thread(target=self.uploader, args=(file_data, data))
        lp.daemon = True
        lp.start()
        return Response({})


class MessagePolicyDaysViews(generics.ListAPIView):
    filter_backends = (SearchFilter, OrderingFilter)

    search_fields = ('days_passed',)
    ordering_fields = ('days_passed',)

    perms = {Resource.MESSAGE_POLICY_DAYS.value: Perm.READ.value | Perm.CREATE.value |
            Perm.UPDATE.value | Perm.CANCEL.value}
    permission_classes = (IsAuthenticated, partial(
        HasAccessPermissions, perms),)
    serializer_class = MessagePolicyDaySerializer

    def get_queryset(self):
            return MessagePolicyDays.objects.filter(company=self.request.user.systemCompany)


class MessagePolicyDetailView(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    perms = {Resource.MESSAGE_POLICY_DAYS.value: Perm.READ.value | Perm.CREATE.value |
             Perm.UPDATE.value | Perm.CANCEL.value}
    permission_classes = (IsAuthenticated, partial(
        HasAccessPermissions, perms),)
    serializer_class = MessagePolicyDaySerializer
    queryset = MessagePolicyDays.objects.all()
    lookup_field = "id"

    def perform_create(self, serializers):
        data = self.request.data
        c = MessagePolicyDays.objects.filter(
            company=self.request.user.systemCompany,days_passed=serializers.validated_data['days_passed'])
        if not c.exists():
            serializers.save(company=self.request.user.systemCompany,
                             creator=self.request.user
                             )
        else:
            raise AppValidation("Day already exists", status_code=400)


