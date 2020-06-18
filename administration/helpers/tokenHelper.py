
from rest_framework_simplejwt.tokens import AccessToken
class TokenHelper:
    @staticmethod
    def get_token(requestObj=None):
        if requestObj == None:
            return None
        try:
            token_str = (requestObj.META.get('HTTP_AUTHORIZATION') or requestObj.GET.get('token'))
            #print("token string: ",token_str)
            token = AccessToken(token_str.split(' ')[1])
            #print("the token: ", token)
            return token
        except Exception as e:
       
            return None

    @staticmethod
    def get_token_key(requestObj, key):
        token = TokenHelper.get_token(requestObj)
        if token == None:
            return None
        try:
            keyValue = token.payload[key]
            return keyValue
        except Exception as e:
         
            return None

    @staticmethod
    def get_company_id(requestObj):
        #c_id = TokenHelper.get_token_key(requestObj, "company_id")
       
        c_id = requestObj.user.systemCompany.id
        return c_id
    
    @staticmethod
    def get_user_id(requestObj):
        #c_id = TokenHelper.get_token_key(requestObj, "company_id")
        id = requestObj.user.id
        return id
    
  
   


