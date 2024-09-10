from django.urls import path

import sales
from .views import *
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('campaign', Campaign.as_view()), # Create Campaign
    path('data', DataView.as_view()),
    path('linkedin', LinkedInActivities.as_view()),
    path('linkedin/<str:id>/', LinkedInActivities.as_view()),
    path('emails', EmailActivities.as_view()),
    path('emails/<str:id>/', EmailActivities.as_view()),
    path('phone', PhoneActivities.as_view()),
    path('phone/<str:id>/', PhoneActivities.as_view()),
    path('campaigns', CampaignList.as_view()),
    path('testapollo',Apolloapitest.as_view()),
    path('testdripify',Dripifyapitest.as_view()),
    path('testzoominfo',ZoomInfoapitest.as_view()),
    path('adminsaveconfig',AdminSaveConfig.as_view()),
    path('usersaveconfig',UserSaveConfig.as_view()),
    path('verifyemailpassword',VerifyEmailPassword.as_view()),
    path('dashboard',DashBoardMain.as_view()),
    path('contacts',DashBoardMainInside.as_view()),
    path('nextbestactions',NextBestActions.as_view()),
    path('contact',DeleteContactsDashboard.as_view()),
    path('activecampaigns',ActiveCampaignList.as_view()),
    path('campaignstatus',ChangeCampaignStatus.as_view()),
    path('activity',CreateActivity.as_view()),
    path('customer/<str:customer_id>',GetCustomerInfo.as_view()),
    path('history/<str:customer_id>',GetHistory.as_view()),
    path('correction',ContactCorrection.as_view()),
    # path('test', Test.as_view())
    # path('upload',ZoomInfo.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
