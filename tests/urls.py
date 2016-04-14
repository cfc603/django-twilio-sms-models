from django.conf.urls import include, url

urlpatterns = [
    url(r'^twilio-integration/', include('django_twilio_sms.urls', namespace='django_twilio_sms')),
]