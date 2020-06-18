from administration.models.administration import SystemCompany, SystemRole
from administration.models.authorization import CompanyResource, RolePermission
from administration.models.resourceEnums import Perm, ResourceType
import itertools
from operator import itemgetter


class RolePermissionHelper:

    @staticmethod
    def get_role_permissions(role_id):
        try:
            role = SystemRole.objects.get(pk=role_id)
            resources = CompanyResource.objects.filter(
                company__id=role.company_id)

            existing = role.permissions.all()
            role_perms = []
            permission_list = [item for item in Perm]
            #print(permission_list)

            def get_permission_assigned(target, assigned):
                assignments = []
                for perm in permission_list:
                    if perm.value & target and perm.value != Perm.ALL.value:
                        assignments.append({
                            "permission": perm.value,
                            "name": perm.name,
                            "isAssigned": (perm.value & assigned) != 0
                        })
                return sorted(assignments, key=itemgetter('name'))

            for resource in resources:
                if resource.resource.resource.resource_type == ResourceType.ACTION.value or resource.resource.resource.resource_type == ResourceType.URL.value:
                    perm = {
                        "resource": resource.id,
                        "name": resource.name,
                        "section": resource.resource.resource.section
                    }
                    thePerm = [
                        perm for perm in existing if perm.resource == resource]
                    if len(thePerm) > 0:
                        perm["permissionAssignments"] = get_permission_assigned(
                            resource.permission, thePerm[0].permissions)
                    else:
                        perm["permissionAssignments"] = get_permission_assigned(
                            resource.permission, 0)
                    role_perms.append(perm)

            sorted_perms = sorted(role_perms, key=itemgetter('section'))
            grouped_perms = []
            for key, group in itertools.groupby(sorted_perms, key=lambda x: x['section']):
                grouped_perms.append({
                    "name": key,
                    "resourcePermissions": sorted(list(group), key=itemgetter('name'))
                })
            return grouped_perms
        except SystemRole.DoesNotExist:
            pass

        return []

    @staticmethod
    def update_role_permissions(role_perm):

        def get_resource_permissions(permissionAssignments):
            assignments =[item["permission"] for item in permissionAssignments if item["isAssigned"]==True]
            if len(assignments)>0:
                perm = assignments[0]
                for p in assignments:
                    perm = perm | p
                
                return perm

            return Perm.ZERO.value

        try:
            role = SystemRole.objects.get(pk=role_perm["id"])
            #resources = CompanyResource.objects.filter(company__id=role.company_id)

            existing = role.permissions.all()
            for section in role_perm["resourceSections"]:
                for resource in section["resourcePermissions"]:
                    try:
                        rPerm = RolePermission.objects.get(role_id=role_perm["id"], resource_id=resource["resource"])
                        print("Found permission ", rPerm.id)
                    except RolePermission.DoesNotExist:
                        rPerm = RolePermission()
                        rPerm.role_id = role_perm["id"]
                        rPerm.resource_id = resource["resource"]

                    rPerm.permissions = get_resource_permissions(resource["permissionAssignments"])
                    rPerm.save()
        except SystemRole.DoesNotExist:
            pass
