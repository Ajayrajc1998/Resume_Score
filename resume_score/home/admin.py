from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(UploadedFile)
admin.site.register(Job)
admin.site.register(Resume)
admin.site.register(Application_result)