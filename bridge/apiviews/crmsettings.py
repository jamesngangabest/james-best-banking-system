from administration.models.resourceEnums import CompanyTypes, Perm, Resource
from administration.permissionsMod import HasAccessPermissions, AuthHelper
from functools import partial
from rest_framework.response import Response
from rest_framework import generics, status

from bridge.serializers.crmSettings import CRMSettingSerializer,CrmSettings
from bridge.models.crmSettings import CrmSettings
from bridge.errors import AppValidation
from django.db import transaction
from rest_framework.permissions import IsAuthenticated, AllowAny
from administration.helpers import DateHelper


class CrmSettingView(generics.RetrieveUpdateAPIView):
    serializer_class = CRMSettingSerializer
    lookup_field = "id"
    perms = {Resource.CRM_SETTINGS.value: Perm.READ.value | Perm.UPDATE.value}
    permission_classes = (IsAuthenticated, partial(
        HasAccessPermissions, perms),)

    @transaction.atomic
    def put(self, request, id):

        # item = SaccoSettings.objects.get(id=id)
        # if request.data["time_stamp"] != DateHelper.to_string(item.time_stamp):
        #     raise AppValidation(
        #         "Item has been updated by another user", status_code=400)

        return self.update(request, id)

    def get_object(self):
        try:
            item = CrmSettings.objects.get(
                company=self.request.user.systemCompany)
        except CrmSettings.DoesNotExist:
            item = CrmSettings.objects.create(
                company=self.request.user.systemCompany)

        return item
