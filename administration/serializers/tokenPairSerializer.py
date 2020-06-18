from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from administration.models.administration import  SystemRole
from administration.models.authorization import *
from administration.models.resourceEnums import ResourceType
from django.contrib.auth.models import User
from administration.models.commonEnums import *
from administration.models.authorization import UserSecurityQuestions
from django.http import Http404

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(CustomTokenObtainPairSerializer,cls).get_token(user)
        token['username'] = user.username
        #token['perms'] = "1|3;2|5;4|709;378|1000"

        #print("teken.....")

        if user: #check if user object exists
            #if user.userRole is None:
            #    raise Http404
            if user.is_superuser and user.userRole is None:
                role = SystemRole.objects.get(is_default = True)
                user.userRole = role
                user.systemCompany =role.company
                user.save()
            else:
                pass
        else:
            raise  Http404

        #get permissions
        perms = RolePermission.objects.filter(role=user.userRole).exclude(resource__resource__resource__resource_type=ResourceType.CONTAINER.value)
        #print("Perms Count: ", len(perms))
        # for item in perms:
        #     print("Resource: ", item.resource.resource.resource.resource, " permissions: ", item.permissions)

        pstr = ";".join((str(item.resource.resource.resource.resource) + "|" + str(item.permissions)) for item in perms)
        token['perms'] = pstr

        token['first_name']=str(user.first_name)
        token['last_name']= str(user.last_name)

        token["role_id"] = str(user.userRole.id)
        token['company_id']=str(user.systemCompany.id)
        token['user']=str(user.id)
        token["role_name"] = user.userRole.name
        token['password_reset']=user.password_reset
        user_secs_qs = UserSecurityQuestions.objects.filter(user=user)
      
        if user_secs_qs.count() >= SettingsEnum.no_of_security_question.value:
            token['should_secure'] = False
        else:
            if user.userRole.is_default:  # administrator

                token['should_secure'] = False
            else:
                token['should_secure'] = True

       
        #print("perm string: ", pstr)
        return token
