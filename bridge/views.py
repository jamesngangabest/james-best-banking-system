from django.shortcuts import render
from  .bridgeSerializer import *
from .models import *
from administration.permissionsMod import *

from rest_framework import status
from rest_framework import mixins
from rest_framework import generics


# Create your views here.

class MobilePrefixCollections(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, AdminAuthenticationPermission,)
    queryset=MobilePrefix.objects.all()
    serializer_class=MobilePrefixSerializer


class MobilePrefixSingleCollection(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, AdminAuthenticationPermission,)
    lookup_field='id'
    queryset=MobilePrefix.objects.all()
    serializer_class=MobilePrefixSerializer
