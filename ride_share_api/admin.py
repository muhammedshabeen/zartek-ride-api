from django.contrib import admin
from .models import *

@admin.register(CustomUser)
class CustomUserModelAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'username', 'email', 'phone_number','role')
    
    
    
admin.site.register(Ride)
