import json
import os

from sympy import Expr


class expression(str): pass


def call(function, **arguments):
    args_str = [
        '{}={}'.format(k, serialize_value(v))
        for k, v in sorted(arguments.items())]

    return expression('{}({})'.format(function, ', '.join(args_str)))


def serialize_value(value):
    if isinstance(value, list):
        return '[{}]'.format(', '.join(map(serialize_value, value)))
    elif isinstance(value, expression):
        return value
    elif isinstance(value, Expr):
        return str(float(value))
    else:
        return json.dumps(value)


def write_text_file(path: str, content: str):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            current_content = file.read()
    else:
        current_content = None

    # Only overwrite the file if it changed, to avoid unnecessary
    # recompilation.
    if current_content != content:
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
