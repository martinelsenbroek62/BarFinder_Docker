# cython: language_level=3
import os
import time
import base64
from datetime import datetime

from flask import current_app as app

from tempfile import TemporaryDirectory

from .utils import wavutils
from .engines import ENGINES
from .engines.diarization import diarization
from .utils.engineutils import get_engine_config


@app.celery.task()
def async_decode(b64_stream, stream_format, engine_name,
                 audio_language, filename, filepath, cluster_mode,
                 num_speakers, email, engine_args):
    print('async_decode/filename: ', filepath)

    time_start = time.time()
    engine_func = ENGINES[engine_name]
    framerate = get_engine_config(
        'WAV_MAX_FRAMERATE', engine_name, audio_language)
    audiodata = base64.b64decode(b64_stream)
    with TemporaryDirectory() as workdir:
        audiofile = os.path.join(workdir, 'audio.{}'.format(stream_format))
        with open(audiofile, 'wb') as fp:
            fp.write(audiodata)
        chunks = list(wavutils.iter_wav_chunks(
            audiofile, stream_format, framerate,
            min_chunk_len=(
                app.config['WAV_CHUNK_MIN_DURATION'][engine_name]),
            max_chunk_len=(
                app.config['WAV_CHUNK_MAX_DURATION'][engine_name])))
        transcripts = list(engine_func(chunks, audio_language, engine_args))
        total_duration = wavutils.chunks_get_duration(chunks)
        if email:
            current_user = app.models.User.get_by_email(email)
            current_user.log_usage(engine_name, int(total_duration))
            app.db.session.commit()
        finaltps = diarization(
            chunks, transcripts, cluster_mode, num_speakers, filepath)
        return {
            'engine': engine_name,
            'engine_args': engine_args,
            'language': audio_language,
            'duration': total_duration,
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'filename': filename,
            'transcripts': finaltps,
            'process_time': time.time() - time_start
        }
