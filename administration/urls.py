from django.urls import path

from . import views
from rest_framework_jwt.views import obtain_jwt_token,refresh_jwt_token
from administration.apiviews import administrationViews, tokenViews
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('api/companies/all/', views.CompaniesCollection.as_view()), #list and create company

    path('api/company/<int:id>/', views.CompanySingle.as_view()), #retrieve,update,delete company
    path('api/admin/company/setting/', administrationViews.CompanySettingDetail.as_view()), 
    path('api/admin/company/setting/<id>/', administrationViews.CompanySettingDetail.as_view()), 

    path('api/users/all/', views.UsersCollectionView.as_view()), # #create and list users
    # create and list users
    path('api/admin/users/fileupload/', views.UsersFileUploadView.as_view()),
    path('api/admin/users/profilepictures/<id>/', views.UserImagesUploadView.as_view()),

    path('api/admin/teachers/<company>/', views.TeachersCollectionView.as_view()),
    path('api/admin/teacher/<id>/', views.TeacherCollectionView.as_view()),
 



    path('api/user/<id>/', views.UserCollectionView.as_view()),#retrieve,update,delete  user
    path('api/user/', views.UserCollectionView.as_view()),#retrieve,update,delete  user
    path('api/user/search/<username>/', views.UserSearchCollectionView.as_view()),#retrieve,update,delete  user

    path('api/user/<id>/manage/role/', views.UserRoleManage.as_view()),#retrieve,update,delete  use

    path('api/roles/all/', views.GroupsView.as_view()), #get all OR CREATE roles/group
    path('api/roles/all/', views.GroupsView.as_view()), #get all OR CREATE roles/group
    path('api/roles/search/<name>', views.GroupSearch.as_view()),

    path('api/roles/user/<int:created_by>/', views.GroupsView.as_view()), #get  roles/group created by a member

    path('api/roles/user/manage/<int:id>/', views.GroupView.as_view()), #Edit a particular group object

    path('api/system/resources/', views.SystemResourcesView.as_view()), #SYStem resources
    path('api/system/resource/<int:id>/', views.SystemResourceView.as_view()),#manage a single resource

    #create permissions and list
    path('api/system/permissions/', views.SystemPermissionsView.as_view()),
    #create user profile and assign groups,
    path('api/user/profile/all/', views.ProfileView.as_view()),

    path('api/user/profile/single/<int:id>/', views.ProfileSingleView.as_view()),
    #add register
    path('api/v1/admin/usersearch/<key>/', views.Usearsearch.as_view()),


    #add school

    path('api/admin/schools/<company>/', views.SchoolsView.as_view()),
    path('api/admin/countyschools/<sub_county>/', views.countyschools.as_view()),
    path('api/admin/school/', views.SchoolView.as_view()),
    path('api/admin/school/<id>/', views.SchoolView.as_view()),

  

    path('api/admin/counties/<company>/', views.CountiesView.as_view()),
    path('api/admin/county/', views.CountyView.as_view()),
    path('api/admin/county/<id>/', views.CountyView.as_view()),
    path('api/admin/countyfiles/', views.CountyFilesView.as_view()),

    path('api/admin/user/setstatus/<user>/', views.SetStatus.as_view()),


    #user
    ###mobile app API##
    ##Register###
    path('api/account/register/', views.RegisterView.as_view()),
    ###
    path('api/api-token-auth/', obtain_jwt_token),
    #Refresh token
    path('api/api-token-refresh/', refresh_jwt_token),

    #change password after OTP SENT
    path('api/account/change/password/', views.password_change),


    path('api/account/teacher/manage/<int:user>/', views.RegisterManageTeacher.as_view(),name="register_teacher"),
    #ENTER ACCOUNT NAME TO SENT OTP
    path('api/account/recover/password/', views.recover_passwordAPI,name="recover_password"),
    #fcm push key
    path('api/fcm/initialize/', views.initializeFCM),

    #administration
    path('api/admin/company-types/', administrationViews.CompanyTypeList.as_view()),
    path('api/admin/resources/', administrationViews.GlobalResourceList.as_view()),
    path('api/admin/updateresources/', administrationViews.UpdateCompanyResources.as_view()),
    path('api/admin/setup/', administrationViews.CompanySetup.as_view()),
    path('api/admin/system-menus/', administrationViews.SystemMenu.as_view()),

    path('api/admin/companies/', administrationViews.SystemCompanyList.as_view()), #
    path('api/admin/company/<id>/', administrationViews.SystemCompanyDetail.as_view()), #
    path('api/admin/current-company/', administrationViews.SystemCompanyDetailCurrent.as_view()), #
    path('api/admin/roles/', administrationViews.SystemRoleList.as_view()), #
    path('api/admin/role/<id>/', administrationViews.SystemRoleDetail.as_view()), #

    path('api/admin/role/<id>/permissions/', administrationViews.SystemRolePermission.as_view()), #
    path('api/admin/role/', administrationViews.SystemRoleDetail.as_view()), #

    # bank
    path('api/admin/banks/<company>/', administrationViews.BankAdminViews.as_view()),
    path('api/admin/uploadbanks/',  administrationViews.BankFileUploadView.as_view()),
    path('api/admin/bank/', administrationViews.BankAdminViewDetail.as_view()),
    path('api/admin/bank/<id>/', administrationViews.BankAdminViewDetail.as_view()),

    path('api/admin/branches/<bank>/', administrationViews.BranchAdminViews.as_view()),
   
    path('api/admin/branch/',
         administrationViews.BranchAdminViewDetail.as_view()),
    path('api/admin/branch/<id>/',
         administrationViews.BranchAdminViewDetail.as_view()),


    path('api/admin/subcounties/<county>/', administrationViews.SubCountyViews.as_view()),
    path('api/admin/subcounty/<id>/',
         administrationViews.SubCountyViewDetail.as_view()),

    path('api/admin/subcounty/',
         administrationViews.SubCountyViewDetail.as_view()),
    


    path('api/admin/bankaccounts/<user>/', administrationViews.BankUserDetails.as_view()),
    path('api/admin/bankaccount/',
         administrationViews.BankUserDetail.as_view()),
    path('api/admin/bankaccount/<id>/', administrationViews.BankUserDetail.as_view()),
    
    
    
    # next of kin
    path('api/admin/nextofkins/<user>/', administrationViews.NextOfKinViews.as_view()),
   
    path('api/admin/nextofkin/',
         administrationViews.NextOfKinAdminDetail.as_view()),

    path('api/admin/nextofkin/<id>/', administrationViews.NextOfKinAdminDetail.as_view()),

    path('api/admin/errorlogs/',
         administrationViews.AdminErrorLogs.as_view()),
    path('api/admin/errorlog/<id>/', administrationViews.AdminErrorLog.as_view()),

    path('api-auth/token/obtain/', tokenViews.CustomTokenObtainPairView.as_view(), name='token-obtain'),
    path('api-auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),


    path('api/admin/securityquestions/<company>/',
         administrationViews.SecurityQuestionsView.as_view()),
    path('api/admin/securityquestion/', administrationViews.SecurityQuestionView.as_view()),

   


]
if settings.DEBUG:
      urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
