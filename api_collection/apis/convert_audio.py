# cython: language_level=3
import os
import base64
import random

from flask import request
from flask import current_app as app
from flask_restful import Resource
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from werkzeug.utils import secure_filename
from celery.result import AsyncResult

from ..engines import ENGINES, ENGINE_ARGS_SCHEMA
from ..utils import wavutils
from ..tasks import async_decode


class ConvertAudioAPI(Resource):
    decorators = [jwt_required]

    def post(self):
        engines = request.form.getlist('engine')
        if not engines:
            raise BadRequest('Audio decode engine not specified')
        for engine in engines:
            if engine not in ENGINES:
                raise BadRequest(
                    'Invalid audio decode engine name: {}'.format(engine)
                )

        if 'file' not in request.files:
            raise BadRequest('File is not supplied.')
        fileobj = request.files['file']

        file_name = fileobj.filename
        file_path = os.path.join('/shared', file_name)
        fileobj.save(file_path)
        fileobj.stream.seek(0)

        # file_path = os.path.join(app.root_path, fileobj.filename)
        # fileobj.save(file_path)

        ext = os.path.splitext(fileobj.filename)[-1].lower()
        if ext not in ('.mp3', '.wav', '.flac'):
            raise BadRequest('Uploaded file is not a WAV/MP3/Flac file.')
        stream = fileobj.stream

        cluster_mode = request.form.get('cluster_mode', '0')
        if cluster_mode not in ('0', '1'):
            raise BadRequest(
                'Parameter "cluster_mode" is neither 0 nor 1'
            )
        cluster_mode = int(cluster_mode)

        num_speakers = request.form.get('num_speakers', '2')
        if num_speakers == '0' or not num_speakers.isdigit():
            raise BadRequest(
                'Parameter "num_speakers" must be a number greater than 1'
            )
        num_speakers = int(num_speakers)

        audio_language = request.form.get('language', 'en')
        all_languages = app.config['ALL_LANGUAGES']
        if audio_language not in all_languages:
            raise BadRequest(
                'Parameter "language" must be {}, or {} (default: en)'
                    .format(', '.join(all_languages[:-1]), all_languages[-1])
            )

        for engine in engines:
            support_languages = app.config['ENGINE_LANGUAGES'][engine]
            if audio_language not in support_languages:
                raise BadRequest(
                    'Language "{}" is not supported by Engine "{}"'
                        .format(audio_language, engine)
                )

        engine_args = {key: {} for key in ENGINES}
        for key in request.form.keys():
            if key.startswith('__eargs__'):
                engine_name, arg_name = key[9:].split('_', 1)
                engine_args[engine_name][arg_name] = request.form[key]
        try:
            validate(engine_args, ENGINE_ARGS_SCHEMA)
        except ValidationError as ex:
            raise BadRequest(str(ex))

        if ext == '.wav':
            # convert WAV to FLAC
            app.logger.debug('Convert WAV to FLAC')
            framerate = wavutils.read_framerate(stream)
            stream = wavutils.resample_audio(stream, framerate,
                                             output_format='flac')
            ext = '.flac'

        # prepare stream for JSON.dumps
        b64_stream = base64.b64encode(stream.read()).decode('ASCII')
        app.logger.debug('Base64 Audio Size: %s', len(b64_stream))

        tasks = []
        for engine in engines:
            task = async_decode.apply_async(
                [b64_stream, ext[1:], engine,
                 audio_language, fileobj.filename, file_path,
                 cluster_mode, num_speakers],
                {'email': get_jwt_identity(),
                 'engine_args': engine_args[engine]},
                task_id=str(random.randint(0, 0x7fffffffffffffff)))
            tasks.append({
                'status': task.status,
                'task_id': str(task.id),
                'task_url': app.api.url_for(ConvertAudioAPI,
                                            task_id=str(task.id),
                                            _external=True),
            })
        return tasks

    def get(self, task_id):
        if not task_id:
            raise BadRequest('The task_id is not supplied.')
        task = AsyncResult(task_id, app=app.celery)
        task_url = app.api.url_for(ConvertAudioAPI,
                                   task_id=str(task.id),
                                   _external=True)
        if task.successful():
            return {
                'status': task.status,
                'task_id': str(task.id),
                'task_url': task_url,
                'task_result': task.get(),
            }

        else:
            return {
                'status': task.status,
                'task_id': str(task.id),
                'task_url': task_url
            }
