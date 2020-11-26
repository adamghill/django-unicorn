from django_unicorn.templatetags.unicorn import unicorn
from django.template.base import DebugLexer, Token, TokenType


def test_unicorn():
    token = Token(TokenType.TEXT, "unicorn 'todo'")
    unicorn_node = unicorn(None, token)

    assert unicorn_node.component_name == "todo"


def test_unicorn_args():
    token = Token(TokenType.TEXT, "unicorn 'todo' 'blob'")
    unicorn_node = unicorn(None, token)

    assert unicorn_node.args == [
        "'blob'",
    ]


# def test_unicorn_render():
#     token = Token(TokenType.TEXT, "unicorn 'todo' 'blob'")
#     unicorn_node = unicorn(None, token)
#     context = {}

#     assert unicorn_node.render(context) == ""
