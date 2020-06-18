from rest_framework import serializers
from rest_framework.serializers import CharField,MultipleChoiceField,ValidationError,TimeField,DateTimeField,IntegerField,FileField

from administration.models.models import *
from administration.models.administration import SystemRole, SystemCompany
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
import dateutil.parser
from django.utils.dateparse import parse_datetime

User=get_user_model()
from django.conf import settings
SUPPORT_MAIL = settings.SUPPORT_MAIL

from bridge.helpers import *
val = CleanValidation()
oh = OpalHelper()
msg = MyMessaging()
class GroupAvailableSerializer(serializers.ModelSerializer):
    class Meta:
        model=Group
        fields=('name','id',)

class ProfileDetailSerializer(serializers.Serializer):
    dob = serializers.DateField(format="%Y-%m-%d", input_formats=['%Y-%m-%dT%H:%M:%S.000Z',])
    gender = serializers.CharField()
    other_name = serializers.CharField()
    id_number = serializers.CharField()

class UserDetailsSerializer(serializers.Serializer):
    username = serializers.CharField()
    id = serializers.CharField()    
class UserGroupSerializer(serializers.ModelSerializer):
    groups= GroupAvailableSerializer(many=True)
    class Meta:
        model = User
        fields =('id','groups','username')

class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format="%Y-%m-%d", input_formats=['%Y-%m-%dT%H:%M:%S.000Z',], read_only=True)
    last_login = serializers.DateTimeField(format="%Y-%m-%d", input_formats=['%Y-%m-%dT%H:%M:%S.000Z',], read_only=True)
    dob = serializers.DateTimeField()


    role_name = serializers.SerializerMethodField(read_only=True)
    company_name = serializers.SerializerMethodField(read_only=True)
    #userRole = serializers.CharField(read_only=True)
    #systemCompany = serializers.CharField(read_only=True)
    def get_role_name(self, obj):
        try:
            user_role = SystemRole.objects.get(id=obj.userRole.id)
            return user_role.name
        except:
            return None
    def get_company_name(self,obj):

       
        try:
            company = SystemCompany.objects.get(id=obj.systemCompany.id)
            return company.name
        except:
            return None

    
    class Meta:
        model=User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password_reset', 'skip_crb_report', 'id_picture', 'profile_picture',
       'last_login','is_active','date_joined','loan_limit','county','school','sub_county','tsc_number',
        'userRole','systemCompany','role_name','company_name','gender','dob','id_number','other_name')
    
        # def validate(self, data):
        #     print(data)

        def validate_email(self,value):
            """check that the email is unique"""
            print ("Candidate")
           

            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError('That email exists for another account')
            return value

        def validate_username(self,value):
            """check that the phone/username is unique"""
            ##if administrator is create username ignore format_phone serializers
            value=val.format_phone(value)
            print (self.context.get('request').method) 
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError('That phone exists for another account')

            return value

        def validate_id_number(self,value):
            """check that the id number is unique"""
            ##if administrator is create username ignore format_phone serializers
           
            if User.objects.filter(id_number=value).exists():
                raise serializers.ValidationError('That id number exists for another account')

            return value
        def validate_dob(self,dob):
            print ("validate dob", dob)
            if dob:
                return  datetime.datetime.strptime(
                    dob, '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%Y-%m-%d")

            else:
                return None

        def validate_dod(self, value):
            print("validate dob", value)
            if value:
                return datetime.datetime.strptime(
                    value, '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%Y-%m-%d")
            else:
                return None


        # def create(self, validated_data):
        #     user = super(UserSerializer, self).create(validated_data)
        #     user.set_password(validated_data['password'])
        #     user.save()



        #     return user



class CompaniesSerializer(serializers.ModelSerializer):
    user = UserDetailsSerializer(read_only=True)
    class Meta:
        model=Companies
        fields=('id','email','company_name','location','phone','user')

    def validate_email(self,value):
        """check that the email is unique"""
 
        # if Companies.objects.filter(email=value).exists():
        #     raise serializers.ValidationError('That email exists for another account')
        return value
    def validate_user(self,value):
        return value

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model=GroupRoles
        fields = "__all__"

class SystemResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model=SystemResources
        fields=('id','name')

class SystemPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Permission
        fields=("__all__")


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("profile_picture","id_picture",)

class ProfileSerializer(serializers.ModelSerializer):
    user=UserSerializer(required=False)
    dob = serializers.CharField()
    class Meta:
        model=Profile
        fields=("user","other_name","id_number","gender","dob")

    def validate_dob(self,value):
        print ("Validate ")
        
        return parse_datetime(value).date()
    def validate_user(self,value):
        print ("validate user my guy")
        print (value)
        return value
    
        #check the format

class FrontEndUserSerializer(serializers.ModelSerializer):
    username= serializers.CharField()
    # groups= GroupAvailableSerializer()
    class Meta:
        model=User
        fields=('id','username','email','first_name','last_name')
        def validate_email(self,value):
            """check that the email is unique"""
            print ("email")

            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError('That email exists for another account')
            return value

        def validate_username(self,value):
            """check that the phone/username is unique"""
            ##if administrator is create username ignore format_phone serializers
            value=val.format_phone(value)
            print ("validate username")
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError('That phone exists for another account')

            return value



        def create(self, validated_data):
            password=oh.randChar(5)
            print (password)
            user = super(UserSerializer, self).create(validated_data)
            user.set_password(password)
            user.save()

            tpl=msg.getEmailTemplates("REGISTRATION")
            #email this pasword
            message = tpl.message
            msg.sendEmailMessage(user_data['email'],SUPPORT_MAIL,tpl.subject,message.replace("#",password),user)

            #
class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields=("user","code","county","school",)

class PasswordRecoverSerializer(serializers.Serializer):
    username = serializers.CharField(label="username")
class PasswordChangeSerializer(serializers.Serializer):
    password = serializers.CharField(label="password")
