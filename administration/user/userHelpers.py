
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
User = get_user_model()

class UserHelper:
    def getUserObj(self,id):
        try:
            return User.objects.get(id=id)
        except ObjectDoesNotExist:
            return None
