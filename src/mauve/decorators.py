from functools import wraps


def kwarg_validator(*arg_names):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for arg in arg_names:
                if arg not in kwargs:
                    raise Exception('Not all kwargs given. Required: %s' % (
                        arg_names
                    ))
            return func(*args, **kwargs)
        return wrapper
    return decorator
