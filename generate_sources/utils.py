import json, contextlib


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


def context_value(initial_value):
    def decorator(fn):
        @contextlib.contextmanager
        def decorated_function(*args, **kwargs):
            old_value = decorated_function.current_value
            decorated_function.current_value = fn(old_value, *args, **kwargs)

            try:
                yield
            finally:
                decorated_function.current_value = old_value

        decorated_function.current_value = initial_value

        return decorated_function

    return decorator


def args_accumulator():
    @context_value([])
    def context_fn(value, *args):
        return [*value, *args]

    return context_fn


def kwargs_accumulator():
    @context_value({})
    def context_fn(value, **kwargs):
        return dict(**value, **kwargs)

    return context_fn
