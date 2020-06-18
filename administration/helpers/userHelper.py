from administration.models.administration import BankDetail ,SourceOfIncome
from administration.models.models import Teachers
class SourceOfIncomeHelper:
    @staticmethod
    def setIncome(payload):
        return SourceOfIncome.objects.create(**payload)

    @staticmethod
    def checkIncomeSet(self, payload):
        s = SourceOfIncome.objects.filter(user=payload['user'])
        if s.exists():
            return s
        else:
            return False

class BankDetailHelper:
    @staticmethod
    def createBankDetail(payload):
        print(payload)
        return BankDetail.objects.create(**payload)
   
    #upload selfie
    #upload clear image of national Id
    #link with linkedin

    #link with facebook

    #link with twitter



class TeacherHandler:
    @staticmethod
    def verifyTeacher(user,tsc_number):
        t=Teachers.objects.filter(id_number=user.id_number, tsc_number=tsc_number)
        if t.exists():
            return t
        else:
            return False