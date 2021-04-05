import os

from django.core.management.base import CommandError

import pytest

from django_unicorn.management.commands.startunicorn import Command


def test_handle_no_base_dir():
    with pytest.raises(CommandError):
        Command().handle()


def test_handle_no_args(settings):
    settings.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    with pytest.raises(CommandError):
        Command().handle()
