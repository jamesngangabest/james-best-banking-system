from rest_framework import serializers

from bridge.models.crmSettings import CrmSettings

class CRMSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrmSettings
        fields = '__all__'
