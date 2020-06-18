from administration.models.models import *

class OpalCompanies:
    def getCompanies(self):
        return Companies.objects.all()
    def getCompany(self,id):
        try:
            return Companies.objects.get(id=id)
        except:
            return None

    def deleteCompany(self):
        return self.getCompanies().filter(id=id).delete()

    def createCompany(self,data):
        c=Companies()
        c.phone=data['phone']
        c.email=data['email']
        c.location=data['location']
        c.user=data['userObj']
        c.company_name=data['company_name']
        c.save()
        
