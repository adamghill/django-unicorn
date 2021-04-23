from django.db import models
from django.contrib.auth.models import User, Group
from datetime import datetime,timedelta
from django.utils.timezone import now
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey


class Board_Category(MPTTModel):
    name = models.CharField(max_length=1024)
    parent = TreeForeignKey('self',on_delete=models.CASCADE,null=True,blank=True, related_name='children')
    class MPTTMeta:
        order_insertion_by = ['name']
    def __str__(self):
        return 'BCat ' + str(self.id) + ' - ' + self.name
    class Meta:
        verbose_name = 'Board Category'
        verbose_name_plural = 'Board Categories'


class Board_Status(models.Model):
    status_name = models.CharField(
        max_length=1024)
    badge_class = models.CharField(
        max_length=45,
        default='primary',
        null=True,
        blank=True)
    custom_color = models.CharField(
        max_length=45,
        null=True,
        blank=True)
    force_custom_color = models.BooleanField(default=False)
    def __str__(self):
        return 'S' + str(self.id) + ' - ' + self.status_name
    class Meta:
        verbose_name = 'Board Status'
        verbose_name_plural = 'Board Statuses'

class Board(models.Model):
    board_name = models.CharField(max_length=1024)
    board_revision = models.FloatField(default=1)
    board_variant = models.CharField(default='A',max_length=5)
    board_category = models.ForeignKey(Board_Category,on_delete=models.PROTECT,null=True,blank=True)
    board_added_on = models.DateTimeField(default=now)
    board_added_by = models.ForeignKey(User,on_delete=models.PROTECT,related_name='related_board_added_by',null=True,blank=True)
    board_last_edited_on = models.DateTimeField(default=now)
    board_last_edited_by = models.ForeignKey(User,on_delete=models.PROTECT,related_name='related_board_last_edited_by',null=True,blank=True)
    board_status = models.ForeignKey(Board_Status,on_delete=models.PROTECT,null=True,blank=True)
    board_last_component_upload_on = models.DateTimeField(default=None, null=True, blank=True)
    board_last_component_upload_by = models.ForeignKey(User,on_delete=models.PROTECT,related_name='related_board_last_component_upload_by',null=True,blank=True)
    board_value_update_datetime = models.DateTimeField(default=None, null=True, blank=True)
    board_cover_picture = models.ForeignKey('Board_Image',on_delete=models.PROTECT,null=True,blank=True)
    board_appears_on_tania = models.BooleanField(default=False)
    board_group_visibility = models.ManyToManyField(Group, blank=True)

        
    class Meta:
        verbose_name = 'Board'
        verbose_name_plural = 'Boards'
    # def get_absolute_url(self):
    #     return reverse('board', args=[str(self.id)])


class Board_Image(models.Model):
    bi_board = models.ForeignKey(Board,on_delete=models.PROTECT,null=True,blank=True)
    bi_image = models.ImageField(upload_to='uploads/board-images/%Y/%m/%d/', blank=True, null=True)
    bi_upload_datetime = models.DateTimeField(default=now, blank=True, null=True)
    class Meta:
        verbose_name = 'Board Image'
        verbose_name_plural = 'Board Images'