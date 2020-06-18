from django.urls import path

from . import views
from bridge.apiviews.blogs import *
from bridge.apiviews.crmsettings import *
from bridge.apiviews.messages import *
from bridge.apiviews.ticketing import *

urlpatterns = [
    path('api/mobile/prefix/all/', views.MobilePrefixCollections.as_view()), #list and create company

    path('api/mobile/prefix/<int:id>/', views.MobilePrefixSingleCollection.as_view()), #retrieve.delete,


######blogs###
    path('api/bridge/blogs/', AdminArticlesViews.as_view(), name="blog"),
    path('api/bridge/blog/<id>/', AdminArticleView.as_view(), name="readblog"),
    path('api/bridge/blog/', AdminArticlesViews.as_view(), name="readblog"),

###terms and privacy
    path('api/bridge/privacyterms/<domain_name>/<article_type>/', TermsPrivacyListView.as_view(), name="blog"),
    path('api/bridge/articletypes/', ArticleTypesView.as_view()),

    path('api/bridge/blogcategories/', CategoryViews.as_view()),
    path('api/bridge/blogcategory/<id>/', CategoryView.as_view()),
    path('api/bridge/blogcategory/', CategoryView.as_view()),
    path('api/bridge/blogbycategory/<id>/', BlogByCategoryView.as_view()),

    ####Message Templates ####
    path('api/bridge/messagetemplates/', MessageTemplatesViews.as_view()),
    path('api/bridge/messagetemplate/<id>/', MessageTemplateView.as_view()),
    path('api/bridge/messagetemplate/', MessageTemplateView.as_view()),

    path('api/bridge/messagepolicydays/', MessagePolicyDaysViews.as_view()),
    path('api/bridge/messagepolicyday/<id>/', MessagePolicyDetailView.as_view()),
    path('api/bridge/messagepolicyday/', MessagePolicyDetailView.as_view()),



###messaging

    path('api/bridge/messages/', MessagesViews.as_view()),
    path('api/bridge/message/<id>/', MessageView.as_view()),
    path('api/bridge/message/',  MessageView.as_view()),
    path('api/bridge/messagetypes/',  MessageTypesView.as_view()),
    #groups
    path('api/bridge/messagegroups/', MessageGroupViews.as_view()),
    path('api/bridge/messagegroup/<id>/', MessageGroupView.as_view()),
    path('api/bridge/messagegroup/', MessageGroupView.as_view()),
    path('api/bridge/sendgroupmessage/', SendGroupMessage.as_view()),

    #group contacts
    path('api/bridge/groupcontacts/<group>/', GroupContactViews.as_view()),
    path('api/bridge/groupcontact/<id>/', GroupContactView.as_view()),
    path('api/bridge/groupcontact/',GroupContactView.as_view()),
    path('api/bridge/uploadgroupcontacts/', GroupContactUploadView.as_view()),


    # Sender Id
    path('api/bridge/messagesenderids/', SenderIdViews.as_view()),
    path('api/bridge/messagesenderid/', SenderIdView.as_view()),
    path('api/bridge/messagesenderid/<id>/', SenderIdView.as_view()),

    path('api/bridge/crmsetting/<id>/', CrmSettingView.as_view()),
    path('api/bridge/crmsetting/', CrmSettingView.as_view())
]
