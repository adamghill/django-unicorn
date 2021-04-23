
from django_unicorn.components import QuerySetType, UnicornView
from electronics.models import Board, Board_Status
from django.contrib.auth.models import User, Group
from datetime import datetime,timedelta
from django.utils import timezone

class ModelRelationsView(UnicornView):
    board_id = 1

    board : Board = Board.objects.none()
    users: QuerySetType[User] = User.objects.none()
    board_statuses : QuerySetType[Board_Status] = Board_Status.objects.none()
    is_editing = False

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)  # calling super is required
        self.board_id = kwargs.get("board_id")

    def edit(self):
        self.is_editing = True
        self.users = User.objects.all()
        self.board_statuses = Board_Status.objects.all()


    def save(self):
        self.board.board_last_edited_by = self.request.user
        self.board.board_last_edited_on = datetime.now(tz=timezone.utc)
        self.board.save()
        self.is_editing = False
        self.load_data()

    def cancel(self):
        

        self.is_editing = False
        self.load_data()

    def mount(self):
        self.load_data()
      

    def load_data(self):
        self.board = Board.objects.get(pk=self.board_id)
        self.is_editing = False

    class Meta:
        exclude = ("board_group_visibility", )
    class Meta:
        javascript_exclude = ("board_group_visibility", )