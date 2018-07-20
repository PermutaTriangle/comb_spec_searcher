from functools import partial
from logzero import logger


def get_func_name(f, warn=False,
                  logger_kwargs={'processname': 'utils'}):
    if not callable(f):
        raise TypeError("Function given is not callable.")
    if isinstance(f, partial):
        f = f.func
        if warn:
            logger.warn(("forgetting kwargs given to partial function "
                         "using strategy" + f.__name__),
                        extra=logger_kwargs)
    return f.__name__


def get_module_and_func_names(f, warn=False,
                              logger_kwargs={'processname': 'utils'}):
    if isinstance(f, partial):
        f = f.func
        if warn:
            logger.warn(("forgetting kwargs given to partial function "
                         "using strategy" + f.__name__),
                        extra=logger_kwargs)
    return (f.__module__, f.__name__)


def get_func(module_name, func_name, warn=False,
             logger_kwargs={'processname': 'utils'}):
    import importlib
    try:
        module = importlib.import_module(module_name)
        try:
            func = getattr(module, func_name)
            assert callable(func)
            return func
        except:
            if warn:
                logger.warn(("No function named " + func_name +
                            " in module " + module_name),
                            extra=logger_kwargs)
    except Exception as e:
        if warn:
            logger.warn("No module named " + module_name,
                        extra=logger_kwargs)
