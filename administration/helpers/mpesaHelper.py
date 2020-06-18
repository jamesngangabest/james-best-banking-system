

class MpesaHandler:
    @staticmethod
    def getPaybill(systemCompany,tx):
         m=MPESAPIKeys.objects.filter(transaction_type=tx)
         print(m)
         return m.filter(api_type__paybill_number__company__id=systemCompany.id)   
    