from rest_framework.parsers import FileUploadParser
from django.shortcuts import render
from .administrationSerializers import *
from .permissionsMod import *
import threading
from administration.models.models import *
from administration.models.administration import BankDetail,NextOfKin
from administration.serializers.userSerializers import BankDetailSerializer,NextOfKinSerializer
from administration.serializers.adminSerializers import CountiesSerializer, SchoolsSerializer,TeacherUserSerializer
from django.contrib.auth import get_user_model
User = get_user_model()
from bridge.helpers import OpalHelper,MyMessaging
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import update_last_login
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter
from bridge.models.commonEnums import MessageTemplateEnum

from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework_jwt.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import *
from rest_framework.views import APIView
from administration.permissionsMod import HasAccessPermissions, AuthHelper
from administration.models.resourceEnums import CompanyTypes, Perm, Resource

from administration.helpers.tokenHelper import TokenHelper
from functools import partial

import logging
import datetime
import requests
from django.db.models import Q

logger = logging.getLogger(__name__)
hdlr = logging.FileHandler('django_dev.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.WARNING)
logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)

SUPPORT_MAIL = settings.SUPPORT_MAIL
URL =settings.URL
#initialize notifications class
ms=MyMessaging()
val = CleanValidation()
oh = OpalHelper()
#permissions
# Create your views here.
class CompaniesCollection(generics.ListCreateAPIView):
    permission_classes = (AdminAuthenticationPermission,) #only super administrator can post here
    queryset=Companies.objects.all()
    serializer_class=CompaniesSerializer
    def create(self,request, *args, **kwargs):
        print ("Create")
        serializer=CompaniesSerializer(data=request.data)
        if serializer.is_valid():
            user=User.objects.get(id=request.data['user'])
            print ("post")
            serializer.save(user=user)
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors)
class CompanySingle(generics.RetrieveUpdateDestroyAPIView):
    '''Super admin can delete update and  retrieve '''
    permission_classes = (IsAuthenticated, AdminAuthenticationPermission,)
    lookup_field='id'
    queryset=Companies.objects.all()
    serializer_class=CompaniesSerializer

    
    def put(self,request, *args, **kwargs):
        user=User.objects.get(username=request.data['username'])
        print (user)
        serializer=CompaniesSerializer(instance=user,data=request.data)
        if serializer.is_valid():
        
            serializer.save()
            Companies.objects.filter(id=request.data['id']).update(user=user,
                                    company_name=serializer.validated_data['company_name'],
                                    location=serializer.validated_data['location'],
                                    phone=serializer.validated_data['phone'],
                                    email=serializer.validated_data['email'],
                                        
                                    )
            serializer.data['user']={"id":user.id, "username":user.username}
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors)
    
    
        

class UsersCollectionView(generics.ListCreateAPIView):
    '''Create and list all users'''
    perms = {Resource.USERS.value: Perm.CREATE.value | Perm.UPDATE.value}
    #permission_classes = (IsAuthenticated, partial(HasAccessPermissions, perms),)
    permission_classes = (IsAuthenticated, AdminAuthenticationPermission, partial(HasAccessPermissions, perms),)
    queryset=User.objects.all().order_by('username')
    serializer_class= UserSerializer
    
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('username', 'email', 'first_name','last_name')
    ordering_fields = ("id",'username', 'email', 'first_name','last_name')
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)
        action_perms ={
            "canAdd": AuthHelper.has_access(request, {Resource.USERS.value: Perm.CREATE.value}),
            "canUpdate": AuthHelper.has_access(request, {Resource.USERS.value: Perm.UPDATE.value}),
            "canDelete": False # AuthHelper.has_access(request, {Resource.USERS.value: Perm.DELETE.value})
        }
        response.data["perms"] = action_perms
        return response
    #add role here
    def post(self, request, *args, **kwargs):
        username = request.data['username']

        return self.create(request, *args, **kwargs)
    def create(self, request, *args, **kwargs):
        print ("Create")
        #user serializer
        print (request.data)

        serializer=UserSerializer(data=request.data)
        # serializerProf=ProfileSerializer(data=request.data)
        try:
            serializer.is_valid()
            # serializerProf.is_valid()
                
            user=serializer.save()
            user.set_password(request.data['password'])
            user.save()
            #get group

           
            # serializerProf.save(user=user)
            # g=Group.objects.get(id=request.data['group_id'])
            # user.groups.add(g)

        except serializers.ValidationError:
            return Response({"status":"error","message":"Registration was Unsuccessful","data":[serializerProf.errors]},status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"status":"success","message":"Registration was successful","data":[serializerProf.data]},status=status.HTTP_201_CREATED)
       
    def put(self,request, *args, **kwargs):
        user=User.objects.get(username=request.data['username'])
        print (user)
        serializer=ProfileSerializer(user,data=request.data)
        if serializer.is_valid():
            user.first_name=request.data['first_name']
            user.last_name=request.data['last_name']
            user.email= request.data['email']
            user.save()

            
            # g=Group.objects.get(id=request.data['group_id'])
            # user.groups.add(g)

            serializer.save(user=user,)

            # serializer.data['user']={"id":user.id, "username":user.username}
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors)



class UserCollectionView(generics.RetrieveUpdateDestroyAPIView):
    '''Super admin can delete update and  retrieve'''
    permission_classes = (IsAuthenticated, AdminAuthenticationPermission,)
    queryset=User.objects.all()
    lookup_field='id'

    serializer_class= UserSerializer
    def setPassword(self,user,company):
        password = oh.randChar(5)
        user.set_password(password)
   # force user to reset password
        user.date_password_entered = datetime.datetime.now()
        user.save()


        msg =MyMessaging()
        # try:
        tpl = msg.getMessageTemplate(MessageTemplateEnum.REGISTER_ACCOUNT.value, company,"E")

        msg.initMessaging({"to":user.email,
                        "channels": "E",
                        "from":company.support_email,
                        "subject":tpl.subject,
                        "message":tpl.message.replace("#password", password),
                        "user":user
                        })

    def post(self,request):
   
        serializer=UserSerializer(data=request.data)
        if serializer.is_valid(): 
            c_id = TokenHelper.get_company_id(request)
            # serializer.save(systemCompany=SystemCompany.objects.get(id=request.data['systemCompany']),
            #                 userRole=SystemRole.objects.get(id=request.data['role_id'])
            #                 )
            user=serializer.save(systemCompany=request.user.systemCompany)
            self.setPassword(user, request.user.systemCompany)
            return Response({"user":serializer.data,"message":"A message has been sent to the members email account."})
        else:
            print("New user has some invalid data")
            return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def get(self,request,id):
        user = User.objects.get(id=id)
        user_serializer = UserSerializer(user)
        try:
            bank_detail = BankDetail.objects.get(user=id)
        except:
            bank_detail=None
        
        bank_detail_serializer=BankDetailSerializer(bank_detail)
        try:
            nextOfKin= NextOfKin.objects.get(user=id)
        except:
            nextOfKin=None

        nextOfKin_serializer = NextOfKinSerializer(nextOfKin)

        return Response({"user":user_serializer.data,
                        "bank":bank_detail_serializer.data,
                         "nextOfKin": nextOfKin_serializer.data
                        })

    def put(self,request,id):
        user = User.objects.get(id=id)
        
        serializer=UserSerializer(user,data=request.data)
        #print(request.data)
        #profile_serializer=ProfileSerializer(instance=user.OpalProfile,data=request.data)
        if serializer.is_valid(): #and profile_serializer.is_valid():
        
            serializer.save()
            # if not(request.data["role_id"] is None) and request.data["role_id"] !="":
            #     try:
            #         user_role = UserRole.objects.get(user_id=id)

            #     except UserRole.DoesNotExist:
            #         user_role = UserRole()
            #         user_role.user_id = id

            #     user_role.role_id = request.data["role_id"]
            #     user_role.save()

            #profile_serializer.save()
            print("user updated successfully")
            # serializer.data['user']={"id":user.id, "username":user.username}
            #return Response({"user":serializer.data,"profile":profile_serializer.data})
            return Response({"user":serializer.data})
        else:
            print("user has some invalid data")
            return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class UserImagesUploadView(APIView):
    parser_class = (FileUploadParser,)
    def post(self,request,id):
        print(request.data)
        user = User.objects.get(id=id)
        file_serializer = FileSerializer(data=request.data,instance=user)
        if file_serializer.is_valid():
            file_serializer.save(
                )
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UsersFileUploadView(APIView):
    def uploader(self,lines,data):
        existing = []
        for index, line in enumerate(lines, start=1):
            if index == 1:
                continue
            fields = line.split(",")
            if not fields[0]:  # first cell has nothing...lets skipp
                existing.append(fields)
                continue
            tsc_number = fields[1].strip()
            id_number = fields[2].strip()
            names= fields[3]
            dob = fields[4]
            county_name = fields[5]
            sub_county = fields[6]
            station_code = fields[7]
            station_name = fields[8]
            phone=fields[9]
         
            print(line)
            self.createTeacherUser(id_number,tsc_number,county_name,sub_county,station_code,station_name,self.getDOB(dob),phone,names, data)

    def post(self,request):
        data = request.data
        print(request.FILES)
        company = data['company']
        
        lines =FileUploadHelper(request.FILES['csv_file']).getfile()
        lp = threading.Thread(target=self.uploader, args=(lines, data))
        lp.daemon = True
        lp.start()
        return Response({})
    def createTeacherUser(self,id_number,tsc_number,county_name,sub_county,station_code,station_name,dob,phone,names,data):
        t=Teachers.objects.filter(id_number=id_number, tsc_number=tsc_number,company=data['company'])
        if t.exists():
            return t[0]
        else:
            company=SystemCompany.objects.get(id=data['company'])
           
            Teachers.objects.get_or_create(id_number=id_number, tsc_number=tsc_number,defaults={"tsc_number":tsc_number,
                                            "id_number":id_number,"county":county_name,"dob":dob,"company":company,
                                            "sub_county":sub_county,"school": station_name,"station_code":station_code,
                                            "names":names,"phone":phone
                                            })
    def getDOB(self,dob):    
        print(dob)    
        return datetime.datetime.strptime(dob,"%Y%m%d").strftime("%Y-%m-%d")

    def getStation(self,station_code,station_name,sub_county,county_name,id_number):
        sc=Schools.objects.filter(station_code__iexact=station_code,name__iexact=station_name,sub_county__county__company=self.request.user.systemCompany)
        if sc.exists():
            return sc[0]
        else:
            sub_county= self.get_sub_county(sub_county,county_name,station_name,station_code,id_number)
       
            s, created = Schools.objects.get_or_create(
                station_code=station_code, name=station_name,defaults={"station_code":station_code,"name":station_name,
                "sub_county":sub_county
                })
            if s:
                return s
            else:
                return created
   

    def get_sub_county(self,sub_county,county,station,station_code,id_number):
        c=Subcounty.objects.filter(name__iexact=sub_county,county__name__iexact=county,county__company=self.request.user.systemCompany)
        if c.exists():
            return c[0]
        else:
            ErrorLogger("USERS DATABASE UPLOAD","System could not find a subcounty for "+station_code+" "+station+",and teacher"+id_number+"hence return none",None,self.request.user)
            return None


class TeachersCollectionView(generics.ListAPIView):
    serializer_class = TeacherUserSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('id_number', 'tsc_number', 'county', 'school','station_code','sub_county')
    ordering_fields = ('id_number', 'tsc_number', 'county',
                       'school', 'station_code', 'sub_county')

    def get_queryset(self):
        return Teachers.objects.filter(company=self.kwargs['company'])

class TeacherCollectionView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TeacherUserSerializer
    queryset = Teachers.objects.all()
    lookup_field = 'id'
    def getcounty(self):
        try:
            return Counties.objects.get(id=self.request.data['county_id'])
        except:
            raise AppValidation(
                'county does not exist', status_code=400)

    def getsubcounty(self):
        try:
            return Subcounty.objects.get(id=self.request.data['sub_county'], county=self.request.data['county_id'])
        except:
            raise AppValidation('Subcounty does not exist in specified county',status_code = 400)

    
    def getschool(self):
        try:
            return Schools.objects.get(id=self.request.data['school'], sub_county=self.request.data['sub_county'])
        except:
            raise AppValidation('School does not exist in specified county', status_code=400)

    def perform_update(self,serializer):
        county = self.getcounty()
        sub_county = self.getsubcounty()
        school = self.getschool()

        serializer.save(county=county.name,
                        sub_county= sub_county.name,
                        school = school.name
                        )

    



class Usearsearch(generics.ListAPIView):
    serializer_class = UserSerializer
    def get_queryset(self):
        key = self.kwargs['key']
        print(key)
        return User.objects.filter(Q(username__icontains=key) | Q(email__icontains=key) | Q(id_number__icontains=key), systemCompany=self.request.user.systemCompany)


class UserSearchCollectionView(generics.RetrieveUpdateDestroyAPIView):
    '''Super admin can delete update and  retrieve'''
    permission_classes = (IsAuthenticated, AdminAuthenticationPermission,)
    queryset=User.objects.all()
    lookup_field='username'
    serializer_class= UserSerializer



class UserRoleManage(generics.RetrieveUpdateDestroyAPIView):
    queryset=User.objects.all()
    lookup_field = 'id'
    serializer_class= UserGroupSerializer

    def put(self, request, id):
        print (id)
        user = User.objects.get(id=id)
        try:
            g=Group.objects.get(id=request.data['group_id'])
            user.groups.add(g)
            return Response(status=status.HTTP_201_CREATED)
        except :
            return Response(status=status.HTTP_400_BAD_REQUEST)



class GroupsView(generics.ListCreateAPIView):
    '''Create and list all groups'''

    lookup_field='created_by'
    queryset=GroupRoles.objects.all()
    serializer_class=GroupSerializer

class GroupView(generics.RetrieveUpdateDestroyAPIView):
    '''Retrieve a role ,edit and or delete it '''
    permission_classes = (IsAuthenticated, AdminAuthenticationPermission,)
    lookup_field='id'
    queryset=GroupRoles.objects.all()
    serializer_class=GroupSerializer

    
class GroupSearch(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    lookup_field = 'name'
    
    serializer_class = GroupSerializer
    def get_queryset(self):
        return GroupRoles.objects.filter(name__icontains=self.kwargs['name'])


class SystemResourcesView(generics.ListCreateAPIView):
    '''Create and list all SystemResources'''

    permission_classes = (IsAuthenticated, AdminAuthenticationPermission,)
    queryset=SystemResources.objects.all()
    serializer_class=SystemResourcesSerializer

class SystemResourceView(generics.RetrieveUpdateDestroyAPIView):
    '''Create and list all SystemResources'''

    permission_classes = (IsAuthenticated, AdminAuthenticationPermission,)
    lookup_field='id'
    queryset=SystemResources.objects.all()
    serializer_class=SystemResourcesSerializer

    #Manage permissions

class SystemPermissionsView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, AdminAuthenticationPermission,)
    queryset= Permission.objects.all()
    serializer_class=SystemPermissionsSerializer
class SystemPermissionView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, AdminAuthenticationPermission,)
    lookup_field='id'
    queryset= Permission.objects.all()
    serializer_class=SystemPermissionsSerializer
class CountiesView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, AdminAuthenticationPermission,)
    queryset=Counties.objects.all()
    serializer_class=CountiesSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('name', 'county_code',)
    ordering_fields = ('name', 'county_code',)
    def get_queryset(self):
        return Counties.objects.filter(company=self.kwargs['company'])
     

class CountyView(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    permission_classes = (IsAuthenticated, AdminAuthenticationPermission,)
    lookup_field='id'
    queryset= Counties.objects.all()
    serializer_class=CountiesSerializer



    def perform_create(self,serializer):
        c=Counties.objects.filter(name=self.request.data['name'],company=self.request.user.systemCompany)
        if c.exists():
            raise AppValidation("Item already exists.",status_code="400")

        serializer.save(company=SystemCompany.objects.get(
            id=self.request.data['company']))

    def perform_update(self, serializer):
        serializer.save(company=SystemCompany.objects.get(
            id=self.request.data['company']))




class CountyFilesView(APIView):
    permission_classes = (IsAuthenticated, AdminAuthenticationPermission,)
    def uploader(self,file_data, data):
        lines = file_data.split("\n")
        existing = []
        print(type(lines))

        for index,line in enumerate(lines,start=1):
            if index == 1:
                continue
            fields = line.split(",")
            if not fields[0]: #first cell has nothing...lets skipp
                existing.append(fields)
                continue

            county_code =fields[1]
            county_name = fields[2]
            sub_county = fields[3]
            station_code = fields[4]
            station_name = fields[5]


            if county_code  and county_name and sub_county and station_code:
                #check if county exists:
                county = self.check_county(county_code, county_name)
                sub_county_id = self.check_sub_county(county,sub_county)
                self.check_station(sub_county_id,station_code,station_name)

                print ("success","Next")
            else:
                existing.append(fields) #there were empty cells store and skip
                continue


       

    def post(self,request):
        data= request.data
        print(request.FILES)
        company=data['company']
        file_obj = request.FILES['csv_file']
        if not file_obj.name.endswith('.csv'):
            raise AppValidation("Unacceptable file format.Please upload a csv file","File Format",status_code =400)
        if file_obj.multiple_chunks():
            raise AppValidation(
                "Uploaded file is too big "+ str(file_obj.size/(1000*1000))+" Mb", "File size", status_code=400)

        file_data = file_obj.read().decode("utf-8")
        lp = threading.Thread(target=self.uploader, args=(file_data,data))
        lp.daemon = True
        lp.start()

        return Response({})

    def check_station(self,sub_county,station_code, station):
        sc = Schools.objects.filter(sub_county=sub_county, station_code=station_code,name=station)
        print (sc)
        print (station)
        if sc.exists():
            x = sc.filter(name__isnull=True)
            if x.exists() and x.count() == 1:
                x.update(name=station)
            return sc[0]

        p, created = Schools.objects.get_or_create(sub_county=sub_county, station_code=station_code, defaults={"sub_county":sub_county, "station_code":station_code,
            "name": station})
              
        if p:
            return p
        else:
            return created


    def check_sub_county(self,county,sub_county):
        sc = Subcounty.objects.filter(county=county,name=sub_county)
        if sc.exists():
            return sc[0]
        p, created = Subcounty.objects.get_or_create(name=sub_county,county=county.id, defaults={
                                                    "county": county, "name":sub_county })
        if p:
            return p
        else:
            return created


    def check_county(self,county_code,county):
        c = Counties.objects.filter(name=county)
        if c.exists():
            return c[0];
        p, created = Counties.objects.get_or_create(name=county, defaults={
                                                    "county_code": county_code, "name": county, "company": self.request.user.systemCompany})
        if p:
            return p
        else:
            return created

class countyschools(generics.ListAPIView):
    permission_classes = (IsAuthenticated, AdminAuthenticationPermission,)
    serializer_class = SchoolsSerializer

    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('name', 'phone_no','station_code','sub_county__name','sub_county__county__name','sub_county__county__county_code')
    ordering_fields = ('name', 'phone_no', 'station_code', 'sub_county__name',
                       'sub_county__county__name', 'sub_county__county__county_code')

    
    def get_queryset(self):
        # if its a uuid.ie comes from client
        if CleanValidation().validate_uuid4(self.kwargs['sub_county']):

            return Schools.objects.filter(sub_county=self.kwargs['sub_county'])
        else:
            return Schools.objects.filter(sub_county__name=self.kwargs['sub_county'])

class SchoolsView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, AdminAuthenticationPermission,)
    serializer_class=SchoolsSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('name', 'phone_no', 'station_code', 'sub_county__name',
                     'sub_county__county__name', 'sub_county__county__county_code')
    ordering_fields = ('name', 'phone_no', 'station_code', 'sub_county__name',
                       'sub_county__county__name', 'sub_county__county__county_code')

    def get_queryset(self):

        return Schools.objects.filter(sub_county__county__company=self.kwargs['company'])

        
class SchoolView(generics.RetrieveUpdateDestroyAPIView,generics.CreateAPIView):
    #permissions any user with group schools view permissions or member...
    permission_classes = (IsAuthenticated, AdminAuthenticationPermission,)
    lookup_field='id'
    queryset= Schools.objects.all()
    serializer_class=SchoolsSerializer



    def perform_create(self,serializer):
        c = Schools.objects.filter(
            name=self.request.data['name'], sub_county__county__company=self.request.user.systemCompany)
        if c.exists():
            raise AppValidation("Item already exists.", status_code="400")

        try:

            serializer.save(sub_county=Subcounty.objects.get(
                id=self.request.data['sub_county']))
            return Response(serializer.data)
        except serializers.ValidationError:
            raise AppValidation(
                "Adding this school failed.Please try again or contact support", 401)


    def perform_update(self,serializer):
        serializer.save(county=Counties.objects.get(
            id=self.request.data['county_id']))

class ProfileView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, AdminAuthenticationPermission,)

    queryset=Profile.objects.all()
    serializer_class=ProfileSerializer




class ProfileSingleView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, AdminAuthenticationPermission)
    lookup_field="id"
    queryset=Profile.objects.all()
    serializer_class=ProfileSerializer



#Register
class RegisterView(
                  generics.ListCreateAPIView
                 ):
    permission_classes = (AllowAny,) #is owber
    queryset=User.objects.all()
    serializer_class =  ProfileSerializer
    # def post(self, request, *args, **kwargs):
    #     username = request.data['username']
    #     print (request.data['dob'])

    #     return self.create(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        print ("Create")
        #user serializer

        serializer = FrontEndUserSerializer(data=request.data)
        serializerProf = ProfileSerializer(data=request.data)
        user =None
       
        password = oh.randChar(5)
        if  serializer.is_valid():
            print ("try save")
            try:
                user=serializer.save()
                user.set_password(password)
                user.save()
            except:
                return Response({"status":"error","message":"Registration was unsuccessful.That username already exists",
                            "data":serializer.errors},status=status.HTTP_400_BAD_REQUEST)


        else:
            return Response({"status":"error","message":"Registration was unsuccessful",
                            "data":serializer.errors},status=status.HTTP_400_BAD_REQUEST)

        if serializerProf.is_valid():
            try:
                print ("denis mwi")
                serializerProf.save(user=user)
            except:
                user.save(commit=False)
        else:
            return Response({"status":"error","message":"Registration was unsuccessful",
                            "data":serializerProf.errors},status=status.HTTP_400_BAD_REQUEST)

        return Response({"status":"success","message":"Registration was successful"},status=status.HTTP_201_CREATED)
    

    def get(self, request, *args, **kwargs):
    
        return self.list(request, *args, **kwargs)

#login response
def jwt_response_payload_handler(token, user=None, request=None):
    username = request.data['username']
    password = request.data['password']
    logger.info("jwt login response")

    p = ''
    if user:

        p = Profile.objects.get(user=user.id)

        if "phone_model" in request.data:
            if not p.phone_model:
                logger.info("phone model")
                p.phone_model=request.data['phone_model']
                p.save()

        if "imei_number1" in request.data:
            a= Profile.objects.filter(imei_number1=request.data['imei_number1'])
            if a.count() >= 2:
                return {"status":"error","message":"Dear esteemed customer,This account is opened on another phone."}
            if not p.imei_number1 :
                p.imei_number1=request.data['imei_number1']
                p.save()
            if a.count() >= 2:
                return {"status":"error","message":"Dear esteemed customer,This account is opened on another phone."}
        if "imei_number2" in request.data:
            if not p.imei_number2:
                p.imei_number2=request.data['imei_number2']
                p.save()
        c=CleanValidation(user.id)

        imei=c.checkImei(p,request)
        print (imei)
        if not imei:
            return {"status":"error","message":"Dear esteemed customer,This account is opened on another phone."}
        if not c.checkPhoneModel(p,request):
            return {"status":"error","message":"Dear esteemed customer,This account is opened on another phone."}
    else:
        return {"status":"error","message":"User account  does not exist"}


    update_last_login(None,user)
    return {'token': token,'status': 'success','reset': p.password_reset,'user': user.id}




#recover password

@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def recover_passwordAPI(request):
    username = str(request.data['username']).strip()
    username = val.format_phone(phone = username)
    if len(username) < 9:
        return Response({'status': 'error','message': 'Length of phone number too short'})
    else:
        if len(username) > 11:
            return Response({'status': 'error','message': 'Length of phone number too long'})
        u = ''
        p = PasswordRecoverSerializer(data={'username': username})
        if p.is_valid():
            try:
                u = User.objects.get(username=p.validated_data['username'])
            except:
                return Response({'status': 'error','message': 'That user does not exist'})

            prof = Profile.objects.filter(user__id=u.id)
            password = oh.randChar(5)
            prof.update(password_reset='YES')
            u.set_password(password)
            u.save()
            email=u.email

            print (password)
         
            tpl=ms.getEmailTemplates("RECOVER_PASSWORD")
            #email this pasword
            message = tpl.message
            msg.sendEmailMessage(email,SUPPORT_MAIL,tpl.subject,message.replace("#",password),u)


            status = 'A message has been sent to your email  with a temporary password'
            return Response({'status': 'success','message': status})
        a = p.errors
        a['status'] = 'error'
        return Response(a)


#reset password/change
@api_view(['POST'])
def password_change(request):

    logger.info("password change")
    password = request.data['old_password']
    password2 = request.data['new_password']
    user_id=request.data['user']
    p = PasswordChangeSerializer(data={'password': password})
    c = PasswordChangeSerializer(data={'password': password2})
    logger.info(request.data)
    if p.is_valid() and c.is_valid():
        x=User.objects.get(id=user_id)
        if x:
            x.set_password(c.validated_data['password'].strip())
            x.save()
            req = {'username': x.username,'password': c.validated_data['password'].strip()}
            r = requests.post(URL + '/api/api-token-auth/', data=req)

            a=r.json()
            logger.info(a)
            if "non_field_errors" in a :
                logger.info("non_field_errors")
                return Response({"status":"error","message":"Unable to re-login with provided credentials"})

            token = a['token']
            Profile.objects.filter(user=x.id).update(password_reset="NO")
            return Response({'token': token,'user': user_id,'status': 'success','message': 'Password updated correctly'})
        else:
            return Response({'status': 'error','message': 'User does not exist'})

    else:
        a = p.errors
        a['status'] = 'error'
        return Response(a)


class RegisterManageTeacher(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, AdminAuthenticationPermission,)
    lookup_field="user"
    queryset=Profile.objects.all()
    serializer_class=TeacherSerializer

#update fcm for gcm push communications
@api_view(['POST'])
def initializeFCM(request):
    Profile.objects.filter(user=request.data['user']).update(fcm_id=request.data['fcm_token'])
    return Response({"status":"success","message":"fcm token has been updated"})


class SetStatus(APIView):
    def put(self,request,user,status):
        if status == Resource.SKIP_SCORING:
            User.objects.filter(user=user).update(status=Resource.SKIP_SCORING)

######end of module 1

def policy(request):
    return render(request,'privacypolicy.html',{})

def terms(request):
    return render(request,'terms.html',{})
