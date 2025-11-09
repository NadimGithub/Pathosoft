from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = [
    path('', include('accounts.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
    path('doctor/', include('doctor.urls')),
    path('patient/', include('patient.urls')),
    path('tests/', include('tests.urls')),
    path('labs/', include('labs.urls')),
   

]
