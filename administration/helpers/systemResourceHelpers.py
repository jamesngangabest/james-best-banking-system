from administration.models.administration import *
from administration.models.authorization import *
from administration.models.resourceEnums import *
import uuid

from django.db import transaction, IntegrityError

class SystemResourceViewModel(object):
    def __init__(self, id, name, section, url, display_order, is_active, resource, resource_type, parent_id, parent_resource, permissions):
        self.id = id
        self.name = name
        self.section = section
        self.url = url
        self.display_order = display_order
        self.is_active = is_active
        self.resource = resource
        self.resource_type = resource_type
        self.permissions = permissions
        self.parent_id = parent_id
        self.parent_resource = parent_resource


class MenuViewModel(object):
    def __init__(self, resource):
        self.id = resource.resource.resource.id
        self.parent_id = resource.resource.resource.parent_id
        self.url = resource.resource.resource.url
        self.name = resource.name
        self.display_order = resource.display_order
        self.children = []


class SystemResourceHerlper:
    @staticmethod
    def get_system_menus_by_role_id(role_id):
        role = SystemRole.objects.get(pk=role_id)
        #print("Role Name: ", role.name)
        link_menus = RolePermission.objects.filter(role=role).exclude(permissions=Perm.ZERO.value).exclude(
            resource__resource__resource__resource_type=ResourceType.CONTAINER.value).exclude(
            resource__resource__resource__permission=Perm.ZERO.value)
        link_menus = [item.resource for item in link_menus]
        container_menus = CompanyResource.objects.filter(
            company=role.company, resource__resource__resource_type=ResourceType.CONTAINER.value)

        link_menus.extend(container_menus)

        def toMenu(resource):
            menu = {
                "id": resource.resource.resource.id,
                "parent_id": resource.resource.resource.parent_id,
                "route": resource.resource.resource.url,
                "displayName": resource.name,
                "resource_type": resource.resource.resource.resource_type,
                "display_order": resource.display_order,
                "children": []
            }
            return menu
        link_menus = [toMenu(item) for item in link_menus]
        menus = [item for item in link_menus if item["parent_id"] == None]
        menus.sort(key=lambda x: x["display_order"])

        def setChildren(items):
            for item in items:
                item["children"] = [
                    child for child in link_menus if child["parent_id"] == item["id"]]
                for child in item["children"]:
                    child['route'] = item['route'] + '/' + child['route']

                item["children"] = sorted(
                    item["children"], key=lambda x: x["display_order"])
                setChildren(item["children"])

        def pruneMenus(menus):
            outputs = []
            for menu in menus:
                if menu["resource_type"] == ResourceType.URL.value:
                    outputs.append(menu)
                else:
                    children = pruneMenus(menu["children"])
                    if len(children) > 0:
                        menu["children"] = children
                        outputs.append(menu)
            return outputs

        setChildren(menus)
        pruned = pruneMenus(menus)
        # for menu in pruned:
        #     print("Children Count: ", len(menu["children"]))
        #     for child in menu["children"]:
        #         print("--Children Count: ", len(child["children"]))

        return pruned

    @staticmethod
    def create_update():
        print("updating resources...")
        resources = SystemResourceHerlper.get_resources()

        try:
            with transaction.atomic():
                #  pass

                for item in resources:
                    if item.parent_resource != None:
                        # Update parent Id
                        try:
                            parent = GlobalResource.objects.get(
                                resource=item.parent_resource)
                            item.parent_id = parent.id
                        except GlobalResource.DoesNotExist:
                            pass
                    try:
                        resource = GlobalResource.objects.get(
                            resource=item.resource)
                        #print(item.name, ' found in db')

                    except GlobalResource.DoesNotExist:
                        # print(item.name, ' not in db: Perms ',
                        #        item.permissions)

                        resource = GlobalResource()
                        resource.id = item.id

                    resource.name = item.name
                    resource.section = item.section
                    resource.url = item.url
                    resource.display_order = item.display_order
                    resource.is_active = True
                    resource.resource = item.resource
                    resource.resource_type = item.resource_type
                    resource.permission = item.permissions
                    resource.parent_id = item.parent_id

                    #print(resource.resource, " Perm: ", resource.permission, " - ", resource.name)

                    # create/update
                    resource.save()
        except IntegrityError:
            print("integrity error occurred..")
        except Exception as e:
            print("some error occurred..",e)

    @staticmethod
    def get_resources():
        resources = list()
        resources.extend(SystemResourceHerlper.get_admin_resources())
        resources.extend(SystemResourceHerlper.get_finance_resources())
        resources.extend(SystemResourceHerlper.get_scoring_resources())
        resources.extend(SystemResourceHerlper.get_client_resources())

        resources.extend(SystemResourceHerlper.get_sacco_resources())
        resources.extend(SystemResourceHerlper.get_bp_resources())
        resources.extend(SystemResourceHerlper.get_ap_resources())
        resources.extend(SystemResourceHerlper.get_hr_resources())
        resources.extend(SystemResourceHerlper.get_reporting_resources())
        resources.extend(SystemResourceHerlper.get_crm_resources())
        return resources

    #region Admin Resources
    
    @staticmethod
    def get_admin_resources():
        resources = list()
        admin_id = uuid.uuid4()
        company_setup_id = uuid.uuid4()
        security_setup_id = uuid.uuid4()

        #resources.append({'id': admin_id, 'name': 'administration', 'section': SystemModule.ADMINISTRATION.value, 'url': 'admin', 'order': 1, 'activate': True, 'resource':Resource.ADMINISTRATION.value, 'type':ResourceType.CONTAINER.value,'parent_id': None, 'parent_resource': None, 'perms':Perm.READ.value })

        resources.append(SystemResourceViewModel(admin_id, "Administration", SystemModule.ADMINISTRATION.value,
                                                 "admin", 1, True, Resource.ADMINISTRATION.value, ResourceType.CONTAINER.value,  None, None, Perm.READ.value))
        resources.append(SystemResourceViewModel(company_setup_id, "Company Setup", SystemModule.ADMINISTRATION.value, "companysetup", 1, True,
                                                 Resource.COMPANY_SETUP.value, ResourceType.CONTAINER.value, admin_id, Resource.ADMINISTRATION.value, Perm.READ.value))

        resources.append(SystemResourceViewModel(uuid.uuid4(), "Companies", SystemModule.ADMINISTRATION.value, "companies", 1, True, Resource.COMPANIES.value,
                                                 ResourceType.URL.value, company_setup_id, Resource.COMPANY_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))

        resources.append(SystemResourceViewModel(uuid.uuid4(), "Company Details", SystemModule.ADMINISTRATION.value, "companydetails", 2,

                                                 True, Resource.COMPANY_DETAILS.value, ResourceType.URL.value, company_setup_id, Resource.COMPANY_SETUP.value, Perm.READ.value | Perm.UPDATE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Next Numbers", SystemModule.ADMINISTRATION.value, "nextnumbers", 3,
                                                 True, Resource.NEXT_NUMBERS.value, ResourceType.URL.value, company_setup_id, Resource.COMPANY_SETUP.value, Perm.READ.value | Perm.UPDATE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Default Settings", SystemModule.ADMINISTRATION.value, "defaultsettings", 4,
                                                 True, Resource.DEFAULT_SETTINGS.value, ResourceType.URL.value, company_setup_id, Resource.COMPANY_SETUP.value, Perm.READ.value | Perm.UPDATE.value))

        resources.append(SystemResourceViewModel(uuid.uuid4(), "Counties", SystemModule.ADMINISTRATION.value, "counties", 5,
                                                 True, Resource.COUNTIES.value, ResourceType.URL.value, company_setup_id, Resource.COMPANY_SETUP.value, Perm.READ.value | Perm.UPDATE.value))
    
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Schools", SystemModule.ADMINISTRATION.value, "schools", 7,
                                                 True, Resource.SCHOOLS.value, ResourceType.URL.value, company_setup_id, Resource.COMPANY_SETUP.value, Perm.READ.value | Perm.UPDATE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Teacher Upload", SystemModule.ADMINISTRATION.value, "teachers", 8,
                                                 True, Resource.TEACHERS.value, ResourceType.URL.value, company_setup_id, Resource.COMPANY_SETUP.value, Perm.READ.value | Perm.UPDATE.value))

        resources.append(SystemResourceViewModel(uuid.uuid4(), "Banks", SystemModule.ADMINISTRATION.value, "banks", 9,
                                                 True, Resource.BANKS.value, ResourceType.URL.value, company_setup_id, Resource.COMPANY_SETUP.value, Perm.READ.value | Perm.UPDATE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Error Logs", SystemModule.ADMINISTRATION.value, "adminlogs", 10,
                                                 True, Resource.ADMIN_ERROR_LOGGER.value, ResourceType.URL.value, company_setup_id, Resource.COMPANY_SETUP.value, Perm.READ.value | Perm.UPDATE.value))


        resources.append(SystemResourceViewModel(security_setup_id, "Security Setup", SystemModule.ADMINISTRATION.value, "securitysetup", 2, True,
                                                 Resource.SECURITY_SETUP.value, ResourceType.CONTAINER.value, admin_id, Resource.ADMINISTRATION.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Users", SystemModule.ADMINISTRATION.value, "users", 1, True, Resource.USERS.value, ResourceType.URL.value,
                                                 security_setup_id, Resource.SECURITY_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value | Perm.LOCK.value | Perm.UNLOCK.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Roles", SystemModule.ADMINISTRATION.value, "roles", 1, True, Resource.ROLES.value,
                                                 ResourceType.URL.value, security_setup_id, Resource.SECURITY_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Role Permissions", SystemModule.ADMINISTRATION.value, "", 1, True, Resource.ROLE_PERMISSIONS.value,
                                                 ResourceType.ACTION.value, security_setup_id, Resource.SECURITY_SETUP.value, Perm.READ.value | Perm.UPDATE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Update System Resources", SystemModule.ADMINISTRATION.value, "updatesystemresources",
                                                 1, True, Resource.RESOURCES_UPDATE.value, ResourceType.URL.value, security_setup_id, Resource.SECURITY_SETUP.value, Perm.READ.value | Perm.UPDATE.value))

        return resources
    
    #endregion

    #region Finance Resources
    
    @staticmethod
    def get_finance_resources():
        resources = list()
        finance_id = uuid.uuid4()
        ledger_setup_id = uuid.uuid4()
        general_ledger_id = uuid.uuid4()
        banking_id = uuid.uuid4()
        banking_setup_id = uuid.uuid4()

        resources.append(SystemResourceViewModel(finance_id, "Financials", SystemModule.FINANCIALS.value,
                                                 "finance", 2, True, Resource.FINANCIALS.value, ResourceType.CONTAINER.value,  None, None, Perm.READ.value))
        resources.append(SystemResourceViewModel(ledger_setup_id, "Ledger Setup", SystemModule.FINANCIALS.value, "ledgersetup", 1, True,
                                                 Resource.LEDGER_SETUP.value, ResourceType.CONTAINER.value, finance_id, Resource.FINANCIALS.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Account Types", SystemModule.FINANCIALS.value, "accounttypes", 1, True, Resource.ACCOUNT_TYPES.value,
                                                 ResourceType.URL.value, ledger_setup_id, Resource.LEDGER_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Transaction Types", SystemModule.FINANCIALS.value, "transactiontypes", 3, True, Resource.TRANSACTION_TYPES.value,
                                                 ResourceType.URL.value, ledger_setup_id, Resource.LEDGER_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Payment Methods", SystemModule.FINANCIALS.value, "paymentmethods", 5, True, Resource.PAYMENT_METHODS.value,
                                                 ResourceType.URL.value, ledger_setup_id, Resource.LEDGER_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Payment Terms", SystemModule.FINANCIALS.value, "paymentterms", 7, True, Resource.PAYMENT_TERMS.value,
                                                 ResourceType.URL.value, ledger_setup_id, Resource.LEDGER_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Profit/ Cost Centers", SystemModule.FINANCIALS.value, "responsibilitycenters", 9, True, Resource.RESPONSIBILITY_CENTERS.value,
                                                 ResourceType.URL.value, ledger_setup_id, Resource.LEDGER_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))

        resources.append(SystemResourceViewModel(general_ledger_id, "General Ledger", SystemModule.FINANCIALS.value, "generalledger", 3, True,
                                                 Resource.GENERAL_LEDGER.value, ResourceType.CONTAINER.value, finance_id, Resource.FINANCIALS.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Ledger Accounts", SystemModule.FINANCIALS.value, "accounts", 1, True, Resource.LEDGER_ACCOUNTS.value,
                                                 ResourceType.URL.value, general_ledger_id, Resource.GENERAL_LEDGER.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Fiscal Years", SystemModule.FINANCIALS.value, "fiscalyears", 3, True, Resource.FISCAL_YEARS.value,
                                                 ResourceType.URL.value, general_ledger_id, Resource.GENERAL_LEDGER.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Fiscal Year Closing", SystemModule.FINANCIALS.value, "fiscalyearclosing", 5, True, Resource.FISCAL_YEAR_CLOSING.value,
                                                 ResourceType.URL.value, general_ledger_id, Resource.GENERAL_LEDGER.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Ledger Transactions", SystemModule.FINANCIALS.value, "ledgertrans", 7, True, Resource.LEDGER_TRANSACTIONS.value,
                                                 ResourceType.URL.value, general_ledger_id, Resource.GENERAL_LEDGER.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))

        resources.append(SystemResourceViewModel(banking_id, "Banking", SystemModule.FINANCIALS.value,
                                                 "banking", 4, True, Resource.BANKING.value, ResourceType.CONTAINER.value,  finance_id, Resource.FINANCIALS.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(banking_setup_id, "Banking Setup", SystemModule.FINANCIALS.value, "bankingsetup", 1, True,
                                                 Resource.BANKING_SETUP.value, ResourceType.CONTAINER.value, banking_id, Resource.BANKING.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Recon Adjust. Categories", SystemModule.FINANCIALS.value, "reconadjustcategories", 1, True, Resource.BANK_RECON_ADJ_CATEGORIES.value,
                                                 ResourceType.URL.value, banking_setup_id, Resource.BANKING_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))

        resources.append(SystemResourceViewModel(uuid.uuid4(), "Bank Transactions", SystemModule.FINANCIALS.value, "banktrans", 3, True, Resource.BANK_TRANSACTIONS.value,
                                                 ResourceType.URL.value, banking_id, Resource.BANKING.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.VOID.value))

        resources.append(SystemResourceViewModel(uuid.uuid4(), "Bank Recons", SystemModule.FINANCIALS.value, "bankrecons", 5, True, Resource.BANK_RECONCILIATIONS.value,
                                                 ResourceType.URL.value, banking_id, Resource.BANKING.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.APPROVE.value | Perm.CANCEL.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Pending Recon Items", SystemModule.FINANCIALS.value, "pendingreconitems", 7, True, Resource.PENDING_RECON_ITEMS.value,
                                                 ResourceType.URL.value, banking_id, Resource.BANKING.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Bank Recons Resolutions", SystemModule.FINANCIALS.value, "reconresolutions", 9, True, Resource.BANK_RECON_RESOLUTIONS.value,
                                                 ResourceType.URL.value, banking_id, Resource.BANKING.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.APPROVE.value | Perm.CANCEL.value))

        return resources

    #endregion
    
    #region Scoring Resources
    
    @staticmethod
    def get_scoring_resources():
        resources = list()
        scoring_id = uuid.uuid4()
        scoring_setup_id = uuid.uuid4()

        resources.append(SystemResourceViewModel(scoring_id, "Scoring", SystemModule.SCORING.value,
                                                 "scoring", 5, True, Resource.SCORING.value, ResourceType.CONTAINER.value,  None, None, Perm.READ.value))

        resources.append(SystemResourceViewModel(scoring_setup_id, "Scoring Setup", SystemModule.SCORING.value, "scoringsetup", 1, True,
                                                 Resource.SCORING_SETUP.value, ResourceType.CONTAINER.value, scoring_id, Resource.SCORING.value, Perm.READ.value))
        
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Score Types", SystemModule.SCORING.value, "scoretypes", 1, True, Resource.SCORE_TYPES.value,
                                                 ResourceType.URL.value, scoring_setup_id, Resource.SCORING_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))

        resources.append(SystemResourceViewModel(uuid.uuid4(), "Credit Houses", SystemModule.SCORING.value, "credithouses", 2, True, Resource.CREDIT_HOUSE.value,
                                                 ResourceType.URL.value, scoring_setup_id, Resource.SCORING_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))

        resources.append(SystemResourceViewModel(uuid.uuid4(), "Credit Type", SystemModule.SCORING.value, "credittypes", 3, True, Resource.CREDIT_TYPE.value,
                                                 ResourceType.URL.value, scoring_setup_id, Resource.SCORING_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))

        resources.append(SystemResourceViewModel(uuid.uuid4(), "Credit Reports", SystemModule.SCORING.value, "creditreports", 4, True, Resource.CREDIT_REPORT_PAYMENTS.value,
                                                 ResourceType.URL.value, scoring_setup_id, Resource.SCORING_SETUP.value, Perm.READ.value ))


        resources.append(SystemResourceViewModel(uuid.uuid4(), "Score Category", SystemModule.SCORING.value, "scorecategory", 7, True, Resource.SCORE_CATEGORIES.value,
                                                 ResourceType.URL.value, scoring_setup_id, Resource.SCORING_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Score Chart", SystemModule.SCORING.value, "scorechart", 8, True, Resource.SCORE_CARDS.value,
                                                 ResourceType.URL.value, scoring_setup_id, Resource.SCORING_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))

        resources.append(SystemResourceViewModel(uuid.uuid4(), "Settings", SystemModule.SCORING.value, "scoringsettings", 9, True, Resource.SCORING_SETTINGS.value,
                                                 ResourceType.URL.value, scoring_setup_id, Resource.SCORING_SETUP.value, Perm.READ.value | Perm.UPDATE.value))

        return resources

    #endregion

    #region Sacco Resources
    
    @staticmethod
    def get_sacco_resources():
        resources = list()
        sacco_id = uuid.uuid4()
        sacco_setup_id = uuid.uuid4()
        loan_setup_id = uuid.uuid4()
        interest_setup_id = uuid.uuid4()
        fine_setup_id = uuid.uuid4()
        unallocated_setup_id = uuid.uuid4()

        resources.append(SystemResourceViewModel(sacco_id, "Credit Management", SystemModule.SACCO.value,
                                                 "sacco", 7, True, Resource.SACCO.value, ResourceType.CONTAINER.value, None, None, Perm.READ.value))
      
        resources.append(SystemResourceViewModel(sacco_setup_id, "Credit Setup", SystemModule.SACCO.value, "creditsetup", 1, True,
                                                 Resource.SACCO_SETUP.value, ResourceType.CONTAINER.value, sacco_id, Resource.SACCO.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Credit Settings", SystemModule.SACCO.value, "creditsettings", 2, True,
                                                 Resource.SACCO_SETTINGS.value, ResourceType.URL.value, sacco_setup_id, Resource.SACCO_SETUP.value, Perm.READ.value | Perm.UPDATE.value ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Charges", SystemModule.SACCO.value, "charges", 3, True,
                                                 Resource.CHARGES.value, ResourceType.URL.value, sacco_setup_id, Resource.SACCO_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))


        resources.append(SystemResourceViewModel(loan_setup_id, "Loans", SystemModule.SACCO.value, "loans", 2, True,
                                                 Resource.LOANS.value, ResourceType.CONTAINER.value, sacco_id, Resource.SACCO.value, Perm.READ.value ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Loan Types", SystemModule.SACCO.value, "loantypes", 1, True,
                                                 Resource.LOAN_TYPES.value, ResourceType.URL.value, loan_setup_id, Resource.LOANS.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value | Perm.LOCK.value | Perm.UNLOCK.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Loan Lists", SystemModule.SACCO.value, "loanlists", 2, True,
                                                 Resource.LOAN_LISTS.value, ResourceType.URL.value, loan_setup_id, Resource.LOANS.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.APPROVE.value | Perm.POST.value | Perm.CANCEL.value | Perm.TRANSFER.value | Perm.UNAPPLY.value | Perm.VOID.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Loan Repayment", SystemModule.SACCO.value, "loanrepayments", 3, True,
                                                 Resource.LOAN_REPAYMENTS.value, ResourceType.URL.value, loan_setup_id, Resource.LOANS.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.APPROVE.value | Perm.CANCEL.value | Perm.VOID.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Cancelled Loans", SystemModule.SACCO.value, "cancelledloans", 4, True,
                                                 Resource.CANCELLED_LOANS.value, ResourceType.URL.value, loan_setup_id, Resource.LOANS.value, Perm.READ.value | Perm.CREATE.value))



        # resources.append(SystemResourceViewModel(uuid.uuid4(), "Loan Fees", SystemModule.SACCO.value, "loanfees", 4, False,
        #                                          Resource.LOAN_FEES.value, ResourceType.URL.value, loan_setup_id, Resource.LOANS.value, Perm.READ.value))

       
        resources.append(SystemResourceViewModel(fine_setup_id, "Fine", SystemModule.SACCO.value, "fine", 3, True,
                                                 Resource.FINE.value, ResourceType.CONTAINER.value, sacco_id, Resource.SACCO.value, Perm.READ.value))

        resources.append(SystemResourceViewModel(uuid.uuid4(), "Loan Fines", SystemModule.SACCO.value, "loanfines", 1, True,
                                                 Resource.LOAN_FINE.value, ResourceType.URL.value, fine_setup_id, Resource.FINE.value, Perm.READ.value))

      #  resources.append(SystemResourceViewModel(uuid.uuid4(), "Fine Payments", SystemModule.SACCO.value, "finepayments", 2, False,
        #                                          Resource.FINE_PAYMENT.value, ResourceType.URL.value, fine_setup_id, Resource.FINE.value, Perm.READ.value))

        # resources.append(SystemResourceViewModel(uuid.uuid4(), "Loans Rollover Fees", SystemModule.SACCO.value, "loanrollover", 3, False,
        #                                           Resource.ROLLOVER.value, ResourceType.URL.value, fine_setup_id, Resource.FINE.value, Perm.READ.value))
        # resources.append(SystemResourceViewModel(uuid.uuid4(), "Rollover Fees Payments", SystemModule.SACCO.value, "rolloverpayment", 4, False,
        #                                          Resource.ROLLOVER_PAYMENT.value, ResourceType.URL.value, fine_setup_id, Resource.FINE.value, Perm.READ.value))

        # Interest

        resources.append(SystemResourceViewModel(interest_setup_id, "Interest", SystemModule.SACCO.value, "interest", 3, False,
                                                 Resource.INTEREST.value, ResourceType.CONTAINER.value, sacco_id, Resource.SACCO.value, Perm.READ.value))

        # resources.append(SystemResourceViewModel(uuid.uuid4(), "Loan Interest", SystemModule.SACCO.value, "loaninterest", 1, False,
        #                                          Resource.LOAN_INTEREST.value, ResourceType.URL.value, interest_setup_id, Resource.INTEREST.value, Perm.READ.value | Perm.PROCESS.value))
       
        resources.append(SystemResourceViewModel(uuid.uuid4(),"Accrued Interest Batches",SystemModule.SACCO.value,"accruedinterestbatches",1,False,
                                                Resource.ACCRUED_INTEREST_BATCHES.value,ResourceType.URL.value,interest_setup_id,Resource.INTEREST.value,Perm.READ.value | Perm.PROCESS.value))
                                                
        # resources.append(SystemResourceViewModel(uuid.uuid4(), "Interest Payment", SystemModule.SACCO.value, "interestpayment", 2, False,
        #                                          Resource.INTEREST_PAYMENT.value, ResourceType.URL.value, interest_setup_id, Resource.INTEREST.value, Perm.READ.value))

        #savings/collections
        resources.append(SystemResourceViewModel(unallocated_setup_id, "Unallocated Fund", SystemModule.SACCO.value, "unallocatedfund", 5, True,
                                                 Resource.UNALLOCATEDFUND.value, ResourceType.CONTAINER.value, sacco_id, Resource.SACCO.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Unallocated Funds", SystemModule.SACCO.value, "unalocatedfunds", 1, True,
                                                 Resource.UNALLOCATED_DEPOSIT.value, ResourceType.URL.value, unallocated_setup_id, Resource.UNALLOCATEDFUND.value, Perm.READ.value))

        resources.append(SystemResourceViewModel(uuid.uuid4(), "Stray Deposits", SystemModule.SACCO.value, "straydeposits", 2, True,
                                                 Resource.STRAY_DEPOSIT.value, ResourceType.URL.value, unallocated_setup_id, Resource.UNALLOCATEDFUND.value, Perm.READ.value))


        return resources
    
    #endregion

    #region Client Resources
    
    @staticmethod
    def get_client_resources():
        resources = list()
        client_id = uuid.uuid4()

        client_setup_id = uuid.uuid4()
        activities = uuid.uuid4()

        resources.append(SystemResourceViewModel(client_id, "Client", SystemModule.CLIENT.value,
                                                 "client", 6, True, Resource.CLIENT.value, ResourceType.CONTAINER.value, None, None, Perm.READ.value))

        resources.append(SystemResourceViewModel(activities, "Activities", SystemModule.CLIENT.value, "activities", 1, True,
                                                 Resource.ACTIVITIES.value, ResourceType.CONTAINER.value, client_id, Resource.CLIENT.value, Perm.READ.value))

        resources.append(SystemResourceViewModel(uuid.uuid4(), "Apply Loan", SystemModule.CLIENT.value, "applyloan", 2, True, Resource.APPLY_LOAN.value,
                                                 ResourceType.URL.value, activities, Resource.ACTIVITIES.value, Perm.READ.value | Perm.CREATE.value
                                                 ))

        resources.append(SystemResourceViewModel(uuid.uuid4(), "Loan Statement", SystemModule.CLIENT.value, "statement", 3, True, Resource.STATEMENT.value,
                                                 ResourceType.URL.value, activities, Resource.ACTIVITIES.value, Perm.READ.value
                                                 ))

        resources.append(SystemResourceViewModel(uuid.uuid4(), "Credit Report", SystemModule.CLIENT.value, "creditreport", 4, True, Resource.CREDIT_REPORT.value,
                                                 ResourceType.URL.value, activities, Resource.ACTIVITIES.value, Perm.READ.value | Perm.CREATE.value
                                                 ))

        resources.append(SystemResourceViewModel(uuid.uuid4(), "Upgrade Account", SystemModule.CLIENT.value, "upgradeaccount", 5, True, Resource.UPGRADE_ACCOUNT.value,
                                                 ResourceType.URL.value, activities, Resource.ACTIVITIES.value, Perm.READ.value | Perm.CREATE.value
                                                 ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "My Loans", SystemModule.CLIENT.value, "loanlist", 6, True, Resource.CLIENT_LOAN_LIST.value,
                                                 ResourceType.URL.value, activities, Resource.ACTIVITIES.value, Perm.READ.value
                                                 ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Logs", SystemModule.CLIENT.value, "logs", 6, True, Resource.ERROR_LOGGER.value,
                                                 ResourceType.URL.value, activities, Resource.ACTIVITIES.value, Perm.READ.value
                                                 ))


        resources.append(SystemResourceViewModel(client_setup_id, "Client Setup", SystemModule.CLIENT.value, "clientsetup", 2, True,
                                                 Resource.CLIENT_SETUP.value, ResourceType.CONTAINER.value, client_id, Resource.CLIENT.value, Perm.READ.value))

        resources.append(SystemResourceViewModel(uuid.uuid4(), "Profile", SystemModule.CLIENT.value, "profile", 1, True, Resource.CLIENT_PROFILE.value,
                                                 ResourceType.URL.value, client_setup_id, Resource.CLIENT_SETUP.value, Perm.READ.value | Perm.CREATE.value
                                                 ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Next Of Kin", SystemModule.CLIENT.value, "nextofkin", 2, True, Resource.NEXT_OF_KIN.value,
                                                 ResourceType.URL.value, client_setup_id, Resource.CLIENT_SETUP.value, Perm.READ.value | Perm.CREATE.value
                                                 ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Bank Details", SystemModule.CLIENT.value, "bankdetails", 3, True, Resource.BANK_DETAILS.value,
                                                 ResourceType.URL.value, client_setup_id, Resource.CLIENT_SETUP.value, Perm.READ.value | Perm.CREATE.value
                                                 ))

        return resources

    #endregion
    
    #region BP Resources
    
    @staticmethod
    def get_bp_resources():
        resources = list()
        bp_id = uuid.uuid4()
        bp_setup_id = uuid.uuid4()

        resources.append(SystemResourceViewModel(bp_id, "Business Partners", SystemModule.BP.value,
                                                 "bp", 3, True, Resource.BUSINESSPARTNER.value, ResourceType.CONTAINER.value,  None, None, Perm.READ.value))
        resources.append(SystemResourceViewModel(bp_setup_id, "BP Setup", SystemModule.BP.value, "bpsetup", 1, True,
                                                 Resource.BP_SETUP.value, ResourceType.CONTAINER.value, bp_id, Resource.BUSINESSPARTNER.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "BP Types", SystemModule.BP.value, "bptypes", 1, True, Resource.BP_TYPES.value,
                                                 ResourceType.URL.value, bp_setup_id, Resource.BP_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "BP Groups", SystemModule.BP.value, "bpgroups", 3, True, Resource.BP_GROUPS.value,
                                                 ResourceType.URL.value, bp_setup_id, Resource.BP_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Business Partners", SystemModule.BP.value, "businesspartners", 3, True, Resource.BUSINESS_PARTNERS.value,
                                                 ResourceType.URL.value, bp_id, Resource.BUSINESSPARTNER.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))
              
        return resources
    
    #endregion

    #region AP Resources
    
    @staticmethod
    def get_ap_resources():
        resources = list()
        ap_id = uuid.uuid4()
        bill_id = uuid.uuid4()
        ap_payment_id = uuid.uuid4()
        exp_id = uuid.uuid4()

        resources.append(SystemResourceViewModel(ap_id, "Accounts Payables", SystemModule.AP.value,
                                                 "ap", 6, True, Resource.ACCOUNTS_PAYABLES.value, ResourceType.CONTAINER.value,  None, None, Perm.READ.value))

        resources.append(SystemResourceViewModel(bill_id, "Bills", SystemModule.AP.value, "bill", 1, True,
                                                 Resource.BILL_CONT.value, ResourceType.CONTAINER.value, ap_id, Resource.ACCOUNTS_PAYABLES.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Bills", SystemModule.AP.value, "bills", 1, True, Resource.BILLS.value,
                                                 ResourceType.URL.value, bill_id, Resource.BILL_CONT.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.VOID.value))

        resources.append(SystemResourceViewModel(ap_payment_id, "AP Payments", SystemModule.AP.value, "appayment", 3, True,
                                                 Resource.AP_PAYMENTS.value, ResourceType.CONTAINER.value, ap_id, Resource.ACCOUNTS_PAYABLES.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Pay Bill", SystemModule.AP.value, "paybill", 1, True, Resource.PAY_BILLS.value,
                                                 ResourceType.URL.value, ap_payment_id, Resource.AP_PAYMENTS.value, Perm.READ.value | Perm.CREATE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Payments", SystemModule.AP.value, "payments", 3, True, Resource.PAYMENTS.value,
                                                 ResourceType.URL.value, ap_payment_id, Resource.AP_PAYMENTS.value, Perm.READ.value | Perm.UPDATE.value))

        resources.append(SystemResourceViewModel(exp_id, "Expenditure", SystemModule.AP.value, "expenditure", 5, True,
                                                 Resource.EXPENDITURE.value, ResourceType.CONTAINER.value, ap_id, Resource.ACCOUNTS_PAYABLES.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Expenses", SystemModule.AP.value, "expenses", 1, True, Resource.AP_EXPENSES.value,
                                                 ResourceType.URL.value, exp_id, Resource.EXPENDITURE.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.VOID.value))

        return resources
    # endregion


    #region HR Resources 
    
    @staticmethod
    def get_hr_resources():
        resources = list()
        hr_id = uuid.uuid4()
        payroll_setup_id = uuid.uuid4()
        employee_setup_id = uuid.uuid4()
        payroll_tables_id = uuid.uuid4()
        payroll_processing_id = uuid.uuid4()
        salary_advance_id = uuid.uuid4()

        resources.append(SystemResourceViewModel(hr_id, "HR", SystemModule.HR.value,
                                                "hr", 11, True, Resource.HUMAN_RESOURCE.value, ResourceType.CONTAINER.value,  None, None, Perm.READ.value))

        resources.append(SystemResourceViewModel(payroll_setup_id, "Payroll Setup", SystemModule.HR.value, "payrollsetup", 1, True,
                                                Resource.PAYROLL_SETUP.value, ResourceType.CONTAINER.value, hr_id, Resource.HUMAN_RESOURCE.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Payroll Settings", SystemModule.HR.value, "payrollsettings", 1, True, Resource.PAYROLL_SETTINGS.value,
                                                ResourceType.URL.value, payroll_setup_id, Resource.PAYROLL_SETUP.value, Perm.READ.value | Perm.UPDATE.value ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Costing Centers", SystemModule.HR.value, "costingcenters", 3, True, Resource.COSTING_CENTERS.value,
                                                ResourceType.URL.value, payroll_setup_id, Resource.PAYROLL_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Payroll Items", SystemModule.HR.value, "payrollitems", 5, True, Resource.PAYROLL_ITEMS.value,
                                                ResourceType.URL.value, payroll_setup_id, Resource.PAYROLL_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Payroll Years", SystemModule.HR.value, "payrollyears", 7, True, Resource.PAYROLL_YEARS.value,
                                                ResourceType.URL.value, payroll_setup_id, Resource.PAYROLL_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Employee Pay Types", SystemModule.HR.value, "employeepaytypes", 9, True, Resource.EMPLOYEE_PAY_TYPES.value,
                                                ResourceType.URL.value, payroll_setup_id, Resource.PAYROLL_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.DELETE.value))
        
        resources.append(SystemResourceViewModel(employee_setup_id, "Employee Setup", SystemModule.HR.value, "employeesetup", 3, True,
                                                Resource.EMPLOYEE_SETUP.value, ResourceType.CONTAINER.value, hr_id, Resource.HUMAN_RESOURCE.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Employees", SystemModule.HR.value, "employees", 1, True, Resource.EMPLOYEES.value,
                                                ResourceType.URL.value, employee_setup_id, Resource.EMPLOYEE_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.LOCK.value | Perm.UNLOCK.value ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Employee Types", SystemModule.HR.value, "employeetypes", 3, True, Resource.EMPLOYEE_TYPES.value,
                                                ResourceType.URL.value, employee_setup_id, Resource.EMPLOYEE_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value  ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Salutations", SystemModule.HR.value, "salutations", 5, True, Resource.SALUTATIONS.value,
                                                ResourceType.URL.value, employee_setup_id, Resource.EMPLOYEE_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value  ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Job Titles", SystemModule.HR.value, "jobtitles", 7, True, Resource.JOB_TITLES.value,
                                                ResourceType.URL.value, employee_setup_id, Resource.EMPLOYEE_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value  ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Marital Statuses", SystemModule.HR.value, "maritalstatuses", 9, True, Resource.MARITAL_STATUSES.value,
                                                ResourceType.URL.value, employee_setup_id, Resource.EMPLOYEE_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value  ))

        resources.append(SystemResourceViewModel(payroll_tables_id, "Payroll Tables", SystemModule.HR.value, "payrolltables", 5, True,
                                                Resource.PAYROLL_TABLES.value, ResourceType.CONTAINER.value, hr_id, Resource.HUMAN_RESOURCE.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Paye Tax Tables", SystemModule.HR.value, "payetaxtables", 1, True, Resource.PAYE_TAX_TABLES.value,
                                                ResourceType.URL.value, payroll_tables_id, Resource.PAYROLL_TABLES.value, Perm.READ.value | Perm.UPDATE.value  ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "NHIF Tables", SystemModule.HR.value, "nhiftables", 3, True, Resource.NHIF_TABLES.value,
                                                ResourceType.URL.value, payroll_tables_id, Resource.PAYROLL_TABLES.value, Perm.READ.value | Perm.UPDATE.value  ))

        resources.append(SystemResourceViewModel(payroll_processing_id, "Payroll Processing", SystemModule.HR.value, "payrollprocessing", 7, True,
                                                Resource.PAYROLL_PROCESSING.value, ResourceType.CONTAINER.value, hr_id, Resource.HUMAN_RESOURCE.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Payroll Processes", SystemModule.HR.value, "payrollprocesses", 1, True, Resource.PAYROLL_PROCESSES.value,
                                                ResourceType.URL.value, payroll_processing_id, Resource.PAYROLL_PROCESSING.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.APPROVE.value | Perm.UNAPPROVE.value | Perm.CANCEL.value ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Employee Payments", SystemModule.HR.value, "employeepayments", 3, True, Resource.EMPLOYEE_PAYMENTS.value,
                                                ResourceType.URL.value, payroll_processing_id, Resource.PAYROLL_PROCESSING.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value  ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Liability Payments", SystemModule.HR.value, "liabilitypayments", 5, True, Resource.LIABILITY_PAYMENTS.value,
                                                ResourceType.URL.value, payroll_processing_id, Resource.PAYROLL_PROCESSING.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value  ))

        resources.append(SystemResourceViewModel(salary_advance_id, "Salary Advance", SystemModule.HR.value, "salaryadvance", 9, True,
                                                Resource.SALARY_ADVANCE.value, ResourceType.CONTAINER.value, hr_id, Resource.HUMAN_RESOURCE.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Salary Advances", SystemModule.HR.value, "salaryadvances", 1, True, Resource.SALARY_ADVANCES.value,
                                                ResourceType.URL.value, salary_advance_id, Resource.SALARY_ADVANCE.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value | Perm.APPROVE.value | Perm.UNAPPROVE.value | Perm.CANCEL.value  ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Salary Advance Disbursements", SystemModule.HR.value, "salaryadvancedisbursements", 3, True, Resource.SALARY_ADVANCE_DISBURSEMENTS.value,
                                                ResourceType.URL.value, salary_advance_id, Resource.SALARY_ADVANCE.value, Perm.READ.value | Perm.CREATE.value   ))

        return resources
    # endregion
    
    #region Reporting Resources
    
    @staticmethod
    def get_reporting_resources():
        resources = list()
        reporting_id = uuid.uuid4()
        resources.append(SystemResourceViewModel(reporting_id, "Reporting", SystemModule.REPORTING.value,
                                                 "reporting", 21, True, Resource.REPORTING.value, ResourceType.CONTAINER.value,  None, None, Perm.READ.value))
        
        #region Finance Reports
        
        finance_reporting_id = uuid.uuid4()

        resources.append(SystemResourceViewModel(finance_reporting_id, "Financials", SystemModule.REPORTING.value, "financials", 1, True,
                                                 Resource.FINANCE_REPORTS.value, ResourceType.CONTAINER.value, reporting_id, Resource.REPORTING.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Balance Sheet", SystemModule.REPORTING.value, "balancesheet", 1, True, Resource.BALANCE_SHEET_RPT.value,
                                                 ResourceType.URL.value, finance_reporting_id, Resource.FINANCE_REPORTS.value, Perm.READ.value ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Trial Balance", SystemModule.REPORTING.value, "trialbalance", 3, True, Resource.TRIAL_BALANCE_RPT.value,
                                                 ResourceType.URL.value, finance_reporting_id, Resource.FINANCE_REPORTS.value, Perm.READ.value ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Income Statement", SystemModule.REPORTING.value, "incomestatement", 5, True, Resource.INCOME_STATEMENT_RPT.value,
                                                 ResourceType.URL.value, finance_reporting_id, Resource.FINANCE_REPORTS.value, Perm.READ.value ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Working Capital", SystemModule.REPORTING.value, "workingcapital", 7, True, Resource.WORKING_CAPITAL_RPT.value,
                                                 ResourceType.URL.value, finance_reporting_id, Resource.FINANCE_REPORTS.value, Perm.ZERO.value ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Cash Flow", SystemModule.REPORTING.value, "cashflow", 9, True, Resource.CASH_FLOW_RPT.value,
                                                 ResourceType.URL.value, finance_reporting_id, Resource.FINANCE_REPORTS.value, Perm.ZERO.value ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Account Statement", SystemModule.REPORTING.value, "accountstatement", 11, True, Resource.ACCOUNT_STATEMENT_RPT.value,
                                                 ResourceType.URL.value, finance_reporting_id, Resource.FINANCE_REPORTS.value, Perm.READ.value ))
              
        #endregion
        
        return resources
    
    # endregion




    # start crm region
    @staticmethod
    def get_crm_resources():
        resources = list()
        crm_resource_id = uuid.uuid4()
        crm_setup_id = uuid.uuid4()
        messenger_id = uuid.uuid4()
        blogger_id = uuid.uuid4()
        ticketing_id = uuid.uuid4()

        resources.append(SystemResourceViewModel(crm_resource_id, "CRM", SystemModule.CRM.value,
                                                 "crm", 8, True, Resource.CRM.value, ResourceType.CONTAINER.value,  None, None, Perm.READ.value))

        resources.append(SystemResourceViewModel(crm_setup_id, "CRM Setup", SystemModule.CRM.value, "crmsetup", 1, True,
                                                 Resource.CRM_SETUP.value, ResourceType.CONTAINER.value, crm_resource_id, Resource.CRM.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Crm Settings", SystemModule.CRM.value, "crmsettings", 2, True, Resource.CRM_SETTINGS.value,
                                                 ResourceType.URL.value, crm_setup_id, Resource.CRM_SETUP.value, Perm.READ.value | Perm.CREATE.value | Perm.UPDATE.value))

        resources.append(SystemResourceViewModel(messenger_id, "Messenger", SystemModule.CRM.value, "messenger", 2, True,
                                                 Resource.MESSENGER.value, ResourceType.CONTAINER.value, crm_resource_id, Resource.CRM.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Messaging", SystemModule.CRM.value, "messaging", 1, True, Resource.MESSAGING.value,
                                                 ResourceType.URL.value, messenger_id, Resource.MESSENGER.value, Perm.READ.value | Perm.CREATE.value))

        resources.append(SystemResourceViewModel(uuid.uuid4(), "Message Templates", SystemModule.CRM.value, "templates", 2, True, Resource.MESSAGE_TEMPLATES.value,
                                                 ResourceType.URL.value, messenger_id, Resource.MESSENGER.value, Perm.READ.value | Perm.CREATE.value))

        resources.append(SystemResourceViewModel(uuid.uuid4(), "Message Policy Days", SystemModule.CRM.value, "messagepolicydays", 3, True, Resource.MESSAGE_POLICY_DAYS.value,
                                                 ResourceType.URL.value, messenger_id, Resource.MESSENGER.value, Perm.READ.value | Perm.CREATE.value))


        resources.append(SystemResourceViewModel(uuid.uuid4(), "Sender IDs", SystemModule.CRM.value, "senderid", 5, True, Resource.SENDERID.value,
                                                 ResourceType.URL.value, messenger_id, Resource.MESSENGER.value, Perm.READ.value ))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Groups", SystemModule.CRM.value, "groups", 6, True,
                                                 Resource.GROUPS.value, ResourceType.URL.value, messenger_id, Resource.MESSENGER.value, Perm.READ.value | Perm.CREATE.value))
        
        resources.append(SystemResourceViewModel(blogger_id, "Blogger", SystemModule.CRM.value, "blogging", 3, True,
                                                  Resource.BLOGGER.value, ResourceType.CONTAINER.value, crm_resource_id, Resource.CRM.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "blogging", SystemModule.CRM.value, "blogs", 1, True, Resource.BLOGGING.value,
                                                 ResourceType.URL.value, blogger_id, Resource.BLOGGER.value, Perm.READ.value | Perm.CREATE.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "Categories", SystemModule.CRM.value, "categories", 2, True, Resource.BLOG_CATEGORIES.value,
                                                 ResourceType.URL.value, blogger_id, Resource.BLOGGER.value, Perm.READ.value | Perm.CREATE.value))



        resources.append(SystemResourceViewModel(ticketing_id, "Ticketing", SystemModule.CRM.value, "ticketing", 4, True,
                                                 Resource.TICKETING.value, ResourceType.CONTAINER.value, crm_resource_id, Resource.CRM.value, Perm.READ.value))
        resources.append(SystemResourceViewModel(uuid.uuid4(), "tickets", SystemModule.CRM.value, "tickets", 1, True, Resource.TICKETS.value,
                                                 ResourceType.URL.value, ticketing_id, Resource.TICKETING.value, Perm.READ.value | Perm.CREATE.value))

        return resources
