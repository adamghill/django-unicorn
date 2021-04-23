from django.contrib import admin
from .models import Board, Board_Status, Board_Category, Board_Image

class BoardAdmin(admin.ModelAdmin):
    filter_horizontal = ('board_group_visibility',)
    list_display = ['id', 'board_name', 'board_status']
    list_filter = ('board_status','board_name')
admin.site.register(Board,BoardAdmin)
admin.site.register(Board_Status)
admin.site.register(Board_Image)
admin.site.register(Board_Category)