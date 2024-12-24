# general utils for native clients

def client_oneshot(func_name, client_class, arg_names):
    def wrapper(query, **kwargs):
        client = client_class(**{k: kwargs.pop(k) for k in arg_names if k in kwargs})
        return getattr(client, func_name)(query, **kwargs)
    return wrapper
