import ast
import logging
from typing import Any, Dict, List, Tuple
from uuid import UUID

from django.utils.dateparse import (
    parse_date,
    parse_datetime,
    parse_duration,
    parse_time,
)


logger = logging.getLogger(__name__)

# Lambdas that attempt to convert something that failed while being parsed by `ast.parse`.
CASTERS = [
    lambda a: parse_datetime(a),
    lambda a: parse_time(a),
    lambda a: parse_date(a),
    lambda a: parse_duration(a),
    lambda a: UUID(a),
]


class InvalidKwarg(Exception):
    pass


def eval_arg(arg):
    try:
        arg = ast.literal_eval(arg)
    except SyntaxError:
        for caster in CASTERS:
            try:
                casted_value = caster(arg)

                if casted_value:
                    arg = casted_value
                    break
            except ValueError:
                pass

    return arg


def parse_kwarg(kwarg: str, raise_if_unparseable=False) -> Dict[str, Any]:
    """
    Parses a potential kwarg as a string into a dictionary.
    For example: `parse_kwarg("test='1'")` == `{"test": "1"}`
    """

    # TODO: Look into using something like `ast.parse(kwarg, "eval")` for this

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
        val = eval_arg(val)
    except ValueError:
        if raise_if_unparseable:
            raise

    parsed_kwarg[key] = val

    return parsed_kwarg


def parse_call_method_name(call_method_name: str) -> Tuple[str, List[Any]]:
    """
    Parses the method name from the request payload into a set of parameters to pass to a method.

    Args:
        param call_method_name: String representation of a method name with parameters, e.g. "set_name('Bob')"

    Returns:
        Tuple of method_name and a list of arguments.
    """

    dollar_func = False

    # Deal with special methods that start with a "$"
    if call_method_name.startswith("$"):
        dollar_func = True
        call_method_name = call_method_name[1:]

    tree = ast.parse(call_method_name, "eval")
    method_name = call_method_name
    params: List[Any] = []
    kwargs: Dict[str, Any] = {}

    if tree.body and isinstance(tree.body[0].value, ast.Call):
        call = tree.body[0].value
        method_name = call.func.id
        params = [eval_arg(arg) for arg in call.args]

        # Not returned, but might be usable
        kwargs = {kw.arg: eval_arg(kw.value) for kw in call.keywords}

    # Add "$" back to special functions
    if dollar_func:
        method_name = f"${method_name}"

    return (method_name, params, kwargs)
