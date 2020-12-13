import logging
from ast import literal_eval
from typing import Any, Dict, List, Tuple
from uuid import UUID

from django.utils.dateparse import parse_datetime


logger = logging.getLogger(__name__)

# Lambda that attempts to convert something that failed while being parsed by `ast.literal_eval`.
CASTERS = [
    lambda a: parse_datetime(a),
    lambda a: UUID(a),
]

STOP_CHARACTERS = [":", ",", "]", "}", ")"]
STRING_CHARACTERS = ["'", '"']


class InvalidKwarg(Exception):
    pass


def parse_kwarg(kwarg: str, raise_if_unparseable=False) -> Dict[str, Any]:
    """
    Parses a potential kwarg as a string into a dictionary.

    For example: `parse_kwarg("test='1'")` == `{"test": "1"}`


    """

    parsed_kwarg = {}
    kwarg = kwarg.strip()

    if "=" not in kwarg:
        raise InvalidKwarg(f"{kwarg} is invalid")
    if kwarg.startswith("'") or kwarg.startswith('"'):
        raise InvalidKwarg(
            f"{kwarg} key cannot start with single quote or double quote"
        )

    has_equal_sign = False
    key = ""
    val = ""

    for c in kwarg:
        if c == "=":
            has_equal_sign = True
        elif has_equal_sign:
            val += c
        else:
            key += c

        if not has_equal_sign and (c == "'" or c == '"'):
            raise InvalidKwarg(
                f"{kwarg} key cannot contain a single quote or double quote"
            )

    # Attempt to parse the value into a primitive, but allow it to be returned if not possible
    # (the value can be a template variable that will get set from the context when
    # the templatetag is rendered in which case it can't be parsed in this manner)
    try:
        val = parse_args(val)[0]
    except ValueError:
        if raise_if_unparseable:
            raise

    parsed_kwarg[key] = val

    return parsed_kwarg


def parse_args(args: str) -> List[Any]:
    """
    Parses arguments as a string into Python objects.

    For example: "'1'" would result in a "1". Or "[1, 2]" would result in [1, 2].

    Handles strings, ints, floats, lists, tuples, dictionaries, sets, datetime, UUID.

    Datetime is parsed with `parse_datetime`: https://docs.djangoproject.com/en/stable/ref/utils/#django.utils.dateparse.parse_datetime.
    """
    found_args = []
    arg = ""

    curly_bracket_count = 0
    square_bracket_count = 0
    parenthesis_count = 0

    inside_string = False

    def _eval_arg(_arg):
        try:
            _arg = literal_eval(_arg)
        except SyntaxError:
            for caster in CASTERS:
                try:
                    casted_value = caster(_arg)

                    if casted_value:
                        _arg = casted_value
                        break
                except ValueError:
                    pass

        return _arg

    def _parse_arg(_arg):
        if (
            curly_bracket_count == 0
            and square_bracket_count == 0
            and parenthesis_count == 0
        ):
            _arg = _eval_arg(_arg)
            found_args.append(_arg)
            return ""

        return _arg

    for c in args:
        if len(arg) > 1:
            if c in STOP_CHARACTERS:
                previous_char = arg[-1:][0]

                if previous_char == "'":
                    inside_string = False

        if not inside_string and not c.strip():
            continue

        if (
            c == ","
            and not inside_string
            and curly_bracket_count == 0
            and square_bracket_count == 0
            and parenthesis_count == 0
        ):
            if arg:
                arg = _eval_arg(arg)
                found_args.append(arg)
                arg = ""

            continue

        arg += c

        if c == "{":
            curly_bracket_count += 1
        elif c == "}":
            curly_bracket_count -= 1
            arg = _parse_arg(arg)
        elif c == "[":
            square_bracket_count += 1
        elif c == "]":
            square_bracket_count -= 1
            arg = _parse_arg(arg)
        elif c == "(":
            parenthesis_count += 1
        elif c == ")":
            parenthesis_count -= 1
            arg = _parse_arg(arg)
        elif c in STRING_CHARACTERS:
            inside_string = True

    if arg:
        if arg.startswith("'") and arg.endswith("'") and len(arg.split("'")) > 3:
            arg = arg[1:-1]

        arg = _eval_arg(arg)
        found_args.append(arg)

    return found_args


def parse_call_method_name(call_method_name: str) -> Tuple[str, List[Any]]:
    """
    Parses the method name from the request payload into a set of parameters to pass to a method.

    Args:
        param call_method_name: String representation of a method name with parameters, e.g. "set_name('Bob')"

    Returns:
        Tuple of method_name and a list of arguments.
    """

    method_name = call_method_name
    params: List[Any] = []

    if "(" in call_method_name and call_method_name.endswith(")"):
        param_idx = call_method_name.index("(")
        params_str = call_method_name[param_idx:]

        # Remove the arguments from the method name
        method_name = call_method_name.replace(params_str, "")

        # Remove parenthesis
        params_str = params_str[1:-1]

        if params_str == "":
            return (method_name, params)

        # Split up mutiple args
        # TODO: Handle kwargs
        params = parse_args(params_str)

    return (method_name, params)
