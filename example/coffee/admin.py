from django.contrib import admin

from .models import Flavor, Origin, Taste


admin.site.register(Flavor)
admin.site.register(Taste)
admin.site.register(Origin)
