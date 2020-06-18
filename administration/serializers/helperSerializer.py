
from rest_framework import serializers
from rest_framework.serializers import CharField, MultipleChoiceField, ValidationError, TimeField, DateTimeField, IntegerField, FileField


class DateTimeFieldWihTZ(serializers.DateTimeField):
    '''Class to make output of a DateTime Field timezone aware
    '''

    def to_representation(self, value):
        value = timezone.localtime(value)
        return super(DateTimeFieldWihTZ, self).to_representation(value)


