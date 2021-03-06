import cProfile as c
import dis
import functools
import sys
import time
from pprint import pformat

import slippery.output as o
from slippery.helpers import CustomStats
from slippery.utils import represent_params, get_line, get_module_name

__all__ = [
    'efficiency',
    'execution_time',
    'disassemble',
    'prettify'
]


# TODO: Refactor in all. This is awful!

def execution_time(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)

        template = o.OUTPUT_TEMPLATE
        args, kwargs = represent_params(args, kwargs)

        print(template.format(**{
            'time': time.time() - start_time,
            'func': func.__name__,
            'args': args,
            'kwargs': kwargs,
            'result': pformat(result, indent=0, width=80, compact=True),
        }))
        return result

    return inner


def disassemble(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        result = fn(*args, **kwargs)

        args, kwargs = represent_params(args, kwargs)

        # Get code line
        line = get_line(fn)

        arguments = args + ', ' + kwargs if \
            len(args) >= 1 else kwargs

        with o.LinesPrinter() as lp:
            print(o.DIS_TEMPLATE.format(**{
                'func': fn.__name__,
                'line': o.bold(line),
                'args': args,
                'kwargs': kwargs,
                'arguments': arguments
            }))
            lp.line()
            dis.dis(fn)
        return result

    return inner


# TODO: Add function name, line and args, kwargs
def efficiency(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        profiler = c.Profile()
        profiler.enable()
        try:
            result = func(*args, **kwargs)
        finally:
            profiler.disable()
            stats = CustomStats(profiler, stream=sys.stdout)
            with o.LinesPrinter(end='\n\n') as lp:
                stats.print_stats()

        return result

    return inner


def prettify(indent=0, width=80, compact=True):
    def decorate(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)

            res = pformat(
                result,
                indent=indent,
                width=width,
                compact=compact,
            )

            line = get_line(func)

            # TODO: Replace template with much useful.
            # TODO: Refactoring. It's looks so f**king bad.
            with o.LinesPrinter() as lp:
                print('Function {} from file {}, line {} returns:\n{}'.format(
                    o.cyan(func.__name__ + '()'),
                    o.cyan(get_module_name(func)),
                    line, o.green(res)))

            return result

        return inner

    return decorate
