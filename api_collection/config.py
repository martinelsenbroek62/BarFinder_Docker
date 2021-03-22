# cython: language_level=3
"""EngineDialFrontend configuration"""
import os


def getenv(name, default=None, typehandler=str):
    if name in os.environ:
        return typehandler(os.environ[name])
    elif default is None:
        raise RuntimeError('OS Envrionment `{}` is required.'.format(name))
    else:
        return default


def text_bool(value):
    return value.lower() == 'true'


class Default:
    """Default configuration

    pylint: disable=too-few-public-methods
    """

    # Enable or disable debug mode. This should be set to False in production.
    DEBUG = getenv('DEBUG', True, text_bool)

    # Whether to remove engine containers automatically or not,
    # this parameter can be very useful for debugging
    AUTOREMOVE_CONTAINERS = \
        getenv('AUTOREMOVE_CONTAINERS', True, text_bool)

    # Super secret key used by JWT to create access token
    JWT_SECRET_KEY = getenv('JWT_SECRET_KEY')  # required

    # SQLAlchemy settings. By default we support PostgreSQL as the database
    # backend. However it is easy to change to other engine by chaging the
    # DATABASE_URI variable.
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = getenv(
        'DATABASE_URI',
        'postgresql+psycopg2://postgres@localhost:5436/postgres')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # In Debian > 8, ffmpeg is replaced by avconv
    FFMPEG_CMD = getenv('FFMPEG_CMD', 'ffmpeg')

    # ffmpeg process timeout (seconds); used for resampling and chunk-splitting
    FFMPEG_TIMEOUT = getenv('FFMPEG_TIMEOUT', 120.0, float)

    # Maximum framerate (sampling rate) of a WAV audio
    WAV_MAX_FRAMERATE = {
        'xcel-1': 16000,  # dial gpu
        'xcel-2': 8000,  # kaldi gpu
        'xcel-2_lang-zh': 16000,  # kaldi gpu for Chinese
        'xcel-2_lang-en2': 16000,  # kaldi gpu for Teldium English
        'xcel-2_lang-en-us': 16000,  # kaldi gpu for Teldium English
        'xcel-2_lang-en-uk': 16000,  # kaldi gpu for Teldium English
        'xcel-3': 16000,  # dial cpu
        'xcel-4': 8000,  # kaldi cpu
        'xcel-4_lang-zh': 16000,  # kaldi cpu for Chinese
        'xcel-4_lang-en2': 16000,  # kaldi gpu for Teldium English
        'xcel-4_lang-en-us': 16000,  # kaldi gpu for Teldium English
        'xcel-4_lang-en-uk': 16000,  # kaldi gpu for Teldium English
        'xcel-5': 16000,  # julius gpu
        'xcel-6': 16000,  # julius cpu
        'diarization': 8000  # kaldi diarization
    }

    # Minimal duration of an audio (by seconds). When exceeded, the audio
    # file will be chunk splitted, either by VAD or WAV_CHUNK_MAX_DURATION.
    WAV_CHUNK_MIN_DURATION = {
        'xcel-1': getenv('ENGINE_XCEL1_WAV_MIN_DURATION', 15, int),
        'xcel-2': getenv('ENGINE_XCEL2_WAV_MIN_DURATION', 150, int),
        'xcel-3': getenv('ENGINE_XCEL3_WAV_MIN_DURATION', 15, int),
        'xcel-4': getenv('ENGINE_XCEL4_WAV_MIN_DURATION', 150, int),
        'xcel-5': getenv('ENGINE_XCEL5_WAV_MIN_DURATION', -1, int),  # no limit
        'xcel-6': getenv('ENGINE_XCEL6_WAV_MIN_DURATION', -1, int),  # no limit
    }

    # Maximum duration of an audio (by seconds).
    WAV_CHUNK_MAX_DURATION = {
        'xcel-1': getenv('ENGINE_XCEL1_WAV_MAX_DURATION', 25, int),
        'xcel-2': getenv('ENGINE_XCEL2_WAV_MAX_DURATION', 300, int),
        'xcel-3': getenv('ENGINE_XCEL3_WAV_MAX_DURATION', 25, int),
        'xcel-4': getenv('ENGINE_XCEL4_WAV_MAX_DURATION', 300, int),
        'xcel-5': getenv('ENGINE_XCEL5_WAV_MIN_DURATION', -1, int),  # no limit
        'xcel-6': getenv('ENGINE_XCEL6_WAV_MIN_DURATION', -1, int),  # no limit
    }

    # Minimal chunk duration (seconds)
    WAV_MIN_DURATION = getenv('WAV_MIN_DURATION', 0.1, float)

    # `docker run` parameters for starting decoder image
    ENGINE_DOCKER_IMAGE = {
        'xcel-1': getenv('ENGINE_XCEL1_DOCKER_IMAGE',
                         'engine_dial:latest-gpu'),
        'xcel-2': getenv('ENGINE_XCEL2_DOCKER_IMAGE',
                         'engine_xcel2:latest'),
        'xcel-2_lang-en2': getenv('ENGINE_XCEL2_DOCKER_IMAGE_LANG_EN2',
                                  'engine_xcel2:latest-tedlium'),
        'xcel-2_lang-en-us': getenv('ENGINE_XCEL2_DOCKER_IMAGE_LANG_EN_US',
                                    'engine_xcel2:latest-tedlium-en-us'),
        'xcel-2_lang-en-uk': getenv('ENGINE_XCEL2_DOCKER_IMAGE_LANG_EN_UK',
                                    'engine_xcel2:latest-tedlium-en-uk'),
        'xcel-2_lang-zh': getenv('ENGINE_XCEL2_DOCKER_IMAGE_LANG_ZH',
                                 'engine_xcel2:latest-mandarin'),
        'xcel-3': getenv('ENGINE_XCEL3_DOCKER_IMAGE',
                         'engine_dial:latest-cpu'),
        'xcel-4': getenv('ENGINE_XCEL4_DOCKER_IMAGE',
                         'engine_xcel2:latest'),
        'xcel-4_lang-en2': getenv('ENGINE_XCEL4_DOCKER_IMAGE_LANG_EN2',
                                  'engine_xcel2:latest-tedlium'),
        'xcel-4_lang-en-us': getenv('ENGINE_XCEL4_DOCKER_IMAGE_LANG_EN_US',
                                    'engine_xcel2:latest-tedlium-en-us'),
        'xcel-4_lang-en-uk': getenv('ENGINE_XCEL4_DOCKER_IMAGE_LANG_EN_UK',
                                    'engine_xcel2:latest-tedlium-en-uk'),
        'xcel-4_lang-zh': getenv('ENGINE_XCEL4_DOCKER_IMAGE_LANG_ZH',
                                 'engine_xcel2:latest-mandarin'),
        'diarization': getenv('ENGINE_DIARIZATION_DOCKER_IMAGE',
                              'engine_diarization:latest'),
        'xcel-5_lang-ja': getenv('ENGINE_XCEL5_DOCKER_IMAGE_LANG_JA',
                                 'engine_julius:latest-ja'),
        'xcel-6_lang-ja': getenv('ENGINE_XCEL6_DOCKER_IMAGE_LANG_JA',
                                 'engine_julius:latest-ja'),
    }

    ALL_LANGUAGES = ('en', 'en2', 'en-us', 'en-uk', 'zh', 'ja')

    ENGINE_LANGUAGES = {
        'xcel-1': ['en', 'zh'],
        'xcel-2': ['en', 'zh', 'en2', 'en-us', 'en-uk'],
        'xcel-3': ['en', 'zh'],
        'xcel-4': ['en', 'zh', 'en2', 'en-us', 'en-uk'],
        'xcel-5': ['ja'],
        'xcel-6': ['ja'],
    }

    ENGINE_CMD = {
        'xcel-1': getenv('ENGINE_XCEL1_CMD', '/entrypoint.sh'),
        'xcel-2': getenv('ENGINE_XCEL2_CMD', '/entrypoint.sh'),
        'xcel-3': getenv('ENGINE_XCEL3_CMD', '/entrypoint.sh'),
        'xcel-4': getenv('ENGINE_XCEL4_CMD', '/entrypoint.sh'),
        'xcel-5': getenv('ENGINE_XCEL5_CMD',
                         '/decode_engine/scripts/entrypoint.sh'),
        'xcel-6': getenv('ENGINE_XCEL6_CMD',
                         '/decode_engine/scripts/entrypoint.sh'),
        'diarization': getenv('ENGINE_DIARIZATION_CMD', '/entrypoint.sh'),
    }

    # Fail-safe mechanism in case an engine dead and block all follow-up tasks.
    # Once set, the master thread will monitor each iteration of the engine
    # for ENGINE_ITERATION_TIMEOUT seconds. Once exceeded a TimeoutError will
    # be triggered
    DEFAULT_ITERATION_TIMEOUT = \
        getenv('DEFAULT_ITERATION_TIMEOUT', 600.0, float)

    ENGINE_SUBSAMPLING_FACTOR = {
        'xcel-2': 3,
        'xcel-4': 3,
    }

    ENGINE_DIAL_HOST_MODELS_DIR = getenv('ENGINE_DIAL_HOST_MODELS_DIR')
    ENGINE_DIAL_MODELS_DIR = \
        getenv('ENGINE_DIAL_VOLUMES_BIND', '/DecodeEngine/models')
    ENGINE_DIAL_TRAINER_COUNT = getenv('ENGINE_DIAL_TRAINER_COUNT', 1, int)

    # Local folder shared with decode.py Docker container
    SHARED_DIR = getenv('SHARED_DIR', '/shared')

    # Host folder that shared same files with SHARED_DIR
    HOST_SHARED_DIR = getenv('HOST_SHARED_DIR')

    # Decode.py Docker container folder that shared same files with SHARED_DIR
    DECODER_SHARED_DIR = getenv('DECODER_SHARED_DIR', '/shared')

    # Celery backend settings
    CELERY_BROKER_URL = getenv('CELERY_BROKER_URL',
                               'pyamqp://rabbitmq:5672')
    CELERY_RESULT_BACKEND = getenv('CELERY_RESULT_BACKEND',
                                   'redis://redis:6379')
    CELERY_TASK_RESULT_EXPIRES = getenv('CELERY_TASK_RESULT_EXPIRES',
                                        604800, int)
    BROKER_CONNECTION_TIMEOUT = 60

    # CORS setting
    ALLOWED_ORIGIN = '*'
    RTP_PORT_RANGE = getenv('RTP_PORT_RANGE', (45000, 46000),
                            lambda x: [int(i.strip()) for i in x.split('-')])
