# cython: language_level=3
import re
import uuid
import random
import base64
from threading import Thread, Lock
from contextlib import contextmanager

from flask import session, request, current_app as app, url_for
from flask_socketio import emit, send

from ..utils import wavutils
from ..utils.safetee import safetee
from ..utils.engineutils import get_engine_config
from ..engines import ENGINES
from ..tasks import async_decode

URL_PATTERN = re.compile(r'^(rtmp)://.+$')

_port_allocation_lock = Lock()
_port_allocated = set()


@contextmanager
def allocate_rtp_port():
    port_start, port_end = app.config['RTP_PORT_RANGE']
    with _port_allocation_lock:
        if len(_port_allocated) == port_end - port_start:
            raise RuntimeError('RTP port pool getting exhausted.')
        for port in range(port_start, port_end, 2):
            if port not in _port_allocated:
                # Audio and video are typically sent using RTP [RFC3550], which
                # requires two UDP ports, one for the media and one for the
                # control protocol (RTCP).
                # -- https://tools.ietf.org/html/rfc3605
                _port_allocated.add(port)
                _port_allocated.add(port + 1)
                break
    yield port
    with _port_allocation_lock:
        _port_allocated.remove(port)
        _port_allocated.remove(port + 1)


def parallel_log(app, wavchunks, engine, user_email):
    with app.app_context():
        preserved_chunks = []

        log = None
        total_duration = .0
        prev_checkpoint = .0
        current_user = app.models.User.get_by_email(user_email)

        for wavchunk in wavchunks:
            preserved_chunks.append(wavchunk)
            _, _, duration, _ = wavchunk
            total_duration += duration
            # update user_log every 30 seconds
            if total_duration - prev_checkpoint > 30:
                if not log:
                    log = current_user.log_usage(engine, int(total_duration))
                else:
                    log.instance_quantity = int(total_duration)
                    prev_checkpoint = total_duration
                app.db.session.commit()


def _livestream(event_id, url, source_url, engine,
                audio_language, cluster_mode, num_speakers):
    engine_func = ENGINES[engine]
    user_email = session.get('current_user_email')

    send({
        'event': 'livestream',
        'event_id': event_id,
        'source_url': source_url,
        'status': 'created'
    })
    framerate = get_engine_config('WAV_MAX_FRAMERATE', engine, audio_language)
    wavchunks = wavutils.iter_wav_chunks(
        url, None,
        framerate,
        min_chunk_len=10,
        max_chunk_len=20
    )

    wavchunks, wavchunks2, wavchunks3 = safetee(wavchunks, 3)
    thread = Thread(
        target=parallel_log,
        args=(app._get_current_object(),
              wavchunks, engine, user_email)
    )
    thread.start()

    for transcript in engine_func(wavchunks2, audio_language, {}):
        send({
            'event': 'livestream',
            'event_id': event_id,
            'source_url': url,
            'status': 'ongoing',
            'task_result': transcript
        })
    stream = wavutils.concat_wavchunks(wavchunks3, framerate, 'flac')
    # prepare stream for JSON.dumps
    b64_stream = base64.b64encode(stream.read()).decode('ASCII')

    print("I'm jumpping into livestream...")

    task = async_decode.apply_async(
        [b64_stream, 'flac', engine,
         audio_language, '_livestream.flac', '',
         cluster_mode, num_speakers],
        {'email': None,
         'engine_args': {}},
        task_id=str(random.randint(0, 0x7fffffffffffffff)))

    send({
        'event': 'livestream',
        'event_id': event_id,
        'status': 'finished',
        'postprocess': {
            'status': task.status,
            'task_url': url_for('convert_audio',
                                task_id=str(task.id),
                                _external=True)
        }
    })


@app.socketio.on('livestream')
def livestream(data):
    event_id = str(uuid.uuid4())
    url = source_url = data.get('url', '')
    use_rtp = data.get('use_rtp', False)
    engine = data.get('engine', '')
    if engine not in ENGINES:
        emit('error', {
            'event': 'livestream',
            'event_id': event_id,
            'status': 'error',
            'error_message': 'Invalid engine name (engine={}).'.format(engine)
        })
        return

    cluster_mode = data.get('cluster_mode', '0')
    if cluster_mode not in ('0', '1'):
        emit('error', {
            'event': 'livestream',
            'event_id': event_id,
            'status': 'error',
            'error_message': 'Parameter "cluster_mode" is neither 0 nor 1'
        })
        return
    cluster_mode = int(cluster_mode)

    num_speakers = data.get('num_speakers', '2')
    if num_speakers == '0' or not num_speakers.isdigit():
        emit('error', {
            'event': 'livestream',
            'event_id': event_id,
            'status': 'error',
            'error_message':
                'Parameter "num_speakers" must be a number greater than 1'
        })
        return
    num_speakers = int(num_speakers)

    audio_language = data.get('language', 'en')
    all_languages = app.config['ALL_LANGUAGES']
    if audio_language not in all_languages:
        emit('error', {
            'event': 'livestream',
            'event_id': event_id,
            'status': 'error',
            'error_message':
                'Parameter "language" must be {}, or {} (default: en)'
             .format(', '.join(all_languages[:-1]), all_languages[-1])
        })
        return

    support_languages = app.config['ENGINE_LANGUAGES'][engine]
    if audio_language not in support_languages:
        emit('error', {
            'event': 'livestream',
            'event_id': event_id,
            'status': 'error',
            'error_message':
                'Language "{}" is not supported by Engine "{}"'
             .format(audio_language, engine)
        })
        return

    if use_rtp:
        if url:
            emit('error', {
                'event': 'livestream',
                'event_id': event_id,
                'status': 'error',
                'error_message':
                    'The "url" parameter is disallowed when "use_rtp" is set.'
            })
            return
        with allocate_rtp_port() as port:
            source_url = 'rtp://{}:{}'.format(
                request.host.rsplit(':', 1)[0],
                port)
            url = 'rtp://0.0.0.0:{}'.format(port)
            _livestream(event_id, url, source_url, engine,
                        audio_language, cluster_mode, num_speakers)
    elif not URL_PATTERN.match(url.lower()):
        emit('error', {
            'event': 'livestream',
            'event_id': event_id,
            'status': 'error',
            'error_message':
                'Invalid streaming URL (support protocols: RTMP).'
        })
        return
    else:
        _livestream(event_id, url, url, engine,
                    audio_language, cluster_mode, num_speakers)
