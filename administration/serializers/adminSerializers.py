from rest_framework import serializers
from administration.models.administration import *
from bridge.models.models import ErrorLoggerModel
from administration.models.authorization import *
from administration.models.companySetting import *
from administration.helpers.rolePermissionHelper import RolePermissionHelper
from administration.helpers.dateHelper import DateHelper
from django.core.validators import ValidationError
from bridge.errors import AppValidation
from administration.models.models import Counties, Subcounty,Schools,Teachers

class CompanyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyType
        fields = ('id', 'name',)

class GlobalResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalResource
        fields = "__all__"

class RolePermissionField(serializers.RelatedField):
    def to_representation(self, value):
        data = {
            "id": value.id,
            "name": value.resource.name,
            "permissions": value.permissions
        }
        return data

class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = ("id","role","resource","permissions")
        depth = 1

class SystemRoleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemRole
        fields = ("id", "name", "description",'company',)

    # def get_unique_together_validators(self):
    #     '''
    #     Overriding method to disable unique together checks
    #     '''
    #     return []

class SystemRolePermissionSerializer(serializers.ModelSerializer):
    resourceSections = serializers.SerializerMethodField()
    class Meta:
        model = SystemRole
        fields = ("id", "name", "description",'company','resourceSections',)

    def get_resourceSections(self, obj):
        perms = RolePermissionHelper.get_role_permissions(obj.id)
        return perms

class SystemRoleListSerializer(serializers.ModelSerializer):
    #name1 = serializers.CharField(max_length=128)
    class Meta:
        model = SystemRole
        fields = ("id", "name", "description",'company',)

class SystemCompanySerializer(serializers.ModelSerializer):
    company_type = CompanyTypeSerializer()
    class Meta:
        model = SystemCompany
        fields = ("id","name","domain",'description',"company_type")

class SystemCompanyDetailSerializer(serializers.ModelSerializer):
    #company_type = CompanyTypeSerializer()
    class Meta:
        model = SystemCompany
        fields = "__all__"

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','userRole')


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ('id', 'name','code',)


class BranchSerializer(serializers.ModelSerializer):
    bank_name=serializers.SerializerMethodField()
    effective_date = serializers.DateTimeField( read_only=True)
    closed_date = serializers.DateTimeField(read_only=True)

    def get_bank_name(self,obj):
        if obj.bank:
            return obj.bank.name
        else:
            return None


    class Meta:
        model = Branch
        fields = ('id', 'branch_name', 'bank','bank_name','branch_code','effective_date','closed_date','is_open',)


class SubcountySerializer(serializers.ModelSerializer):
    county = serializers.CharField(read_only=True)
    county_name=serializers.SerializerMethodField()

    def get_county_name(self,obj):
        return obj.county.name

    class Meta:
        model= Subcounty
        fields =('id','name','county','county_name')


class BankDetailSerializer(serializers.ModelSerializer):
    branch_name = serializers.SerializerMethodField()
    bank_name = serializers.SerializerMethodField()
    bank = serializers.SerializerMethodField()
    def get_bank(self,obj):
        if obj.branch:
            if obj.branch.bank:
            	return obj.branch.bank.id
            else:
                return None
        else:
            return None

    def get_bank_name(self,obj):
        if obj.branch:
            if obj.branch.bank:
            	return obj.branch.bank.name
            else:
                return None
        else:
            return None

    def get_branch_name(self,obj):
        if obj.branch:
            return obj.branch.branch_name
        else:
            return None
    class Meta:
        model = BankDetail
        fields = ('id', 'branch_name','branch','account_number','account_name','verified','bank_name','bank')

class NextOfKinSerializer(serializers.ModelSerializer):
    class Meta:
        model = NextOfKin
        fields = ('id', 'full_name','email','phone_no','id_number','user')


class CountiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Counties
        fields = ('id', 'name','county_code')
class TeacherUserSerializer(serializers.ModelSerializer):
    dob = serializers.DateTimeField(read_only=True)
    county_id = serializers.SerializerMethodField(read_only=True)
    sub_county =  serializers.SerializerMethodField(read_only=True)
    school = serializers.SerializerMethodField(read_only=True)
    def get_county_id(self,obj):
        try:
            return Counties.objects.get(name__iexact=obj.county.replace("-"," ")).id
        except:
            return obj.county

    def get_sub_county(self,obj):
        try:
            return Subcounty.objects.get(name__iexact=obj.sub_county.replace("-", " ")).id
        except:
            return obj.sub_county
    def get_school(self,obj):
        try:
            return Schools.objects.get(name__iexact=obj.school.replace("-", " ")).id
        except:
            return obj.school
    
    
    class Meta:
        model = Teachers
        fields = ('id','tsc_number','id_number','names','dob','phone','school','county','county_id','sub_county','station_code')

class SchoolsSerializer(serializers.ModelSerializer):
    county = serializers.SerializerMethodField()
    county_id = serializers.SerializerMethodField()
    county_code = serializers.SerializerMethodField()
    sub_county_name = serializers.SerializerMethodField()

    def get_sub_county_name(self,obj):
        if obj.sub_county:
            return obj.sub_county.name
    def get_county_code(self,obj):
        if obj.sub_county:
            return obj.sub_county.county.county_code

    def get_county(self, obj):
        if obj.sub_county:

            return obj.sub_county.county.name

    def get_county_id(self, obj):
        if obj.sub_county:
            return obj.sub_county.county.id

    class Meta:
        model = Schools
        fields = ('id', 'name', 'address', 'phone_no', 'county', 'county_id','station_code','county_code','sub_county','sub_county_name')


class CompanySettingSerializer(serializers.ModelSerializer):
    time_stamp = serializers.SerializerMethodField()

    def get_time_stamp(self, obj):
       return DateHelper.to_string(obj.time_stamp)
    class Meta:
        model = CompanySetting
        fields = "__all__"

    # def validate(self,data):
    #     return data

    # def update(self, instance, validated_data):
    #     if self.initial_data["time_stamp"] != DateHelper.to_string(instance.time_stamp):
    #         # raise serializers.ValidationError("Item has been updated by another user")
    #         raise AppValidation("Item has been updated by another user",status_code=400)

    #     instance.save()
        
    #     return instance


class AdminErrorLogSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    def get_username(self,obj):
        return obj.user.username
    class Meta:
        model = ErrorLoggerModel
        fields = ('id', 'subject', 'responseDump', 'message', 'errorType', 'user', 'date_logged','username'
                  )
