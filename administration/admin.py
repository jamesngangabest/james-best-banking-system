from django.contrib import admin

# Register your models here.
from administration.models.models import *
from administration.models.administration import *

from administration.models.authorization import *
from administration.models.APIKeys import MPESAPIKeys,MPESAPIType,PaybillNumber
admin.site.register(Profile)
admin.site.register(User)
admin.site.register(SourceOfIncome)
admin.site.register(Companies)
admin.site.register(Counties)
admin.site.register(Schools)
admin.site.register(CompanyType)
admin.site.register(Branch)
admin.site.register(SystemCompany)
admin.site.register(SystemRole)
# admin.site.register(APITransunionKeys)
admin.site.register(MPESAPIKeys)
admin.site.register(MPESAPIType)
admin.site.register(PaybillNumber)
admin.site.register(Teachers)
admin.site.register(GlobalResource)

admin.site.register(CompanyTypeResource)
admin.site.register(SecurityQuestions)
admin.site.register(UserSecurityQuestions)


admin.site.register(CompanyResource)
admin.site.register(Bank)

admin.site.register(NextOfKin)
admin.site.register(BankDetail)

admin.site.register(RolePermission)
