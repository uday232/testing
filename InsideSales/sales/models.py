import uuid

from django.db import models


class CustomerInfo(models.Model):
    customer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    customer_name = models.CharField(max_length=255)
    division = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    customer_linkedin_page = models.CharField(max_length=255)
    customer_webpage = models.CharField(max_length=255)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    location_address = models.CharField(max_length=255)
    number_people = models.CharField(max_length=50)
    revenue = models.CharField(max_length=50)
    industry = models.CharField(max_length=100)
    sub_industry = models.CharField(max_length=100)
    ticker = models.CharField(max_length=50)

    def __str__(self):
        return str(self.customer_id)

    class Meta:
        managed = False
        db_table = 'customer'


class ContactInfo(models.Model):
    contact_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    customer_id = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, db_column='customer_id')
    first_name = models.CharField(max_length=255)
    title = models.CharField(max_length=100)
    function = models.CharField(max_length=100)
    last_name = models.CharField(max_length=255)
    location_local = models.CharField(max_length=255)
    linkedin_id_url = models.CharField(max_length=255)
    linkedin_connected = models.CharField(max_length=3, default='no')
    LinkedIn_email = models.CharField(max_length=255, db_column='personal_email_id')
    LinkedIn_email_status = models.CharField(max_length=255, db_column='pe_id_status')
    business_email_id = models.CharField(max_length=255)
    be_id_status = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=50)
    direct_landline = models.CharField(max_length=50)
    hq_landline = models.CharField(max_length=50)
    country = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    zoominfo_url = models.CharField(max_length=255, unique=True)
    zoominfo_scraping_status = models.IntegerField()
    zoominfo_scraping_link = models.CharField(max_length=200)
    last_updated_timestamp = models.BigIntegerField()
    company_status = models.CharField(max_length=255)
    linkedin_url_encrypted = models.CharField(max_length=255)
    apollo_status = models.IntegerField()

    def __str__(self):
        return str(self.contact_id)

    class Meta:
        managed = False
        db_table = 'contact'


class CampaignInfo(models.Model):
    campaign_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    campaign_name = models.CharField(max_length=255)
    description = models.CharField(max_length=500)
    attribute_value_pairs = models.CharField(max_length=500)
    campaign_status = models.CharField(max_length=50)
    created_ts = models.CharField(max_length=255)
    no_of_leads = models.CharField(max_length=255)
    completed_leads = models.CharField(max_length=255)
    csv_flag = models.CharField(max_length=50)

    def __str__(self):
        return str(self.campaign_id)

    class Meta:
        managed = False
        db_table = 'campaign'


class SalesPersonInfo(models.Model):
    salesperson_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    salesperson_name = models.CharField(max_length=100)
    salesperson_email = models.CharField(max_length=255)
    salesperson_ph_number = models.CharField(max_length=20)
    # salesperson_dripify_username = models.CharField(max_length=255)
    # salesperson_dripify_password = models.CharField(max_length=255)

    def __str__(self):
        return str(self.salesperson_id)

    class Meta:
        managed = False
        db_table = 'sales_person'


class SalesPersonDetails(models.Model):
    saels_person_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255) 
    api_key = models.CharField(max_length=100)
    user_level = models.CharField(max_length=45)
    service = models.CharField(max_length=45)
    created_ts = models.BigIntegerField()
    updated_ts = models.BigIntegerField()

    def __str__(self):
        return str(self.saels_person_id)
    
    class Meta:
        managed = False
        db_table = 'sales_person_details'


class CampaignSalesPersonMappingInfo(models.Model):
    campaign_salesperson_mapping_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                                                       unique=True)
    salesperson_id = models.UUIDField(unique=False)
    campaign_id = models.ForeignKey(CampaignInfo, on_delete=models.CASCADE, db_column='campaign_id')

    def __str__(self):
        return str(self.campaign_salesperson_mapping_id)

    class Meta:
        managed = False
        db_table = 'campaign_salesperson_mapping'


class LinkedInTemplate(models.Model):
    linkedin_template_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    template_type = models.CharField(max_length=50)
    subject = models.CharField(max_length=255)
    body = models.CharField()

    def __str__(self):
        return str(self.linkedin_template_id)

    class Meta:
        managed = False
        db_table = 'linkedin_template'


class LinkedInTouchPoints(models.Model):
    ltp_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    tp_type = models.CharField(max_length=50)
    contact_id = models.ForeignKey(ContactInfo, on_delete=models.CASCADE, db_column='contact_id')
    campaign_id = models.ForeignKey(CampaignInfo, on_delete=models.CASCADE, db_column='campaign_id')
    linkedin_template_id = models.UUIDField(default=uuid.uuid4)
    date = models.CharField(max_length=255)
    lstatus = models.CharField(max_length=50)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    dripify_status = models.CharField(max_length=50)

    def __str__(self):
        return str(self.ltp_id)

    class Meta:
        managed = False
        db_table = 'linkedin_touchpoints'


class EmailTemplate(models.Model):
    etemplate_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    subject = models.CharField(max_length=255)
    body = models.CharField()

    def __str__(self):
        return str(self.etemplate_id)

    class Meta:
        managed = False
        db_table = 'email_template'


class EmailTouchPoints(models.Model):
    etouchpoint_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    etype = models.CharField(max_length=50)
    contact_id = models.ForeignKey(ContactInfo, on_delete=models.CASCADE, db_column='contact_id')
    campaign_id = models.ForeignKey(CampaignInfo, on_delete=models.CASCADE, db_column='campaign_id')
    etemplate_id = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE,
                                     db_column='etemplate_id')
    date = models.CharField(max_length=255)
    estatus = models.CharField(max_length=50)

    def __str__(self):
        return str(self.etouchpoint_id)

    class Meta:
        managed = False
        db_table = 'email_touchpoints'


class PhoneTouchPoints(models.Model):
    ptp_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    contact_id = models.ForeignKey(ContactInfo, on_delete=models.CASCADE, db_column='contact_id')
    campaign_id = models.ForeignKey(CampaignInfo, on_delete=models.CASCADE, db_column='campaign_id')
    date = models.CharField(max_length=255)
    pstatus = models.CharField(max_length=50)
    start_time = models.CharField(max_length=255)
    end_time = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    def __str__(self):
        return str(self.ptp_id)

    class Meta:
        managed = False
        db_table = 'phone_touchpoints'


class CampaignContactMappingInfo(models.Model):
    campaign_contact_mapping_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                                                   unique=True)
    contact_id = models.ForeignKey(ContactInfo, on_delete=models.CASCADE, db_column='contact_id')
    campaign_id = models.ForeignKey(CampaignInfo, on_delete=models.CASCADE, db_column='campaign_id')

    def __str__(self):
        return str(self.campaign_contact_mapping_id)

    class Meta:
        managed = False
        db_table = 'campaign_contact_mapping'


class CronJobInfo(models.Model):
    job_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    model_name = models.CharField(max_length=255)
    start_ts = models.BigIntegerField()
    end_ts = models.BigIntegerField()
    status = models.CharField(max_length=255)
    remarks = models.TextField()

    def __str__(self):
        return str(self.job_uuid)

    class Meta:
        managed = False
        db_table = 'cron_job_status'


class MeetingTouchpoint(models.Model):
    meeting_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact_id = models.ForeignKey(ContactInfo, on_delete=models.CASCADE, db_column='contact_id')
    campaign_id = models.ForeignKey(CampaignInfo, on_delete=models.CASCADE, db_column='campaign_id')
    date = models.CharField(max_length=255)
    pmeeting_status = models.CharField(max_length=50)
    start_time = models.CharField(max_length=255)
    end_time = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    def __str__(self):
        return str(self.meeting_id)
    
    class Meta:
        managed = False
        db_table = 'meeting_touchpoints'


class Note(models.Model):
    notes_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact_id = models.ForeignKey(ContactInfo, on_delete=models.CASCADE, db_column='contact_id')
    campaign_id = models.ForeignKey(CampaignInfo, on_delete=models.CASCADE, db_column='campaign_id')
    date = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    description = models.CharField(max_length=255)


    def __str__(self):
        return str(self.notes_id)
    
    class Meta:
        managed = False
        db_table = 'notes'