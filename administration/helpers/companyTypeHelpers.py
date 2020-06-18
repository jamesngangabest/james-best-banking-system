from administration.models.administration import CompanyType
from administration.models.resourceEnums import CompanyTypes, Resource
from administration.models.authorization import GlobalResource, CompanyTypeResource


class CompanyTypeHelper:

    @staticmethod
    def create(company_type):
        print("company type ", company_type)
        if company_type == CompanyTypes.MICROFINANCE.value:

            CompanyTypeHelper.create_microfinance()

    @staticmethod
    def create_microfinance():
        if CompanyType.objects.filter(id=CompanyTypes.MICROFINANCE.value).exists():
            pass
        else:
            ct = CompanyType(id=CompanyTypes.MICROFINANCE.value,
                             name='Micro-Finance')
            ct.save()
        resources = CompanyTypeHelper.getMicroFinanceResources()
        print("preparing to create...")
        # print(resources)
        CompanyTypeHelper.create_resources(
            CompanyTypes.MICROFINANCE.value, resources)

    @staticmethod
    def create_resources(companyTypeId, resources):
        print(resources)
        for item in resources:
            print('Resource', item['resource'])
            try:
                gResource = GlobalResource.objects.get(
                    resource=item['resource'])
                try:
                    #tobj= CompanyTypeResource.objects.filter(company_type__id=companyTypeId, resource__resource=item['resource'])
                    #print("Count: ", len(tobj))
                    print("Resource (", item['resource'], ') to be updated')

                    cResource = CompanyTypeResource.objects.get(
                        company_type__id=companyTypeId, resource__resource=item['resource'])
                    #print("Resource (", item['resource'], ') to be updated')
                except CompanyTypeResource.DoesNotExist:
                    #print("Resource (", item['resource'], ') to be created')
                    cResource = CompanyTypeResource()
                    cResource.resource = gResource
                    cResource.company_type_id = companyTypeId
                except Exception as e:
                    print(e)
                    pass

                cResource.name = gResource.name
                cResource.permission = gResource.permission
                cResource.display_order = gResource.display_order
                cResource.is_active = gResource.is_active

                # create/update
                cResource.save()

            except GlobalResource.DoesNotExist:
                print('Global Resource (', item.resource, ') not yet created')
            except Exception as e:
                print(e)

    @staticmethod
    def getMicroFinanceResources():
        resources = []

        # administration

        resources.append({'resource': Resource.ADMINISTRATION.value})
        resources.append({'resource': Resource.COMPANY_SETUP.value})
        resources.append({'resource': Resource.COMPANIES.value})
        resources.append({'resource': Resource.COMPANY_DETAILS.value})
        resources.append({'resource': Resource.DEFAULT_SETTINGS.value})
        resources.append({'resource': Resource.COUNTIES.value})
    #    resources.append({'resource': Resource.SUB_COUNTIES.value})

        resources.append({'resource': Resource.SCHOOLS.value})
        resources.append({'resource': Resource.TEACHERS.value})

        resources.append({'resource': Resource.BANKS.value})
        resources.append({'resource': Resource.ADMIN_ERROR_LOGGER.value})
      #   resources.append({'resource': Resource.BRANCHES.value})

        resources.append({'resource': Resource.SECURITY_SETUP.value})
        resources.append({'resource': Resource.USERS.value})
        resources.append({'resource': Resource.ROLES.value})
        resources.append({'resource': Resource.RESOURCES_UPDATE.value})

        resources.append({'resource': Resource.ROLE_PERMISSIONS.value})

        # Financials
        resources.append({'resource': Resource.FINANCIALS.value})
        resources.append({'resource': Resource.LEDGER_SETUP.value})
        resources.append({'resource': Resource.ACCOUNT_TYPES.value})

        resources.append({'resource': Resource.TRANSACTION_TYPES.value})
        resources.append({'resource': Resource.PAYMENT_METHODS.value})
        resources.append({'resource': Resource.PAYMENT_TERMS.value})
        resources.append({'resource': Resource.RESPONSIBILITY_CENTERS.value})

        resources.append({'resource': Resource.GENERAL_LEDGER.value})
        resources.append({'resource': Resource.LEDGER_ACCOUNTS.value})
        resources.append({'resource': Resource.FISCAL_YEARS.value})
        resources.append({'resource': Resource.FISCAL_YEAR_CLOSING.value})
        resources.append({'resource': Resource.LEDGER_TRANSACTIONS.value})

        resources.append({'resource': Resource.BANKING.value})
        resources.append({'resource': Resource.BANKING_SETUP.value})
        resources.append({'resource': Resource.BANK_RECON_ADJ_CATEGORIES.value})
        resources.append({'resource': Resource.BANK_TRANSACTIONS.value})
        resources.append({'resource': Resource.BANK_RECONCILIATIONS.value})
        resources.append({'resource': Resource.BANK_RECON_RESOLUTIONS.value})
        resources.append({'resource': Resource.PENDING_RECON_ITEMS.value})

        # scoring
        resources.append({'resource': Resource.SCORING.value})
        resources.append({'resource': Resource.SCORING_SETUP.value})
        resources.append({'resource': Resource.SCORE_TYPES.value})
        resources.append({'resource': Resource.SCORE_CARDS.value})
        resources.append({'resource': Resource.CREDIT_REPORT_PAYMENTS.value})
        resources.append({'resource': Resource.SCORE_CATEGORIES.value})
        resources.append({'resource': Resource.SCORING_SETTINGS.value})
        
        resources.append({'resource': Resource.CREDIT_HOUSE.value})
        resources.append({'resource': Resource.CREDIT_TYPE.value})
        # sacco
        resources.append({'resource': Resource.SACCO.value})
        resources.append({'resource': Resource.SACCO_SETUP.value})
        resources.append({'resource': Resource.SACCO_SETTINGS.value})
        resources.append({'resource': Resource.CHARGES.value})

        resources.append({'resource': Resource.LOANS.value})
        resources.append({'resource': Resource.LOAN_LISTS.value})
        resources.append({'resource': Resource.LOAN_TYPES.value})
        resources.append({'resource': Resource.LOAN_REPAYMENTS.value})
        resources.append({'resource': Resource.CANCELLED_LOANS.value})

      #  resources.append({'resource': Resource.LOAN_FEES.value})
        resources.append({'resource': Resource.INTEREST.value})
        resources.append({'resource':Resource.ACCRUED_INTEREST_BATCHES.value})

      #  resources.append({'resource': Resource.LOAN_INTEREST.value})
      #  resources.append({'resource': Resource.INTEREST_PAYMENT.value})
        resources.append({'resource': Resource.FINE.value})
        # resources.append({'resource': Resource.FINE_PAYMENT.value})
        # resources.append({'resource': Resource.LOAN_FINE.value})
        # resources.append({'resource': Resource.ROLLOVER.value})
        # resources.append({'resource': Resource.ROLLOVER_PAYMENT.value})
        resources.append({'resource': Resource.UNALLOCATEDFUND.value})
        resources.append({'resource': Resource.UNALLOCATED_DEPOSIT.value})
        resources.append({'resource': Resource.STRAY_DEPOSIT.value})

        # client
        resources.append({'resource': Resource.CLIENT.value})
        resources.append({'resource': Resource.ACTIVITIES.value})
        resources.append({'resource': Resource.STATEMENT.value})
        resources.append({'resource': Resource.APPLY_LOAN.value})
        resources.append({'resource': Resource.CREDIT_REPORT.value})
        resources.append({'resource': Resource.UPGRADE_ACCOUNT.value})
        resources.append({'resource': Resource.CLIENT_LOAN_LIST.value})
        resources.append({'resource': Resource.ERROR_LOGGER.value})

        resources.append({'resource': Resource.CLIENT_SETUP.value})
        resources.append({'resource': Resource.CLIENT_PROFILE.value})
        resources.append({'resource': Resource.NEXT_OF_KIN.value})
        resources.append({'resource': Resource.BANK_DETAILS.value})

        # BP
        resources.append({'resource': Resource.BUSINESSPARTNER.value})
        resources.append({'resource': Resource.BP_SETUP.value})
        resources.append({'resource': Resource.BP_GROUPS.value})
        resources.append({'resource': Resource.BP_TYPES.value})
        resources.append({'resource': Resource.BUSINESS_PARTNERS.value})

        # AP
        resources.append({'resource': Resource.ACCOUNTS_PAYABLES.value})
        resources.append({'resource': Resource.BILL_CONT.value})
        resources.append({'resource': Resource.BILLS.value})
        resources.append({'resource': Resource.AP_PAYMENTS.value})
        resources.append({'resource': Resource.PAY_BILLS.value})
        resources.append({'resource': Resource.PAYMENTS.value})
        resources.append({'resource': Resource.EXPENDITURE.value})
        resources.append({'resource': Resource.AP_EXPENSES.value})

        # HR
        resources.append({'resource': Resource.HUMAN_RESOURCE.value})
        resources.append({'resource': Resource.PAYROLL_SETUP.value})
        resources.append({'resource': Resource.COSTING_CENTERS.value})
        resources.append({'resource': Resource.PAYROLL_SETTINGS.value})
        resources.append({'resource': Resource.PAYROLL_ITEMS.value})
        resources.append({'resource': Resource.PAYROLL_YEARS.value})
        resources.append({'resource': Resource.EMPLOYEE_PAY_TYPES.value})

        resources.append({'resource': Resource.EMPLOYEE_SETUP.value})
        resources.append({'resource': Resource.EMPLOYEES.value})
        resources.append({'resource': Resource.EMPLOYEE_TYPES.value})
        resources.append({'resource': Resource.SALUTATIONS.value})
        resources.append({'resource': Resource.JOB_TITLES.value})
        resources.append({'resource': Resource.MARITAL_STATUSES.value})

        resources.append({'resource': Resource.PAYROLL_TABLES.value})
        resources.append({'resource': Resource.PAYE_TAX_TABLES.value})
        resources.append({'resource': Resource.NHIF_TABLES.value})

        resources.append({'resource': Resource.PAYROLL_PROCESSING.value})
        resources.append({'resource': Resource.PAYROLL_PROCESSES.value})
        resources.append({'resource': Resource.EMPLOYEE_PAYMENTS.value})
        resources.append({'resource': Resource.LIABILITY_PAYMENTS.value})

        resources.append({'resource': Resource.SALARY_ADVANCE.value})
        resources.append({'resource': Resource.SALARY_ADVANCES.value})
        resources.append({'resource': Resource.SALARY_ADVANCE_DISBURSEMENTS.value})

        # Reporting
        resources.append({'resource': Resource.REPORTING.value})

        resources.append({'resource': Resource.FINANCE_REPORTS.value})
        resources.append({'resource': Resource.BALANCE_SHEET_RPT.value})
        resources.append({'resource': Resource.TRIAL_BALANCE_RPT.value})
        resources.append({'resource': Resource.WORKING_CAPITAL_RPT.value})
        resources.append({'resource': Resource.INCOME_STATEMENT_RPT.value})
        resources.append({'resource': Resource.CASH_FLOW_RPT.value})
        resources.append({'resource': Resource.ACCOUNT_STATEMENT_RPT.value})

        #CRM
        resources.append({'resource': Resource.CRM.value})
        resources.append({'resource': Resource.CRM_SETUP.value})
        resources.append({'resource': Resource.CRM_SETTINGS.value})
        resources.append({'resource': Resource.MESSENGER.value})
        resources.append({'resource': Resource.MESSAGE_TEMPLATES.value})
        resources.append({'resource': Resource.MESSAGE_POLICY_DAYS.value})
        resources.append({'resource': Resource.MESSAGING.value})

        resources.append({'resource': Resource.SENDERID.value})
        resources.append({'resource': Resource.BLOGGER.value})
        resources.append({'resource': Resource.BLOGGING.value})
        resources.append({'resource': Resource.BLOG_CATEGORIES.value})
        resources.append({'resource': Resource.TICKETING.value})
        resources.append({'resource': Resource.TICKETS.value})




        return resources

        @staticmethod
        def PeerToPeerResources():
            resources = []

            # administration

            resources.append({'resource': Resource.ADMINISTRATION.value})
            resources.append({'resource': Resource.COMPANY_SETUP.value})
            resources.append({'resource': Resource.COMPANIES.value})
            resources.append({'resource': Resource.COMPANY_DETAILS.value})
            resources.append({'resource': Resource.DEFAULT_SETTINGS.value})
            resources.append({'resource': Resource.SECURITY_SETUP.value})
            resources.append({'resource': Resource.USERS.value})
            resources.append({'resource': Resource.ROLES.value})
            resources.append({'resource': Resource.RESOURCES_UPDATE.value})

            # Financials
            resources.append({'resource': Resource.FINANCIALS.value})
            resources.append({'resource': Resource.LEDGER_SETUP.value})
            resources.append({'resource': Resource.ACCOUNT_TYPES.value})



            return resources
