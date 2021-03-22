# cython: language_level=3
from .xcel1_decode import xcel1_decode, xcel1_args_schema
from .xcel2_decode import xcel2_decode, xcel2_args_schema
from .xcel3_decode import xcel3_decode, xcel3_args_schema
from .xcel4_decode import xcel4_decode, xcel4_args_schema
from .xcel5_decode import xcel5_decode, xcel5_args_schema
from .xcel6_decode import xcel6_decode, xcel6_args_schema

ENGINES = {
    'xcel-1': xcel1_decode,
    'xcel-2': xcel2_decode,
    'xcel-3': xcel3_decode,
    'xcel-4': xcel4_decode,
    'xcel-5': xcel5_decode,
    'xcel-6': xcel6_decode,
}

ENGINE_ARGS_SCHEMA = {
    'type': 'object',
    'properties': {
        'xcel-1': xcel1_args_schema,
        'xcel-2': xcel2_args_schema,
        'xcel-3': xcel3_args_schema,
        'xcel-4': xcel4_args_schema,
        'xcel-5': xcel5_args_schema,
        'xcel-6': xcel6_args_schema,
    }
}
