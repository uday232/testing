from rest_framework import serializers
from .models import PhoneTouchPoints,EmailTouchPoints,LinkedInTouchPoints,CampaignInfo

class PhoneTouchPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneTouchPoints
        fields = '__all__'


class EmailTouchPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTouchPoints
        fields = '__all__'

class LinkedInTouchPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkedInTouchPoints
        fields = '__all__'

class CampaignInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignInfo
        fields = '__all__'