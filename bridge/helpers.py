# from django.db.models import Q
#
# from AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException
#
import africastalking
from uuid import UUID
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient
from phonenumber_field.phonenumber import PhoneNumber
from bridge.errors import ErrorLogger
import random
import datetime
import pytz
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pyfcm import FCMNotification
from django.contrib.auth import get_user_model
from bridge.models.crmSettings import *
User = get_user_model()
import sys
import json
import csv
import os
import mimetypes
from administration.models.companySetting import CompanySetting
# from decimal import Decimal
# from django.db.models import Sum,F
username = "opalquick"
apikey   = "e93094d4e88f7f69345fd0d768544f9aae6407fe271d06aed8ee02294fc99322"
import logging
from .models import *

logger = logging.getLogger(__name__)
hdlr = logging.FileHandler('/tmp/django_dev.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

# # Create a new instance of our awesome gateway class
# gateway = AfricasTalkingGateway(username, apikey)
MAIL_ORIGIN="support@opalquick.co.ke"
from .errors import *

class ChannelResponseFail:
    def __init__(self, response):

        if not response:
           raise AppValidation('Response','Empty response',500)
        elif response['Result']['ResultCode'] == 2:
            ErrorLogger("MPESA B2C CALLBACK",response['Result']['ResultDesc'], response)

    def B2C_ERROR(self,response,loan=None):
        
        if "ResultCode" in response['Result']:
            if response['Result']['ResultCode'] == 2040:
                ErrorLogger("MPESA B2C CALLBACK",
                            response['Result']['ResultDesc'], response)
                raise AppValidation('Response', 'Empty response', 500)

            if response['Result']['ResultCode'] == 1:
                ErrorLogger("MPESA B2C CALLBACK",
                            response['Result']['ResultDesc'], response)
                #notify support
                msg= MyMessaging()
                obj=msg.getMessageTemplate("FUNDSALERT", loan[0].user.systemCompany,"S")
                msg.initMessaging({"channels":"S","phone":loan[0].user.systemCompany.phone,
                                    "message":obj.message
                                    })

                raise AppValidation('Response', 'Empty response', 500)
            if response['Result']['ResultCode'] == 2:
                ErrorLogger("MPESA B2C CALLBACK",
                        response['Result']['ResultDesc'], response)

class FileUploadHelper:
    def __init__(self,file_obj):
        print(file_obj.multiple_chunks())
        if not file_obj.name.endswith('.csv'):
                raise AppValidation(
                    "Unacceptable file format.Please upload a csv file", "File Format", status_code=400)
        if file_obj.multiple_chunks():
            raise AppValidation(
                "Uploaded file is too big " + str(file_obj.size/(1000*1000))+" Mb.Max allowable size is 20Mb", "File size", status_code=400)

        self.file_data = file_obj.read().decode("utf-8")
    
    def getfile(self):
        lines = self.file_data.split("\n")
        return lines
class MessagingModel:
    def storeMessage(self,payload):
        print(payload)
        return EmailMessage.objects.create(**payload)
    def storeEmailMessage(self,payload):
        print("StoreEmail")
        if "id" in payload:
            if  payload["id"]:
                self.updateMessage(payload)
            del payload["id"]
        return EmailMessage.objects.create(**payload)
    def checkDeplicate(self):
        pass
    def updateMessage(self,payload):
        if not payload['id']:
            del payload["id"]
            print ("hapa")
            EmailMessage.objects.create(**payload)
        else:
            em=EmailMessage.objects.filter(id=payload["id"].id)
            del payload["id"]
            print(payload)
            em.update(**payload)


class SMS:
    pass
class Email:
    pass
class GCM:
    pass

class MyMessaging:
    def __init__(self):
        self.msgm=MessagingModel()

    def initMessaging(self,payload):
        if payload['channels']=="ESG":
            self.sendEmailMessage(
                payload['to'], payload['from'], payload['subject'], payload['message'], payload['user'])

            #send to all 3 channels
        elif payload['channels']=="E": #email
           self.sendEmailMessage(payload['to'],payload['from'],payload['subject'],payload['message'],payload['user'])
        elif payload['channels']=="S": # sms
            pass
        elif payload['channels'] == "G": # GCM
            pass
    def getCompanySetting(self,company):
        return CompanySetting.objects.get(company=company)

    def getMessageTemplate(self,typ,company,message_type):
        # try:
        print(typ,company,message_type)
        return MessageTemplates.objects.get(typ=typ,company=company,message_type=message_type)
        # except:
        #     ErrorLogger(typ,"Message template does not exist.Code not sent",company)
            
#     def checkBalance(self):
#         try:
#             user = gateway.getUserData()
#             print "check sms balance every 6 hours dude"+user['balance']
#             if float(user['balance'].split(" ")[1])>100:
#                 pass
#             else:
#                 self.sendEmailAlert("support@opalquick.co.ke","mwendashammah@gmail.com","Courtesy balance .This stands at "+user['balance'],"SMS BALANCE STATEMENT")
#
#             return user['balance']
#     # The result will have the format=> KES XXX
#         except AfricasTalkingGatewayException, e:
#             print 'Error: %s' % str(e)
#             return str(e)
#
#     def sendEmailAlert(self,email1,email2,message,subject):
#         msg = MIMEMultipart()
#         msg['From'] = "support@opalquick.co.ke"
#         msg['To'] = email2
#         msg['Subject'] = subject
#
#
#         server = smtplib.SMTP('mailgateway-01.angani.co', 26)
#         # server.starttls()
#         #Next, log in to the server
#         #server.login("youremailusername", "password")
#         body= message
#         msg.attach(MIMEText(body, 'plain'))
#         text = msg.as_string()
#
#         #Send the mail
#          # The /n separates the message from the headers
#
#         server.sendmail(email2, "support@opalquick.co.ke", text)
    def getCrmSettingObj(self,company):
        return CrmSettings.objects.get(company=company)
    def sendEmailMessage(self,toaddr,fromaddr,subject,message,owner):
        msg=message
      
        crmSettingObj = self.getCrmSettingObj(owner.systemCompany)

        message = Mail(
            from_email=fromaddr,
            to_emails=toaddr,
            subject=subject,
            html_content=message)
        print(fromaddr,toaddr,subject,message)
        status_code=disable_flag=""
        try:
            #owner
            if not crmSettingObj.disable_email:
                sg = SendGridAPIClient(crmSettingObj.sendgrid_api_key)
                response = sg.send(message)
                status_code = response.status_code
            else:

                disable_flag="Simulated.GCM DISABLED"
                status_code="success"


            return self.msgm.storeEmailMessage({"message": msg, "subject": subject, "user": owner,
                                         "delivery_report": "Message sent "+str(status_code)+ " "+disable_flag, "origin":owner.systemCompany.support_email, "recipient": toaddr,
                                                "message_type": MessageTypes.email.value,
                                         })
        except Exception as e:
            return self.msgm.storeEmailMessage({"message": msg, "subject": subject, "user": owner,
                                                "delivery_report": e, "origin": owner.systemCompany.support_email, "recipient": toaddr,
                                                "message_type": MessageTypes.email.value,    
                                         })

    def getCompany(self,payload):
        if "company" in payload:
            return payload['company']
        else:
            print("cget com")
            return payload['id'].company

    def getSenderId(self,SaccoSetting):
        return SaccoSetting.message_policy_senderid.name

        
    def sendEmail(self,payload):
        user = payload['user']
        company=self.getCompany(payload)

        origin = payload['origin']
        toaddr = payload['to']
        subject = payload['subject']
        message = payload['message']
        id = payload["id"]
        
        crmSettingObj = self.getCrmSettingObj(company)

        message = Mail(
            from_email=origin,
            to_emails=toaddr,
            subject=subject,
            html_content=message)

        try:
            #owner
            print("here dude")

            status_code = disable_flag = ""
            if not crmSettingObj.disable_email:
                sg = SendGridAPIClient(crmSettingObj.sendgrid_api_key)
                response = sg.send(message)
                status_code = response.status_code
            else:
                status_code="202"
                disable_flag=" SMS DISABLED"

            return self.msgm.updateMessage({
                "delivery_report": "Message sent "+str(status_code)+disable_flag, "origin": origin, "recipient": toaddr,
                                                "message_type": MessageTypes.email.value, "id": id,
                                                })
        except Exception as e:
            return self.msgm.updateMessage({
                                                "delivery_report": e, "origin": origin, "recipient": toaddr,
                                                "message_type": MessageTypes.email.value, "id": id,
                                                
                                                })





        

    def gcm(self,data):
        
        #  key="AAAA6GCJxNk:APA91bEqVE9stEgeiGNPRsqDX2ou3EIqqhEv48RoTopuH6oAY7O-HoYTvi1O_wBPbu4FRBiw2eLgAlmnOL_QFvRFB2IiJ-YLS_5zkuxvbVleOaKFdCtMHbcekZygTDipxk-Xp_FcNT8_"
        user= data['user']
        company = self.getCompany(data)
        crmSettingObj = self.getCrmSettingObj(company)
        key = crmSettingObj.fcm_api_key
        push_service = FCMNotification(api_key=key)


        registration_id =data['token']
        message_title = data['subject']
        message_body = data['message']
        data_message={"title":message_title,"message":message_body}
        result=disable_flag=""
        if not  crmSettingObj.disable_gcm:
            try:
                result = push_service.notify_single_device(registration_id=registration_id,  message_body=message_body,data_message=data_message)
                print(result)
            except Exception  as e:
                raise AppValidation(e,status_code=400)
        else:
            disable_flag="Simulated.GCM DISABLED"
            result="success"

        if "success" in result:
            if int(result['success']) ==0:
                self.msgm.updateMessage({"id": data["id"],
                                         "gcm_delivery_report": "GCM Message sent "+disable_flag,
                                         "message_type": MessageTypes.gcm.value,
                                             })
            else:
                self.msgm.updateMessage({
                                            "gcm_delivery_report": "GCM Message NOT sent", "id": data["id"],
                                            "message_type": MessageTypes.gcm.value,
                                            })
                ErrorLogger("GCM MESSAGE DISPATCH","GCM Message has not been sent to Mobile",result,user=data['user'])
        else:
            self.msgm.updateMessage({
                                     "gcm_delivery_report": "GCM Message NOT sent", "id": data["id"],
                                     "message_type": MessageTypes.gcm.value,
                                     })
            ErrorLogger("GCM MESSAGE DISPATCH",
                        "GCM Message has not been sent to Mobile", result, user=data['user'])
    def deductCredits(self, payload):
        crm  = payload['crmSettingObj']
        crm.at_sms_counter = crm.at_sms_counter -1
        crm.save()
    def sendSMS(self,payload):

        to = payload['to']
        user= payload['user']
        company = self.getCompany(payload)
        message = payload['message']
        SENDERID = payload['senderid']
        print(SENDERID,company)
        crmSettingObj = self.getCrmSettingObj(company)

        africastalking.initialize(crmSettingObj.at_gateway_key_name, crmSettingObj.at_gateway_key)


# Initialize a service e.g. SMS
        sms = africastalking.SMS


        x = crmSettingObj.at_sms_counter

        if x < crmSettingObj.at_alert_counter:
           
            phone = company.phone
            status = x.smscounter_alert_sent
            if status:
                x.smscounter_alert_sent = True
                x.save()
    #            self.sendMessage({"phone": phone, "message": "Dear"+u.name+",Your sms are below "+str(x)+" units.Please buy more units and top up your Africastalking wallet","company":payload['companyObj']})
    
            else:
                pass
                #he has been alerted dude

            # Create a new instance of our awesome gateway class
        def on_finish(error, data):
            logger.info(error)
            logger.info(data) 
            print(error)
            print (type(error))
            if not error is None :
                print("I am in")
                print (None)

                self.msgm.updateMessage({"message":payload['message'],
                                         "id":payload["id"],
                                             "sms_delivery_report":error,
                                          "recipient": to, "message_type": MessageTypes.sms.value,
                                          "sms_error":data
                                             })

                return False
            else:
                d = data['SMSMessageData']['Recipients']
                for recipient in d:

                    #if message is larger by 1 part deduct bt(number of parts *1)
                    if recipient['status'] == "Success":
                        self.msgm.updateMessage({"message": payload['message'], 
                                                "id": payload["id"],
                                                "sms_delivery_report": "Message sent",
                                                 "recipient": to, "message_type": MessageTypes.sms.value,
                                                })
                    else:
                        self.msgm.updateMessage({"message": payload['message'],
                                                 "id": payload["id"],
                                                 "sms_delivery_report": "Message Not sent",
                                                 "recipient": to, "message_type": MessageTypes.sms.value,
                                                 })

                    return True
                    
            
        logger.info(to)
        logger.info("about to send a message")
        if not crmSettingObj.disable_sms:
            response = sms.send(message, [to],SENDERID ,callback=on_finish)
        else:
            print("reality")
            self.msgm.updateMessage({"message": payload['message'],"user":payload['user'],
                                     "id": payload["id"],
                                     "sms_delivery_report": " Message sent "+" SMS DISABLED",
                                     "recipient": to, "message_type": MessageTypes.sms.value,
                                     })
        return True


   # def sendSingleEmailMessage(self,payload):

#     def sender(self):
#         pass
#     def resendMsg(self,id):
#         msgObj=Message.objects.get(id=id)
#         try:
#
#             results = gateway.sendMessage(msgObj.recipient, msgObj.message,"OPALQUICK")
#
#
#             for recipient in results:
#                 msgObj.status=recipient['status']
#                 logger.info(recipient['cost'].split(" "))
#
#                 msgObj.messageid=recipient['messageId']
#                 try:
#                   msgObj.charge=Decimal(recipient['cost'].split(" ")[1])
#                 except:
#                   msgObj.charge=0
#
#                 if recipient['status']=="Success":
#                     msgObj.delivery_report="Message delivered"
#                 else:
#                     msgObj.delivery_report="Message Not delivered"
#                 msgObj.recipient=recipient['number']
#                 msgObj.save()
#             return recipient['status']
#         except AfricasTalkingGatewayException, e:
#             logger.info('Encountered an error while sending: '+str(e))
#             return str(e)
#
#
#     def sendmessage(self,to,message,owner):
#          try:
#
#
#              results = gateway.sendMessage("+254"+str(format_phone(to)), message,"OPALQUICK")
#
#         #     print message
#              for recipient in results:
#         #         # status is either "Success" or "error message"
#         #         print 'number=%s;status=%s;messageId=%s;cost=%s' % (recipient['number'],
#         #                                                             recipient['status'],
#         #                                                             recipient['messageId'],
#         #                                                             recipient['cost'])
#                  msg=Message()
#                  msg.message=message
#                  msg.status=recipient['status']
#                  msg.messageid=recipient['messageId']
#                  try:
#                    msg.charge=Decimal(recipient['cost'].split(" ")[1])
#                  except:
#                    msg.charge=0
#         #
#                  msg.user=User.objects.get(id=owner)
#                  if recipient['status']=="Success":
#                      msg.delivery_report="Message delivered"
#                  else:
#                      msg.delivery_report="Message Not delivered"
#                  msg.recipient=recipient['number']
#                  msg.save()
#         #         print "i am here denis"
#                  return recipient['status']
#         #
#          except AfricasTalkingGatewayException, e:
#              logger.info('Encountered an error while sending: '+str(e))
#              msg=Message()
#              msg.message=message
#              msg.status="Not sent"
#              msg.user=User.objects.get(id=owner)
#              msg.delivery_report="Message not delivered"
#              msg.recipient=to
#              msg.save()
#              return "failed"
#
# def returnDatesDiff(current_tym,variable_date):
#     return abs((current_tym -datetime.strptime(variable_date.strftime("%Y-%m-%d"),"%Y-%m-%d")).days)

class OpalHelper:
    def randChar(self,digits):
            return ''.join(random.choice('1234567890') for i in range(digits))

    def resetOTP(self,user):
        user.otp= None
        user.save()

    

class CleanValidation:

    def validate_uuid4(self,uuid_string):
        """
        Validate that a UUID string is in
        fact a valid uuid4.

        Happily, the uuid module does the actual
        checking for us.

        It is vital that the 'version' kwarg be passed
        to the UUID() call, otherwise any 32-character
        hex string is considered valid.
        """

        try:
            val = UUID(uuid_string, version=4)
        except ValueError:
            # If it's a value error, then the string
            # is not a valid hex code for a UUID.
            return False

        return val.hex == uuid_string.replace('-', '')
    # def storeDeviceDetails(self,data):
    #     d=DeviceDetails.objects.filter(imei_number1=data['imei_number1'],user=self.user.id)
    #     if not d.exists():
    #         d=DeviceDetails()
    #         d.imei_number1=data['imei_number1']
    #         d.imei_number2=data['imei_number2']
    #         d.phone_model=data['phone_model']
    #         d.user=self.user
    #         d.save()
    #     else:
    #         pass
            #do nothing
    def format_phone(self,phone):
        return PhoneNumber.from_string(
            phone_number= phone, region='KE').as_e164
        
    #
    def checkImei(self,p,request):
        if "imei_number1" in request.data or "imei_number2" in request.data:
            #confirm with stored one..
            status1=status2=None

            if not request.data['imei_number1'] == str(p.imei_number1):
                self.storeDeviceDetails({"imei_number1":request.data['imei_number1'],
                                         "imei_number2":request.data['imei_number2'],
                                          "phone_model":request.data['phone_model']})
                                          
                return False

            else:

                return True
        else:
            return True #legacy APPs not updated yet ..Just allow
    #
    def checkPhoneModel(self,p,request):
        if "phone_model" in request.data:
            if request.data['phone_model'] in p.phone_model:
                return True
            else:
                return False
        else:
            return True
    #
    #
    #
    def restrictSafaricom(self,phone):
    
        m=MobilePrefix.objects.filter(name=phone[4:7])
        if m.exists():
            return True
        else:
            return False
# class PaginateHelper:
#     def __init__(self,queryset=None):
#         paginator = Paginator(querysert, 10)
#         page = request.GET.get('page')
#         details
#         try:
#             detail = paginator.page(page)
#         except PageNotAnInteger:
#             # If page is not an integer, deliver first page.
#             details = paginator.page(1)
#         except EmptyPage:
#             # If page is out of range (e.g. 9999), deliver last page of results.
#             details = paginator.page(paginator.num_pages)
#         return details
