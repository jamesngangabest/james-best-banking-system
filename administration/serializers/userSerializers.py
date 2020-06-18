
from rest_framework import serializers
from administration.models.administration import Bank,BankDetail,NextOfKin
#update profile account
from django.contrib.auth import get_user_model
User = get_user_model()
#bank details
class UserImage(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','profile_picture', 'id_picture',)

class BankDetailSerializer(serializers.ModelSerializer):
    bank= serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()
    def get_branch_name(self,obj):
        if obj.branch:
            return obj.branch.branch_name
        else:
            return None

    def get_bank(self,obj):
        if obj.branch:
            if obj.branch.bank:
                return obj.branch.bank.name
            else:
                return None
        else:
            return None

    class Meta:
        model = BankDetail
        fields = ('id','bank','branch_name','account_name','account_number','verified')

class NextOfKinSerializer(serializers.ModelSerializer):
    class Meta:
        model = NextOfKin
        fields = ('id_number','user','full_name','email','phone_no','profile_picture')


class UserHelperSerializer(serializers.Serializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    def get_first_name(self, obj):
        if hasattr(obj,'user'):
            
            return obj.user.first_name
        elif hasattr(obj, 'loan'):
            return obj.loan.user.first_name
        elif hasattr(obj, 'loan_installment'):
            return obj.loan_installment.loan.user.first_name

    def get_last_name(self, obj):
        if hasattr(obj, 'user'):
            return obj.user.last_name
        elif hasattr(obj, 'loan'):
            return obj.loan.user.last_name
        elif hasattr(obj, 'loan_installment'):
            return obj.loan_installment.loan.user.last_name
        
    def get_username(self,obj):
        if hasattr(obj, 'user'):
            return obj.user.username
        elif hasattr(obj, 'loan'):
            return obj.loan.user.username
        elif hasattr(obj, 'loan_installment'):
            return obj.loan_installment.loan.user.username
            
    def get_email(self, obj):
        if hasattr(obj, 'user'):
            return obj.user.email
        elif hasattr(obj, 'loan'):
            return obj.loan.user.email
        elif hasattr(obj, 'loan_installment'):
            return obj.loan_installment.loan.user.email


