import json


class expression(str): pass


def call(function, **arguments):
    args_str = [
        '{} = {}'.format(k, serialize_value(v))
        for k, v in sorted(arguments.items())]

    return expression('{}({})'.format(function, ', '.join(args_str)))


def serialize_value(value):
    if isinstance(value, list):
        return '[{}]'.format(', '.join(map(serialize_value, value)))
    elif isinstance(value, expression):
        return value
    else:
        return json.dumps(value)
