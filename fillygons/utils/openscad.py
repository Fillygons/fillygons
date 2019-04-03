import json
import os

from sympy import Expr


class Expression(str):
    pass


def call(function, **arguments):
    args_str = [
        '{}={}'.format(k, serialize_value(v))
        for k, v in sorted(arguments.items())]

    return Expression('{}({})'.format(function, ', '.join(args_str)))


def serialize_value(value):
    if isinstance(value, list):
        return '[{}]'.format(', '.join(map(serialize_value, value)))
    elif isinstance(value, Expression):
        return value
    elif isinstance(value, Expr):
        return str(float(value))
    else:
        return json.dumps(value)


def use_statement(using_path, used_path):
    return 'use <{}>'.format(
        os.path.relpath(used_path, os.path.dirname(using_path)))
