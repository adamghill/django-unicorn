from django.template.base import Parser, Token, TokenType

from django_unicorn.templatetags.unicorn import unicorn


def test_unicorn():
    token = Token(TokenType.TEXT, "unicorn 'todo'")
    unicorn_node = unicorn(Parser([]), token)

    assert unicorn_node.component_name.resolve({}) == "todo"
    assert len(unicorn_node.kwargs) == 0


def test_unicorn_kwargs():
    token = Token(TokenType.TEXT, "unicorn 'todo' blob='blob'")
    unicorn_node = unicorn(Parser([]), token)

    assert unicorn_node.kwargs == {"blob": "blob"}


def test_unicorn_args_and_kwargs():
    # args after the component name get ignored
    token = Token(TokenType.TEXT, "unicorn 'todo' '1' 2 hello='world' test=3 '4'")
    unicorn_node = unicorn(Parser([]), token)

    assert unicorn_node.kwargs == {"hello": "world", "test": 3}
