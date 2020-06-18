from rest_framework.exceptions import APIException
from django.utils.encoding import force_text
from rest_framework import status
from rest_framework.response import Response
from .models import ErrorLoggerModel
from rest_framework.views import exception_handler

class AppValidation(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'

    def __init__(self, detail, field=None, status_code = None):
        #print (status_code)
        #print ()
        if status_code :
            self.status_code = status_code
        if detail:
            self.detail = {field: force_text(detail)}
        if field:
            self.field = {field:force_text(detail)}
        else:
            # self.detail = {'detail': force_text(self.default_detail)}
            self.field = "detail"
            

class ErrorLogger:
    def __init__(self,subject,message,response=None,user=None):
        e = ErrorLoggerModel()
        e.subject=subject
        e.message =message
        e.responseDump = response
        print("error logger") 
        print(user)
        if user:
            e.user =user
            e.company = user.systemCompany
        e.save()
        

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    print(response,exc)
    if isinstance(exc, AppValidation):
        response=Response(data=vars(exc)["detail"],status=status.HTTP_400_BAD_REQUEST)
        
    if response is None:
        response=Response(data={"errorMessage":str(exc)},status=status.HTTP_400_BAD_REQUEST)
    
    return response
