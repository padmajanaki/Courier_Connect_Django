from django.contrib import admin
from .models import Courier,User,Branch,Tracker,Report,Courierform, ContactMessage
# Register your models here.


admin.site.register(Courier)
admin.site.register(User)
admin.site.register(Branch)
admin.site.register(Tracker)
admin.site.register(Report)
admin.site.register(Courierform)
admin.site.register( ContactMessage)