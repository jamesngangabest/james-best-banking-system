from administration.helpers.systemResourceHelpers import *
from administration.helpers.companyTypeHelpers import *
from administration.models.administration import SystemCompany, SystemRole
from administration.models.authorization import CompanyResource

class CompanySetupHelper:


    @staticmethod
    def setup(data):
        #create global resource
        SystemResourceHerlper.create_update()

        #create company type
        CompanyTypeHelper.create(data['company']['company_type'])

        #create default company
        company_id=CompanySetupHelper.create_company(data['company'])

        #update company resources
        CompanySetupHelper.update_company_resources(company_id)

        #create default role
        role_id = CompanySetupHelper.create_role(company_id, data['role'])

        #create default user
        CompanySetupHelper.update_default_role_permissions(role_id)
        
        #create default threshold


        #create default score card

        

    @staticmethod
    def create_company(data):
        try:
            company = SystemCompany.objects.get(name=data['name'])
        except SystemCompany.DoesNotExist:

            company = SystemCompany()
            company.name = data['name']
            company.domain = data['domain']
            company.company_type_id = data['company_type']
            company.is_default = data['is_default']
            company.is_active = True

        #create/update
        company.save()
        #company.refresh_from_db()
        return company.id

    @staticmethod
    def create_role(company_id, data):
        try:
            role = SystemRole.objects.get(name=data['name'])
        except SystemRole.DoesNotExist:
            role = SystemRole()
            role.name = data['name']
            role.company_id = company_id
            role.is_active = True
            role.is_default = data['is_default']

        #create/update
        role.save()
        return role.id

    @staticmethod
    def update_company_resources(company_id):
        company = SystemCompany.objects.get(pk=company_id)
        resources = CompanyTypeResource.objects.filter(company_type__id=company.company_type_id)#.exclude(resource__id="3db33042-be7a-4b54-9f5e-b1e1dfe102c8")
        existing = CompanyResource.objects.filter(company__id=company_id)

        #print('Resources Count: ', len(resources))
        #print("Existing Count: ", len(existing))
        toDelete = [item for item in existing if item.resource not in resources]
        #print("To Delete Count: ", len(toDelete))
        for item in toDelete:
            rpas = RolePermission.objects.filter(resource=item)
            for rpa in rpas:
                rpa.delete()

            item.delete()

        for item in resources:
            try:
                cResource = CompanyResource.objects.get(company__id=company_id, resource=item)
                #print('Resource ', item.resource)
            except CompanyResource.DoesNotExist:
                #print("Resource to create ", item.resource.resource)
                cResource = CompanyResource()
                cResource.company_id = company_id
                cResource.resource = item
            
            cResource.name = item.name
            cResource.display_order = item.display_order
            cResource.permission = item.permission
            cResource.is_active = item.is_active

            #create/update
            cResource.save()

        
    @staticmethod
    def update_default_role_permissions(role_id):
        try:
            role = SystemRole.objects.get(pk=role_id)
            resources = CompanyResource.objects.filter(company__id=role.company_id)

            existing = role.permissions.all()
            toDelete = [item for item in existing if item.resource not in resources]
            # print("Resources count: ", len(resources))
            # print("Existing Count: ", len(existing))
            # print("To Delete Count: ", len(toDelete))

            for item in toDelete:
                item.delete()

            for item in resources:
                try:
                    rPerm = RolePermission.objects.get(role=role, resource=item)
                except RolePermission.DoesNotExist:
                    rPerm = RolePermission()
                    rPerm.role = role
                    rPerm.resource = item

                rPerm.permissions = item.permission
                #create/update
                rPerm.save()
        except SystemRole.DoesNotExist:
            pass

        
        
    


    


