# cython: language_level=3
import os
import json
from pathlib import Path
from threading import Thread

import docker
from tempfile import TemporaryDirectory

from flask import current_app as app

from ..utils import wavutils
from ..utils.engineutils import get_engine_config
from ..utils.follow_file import follow_file
from ..utils.iter_with_timeout import iter_with_timeout

ENGINE_NAME = 'xcel-5'

xcel5_args_schema = {
    'type': 'object',
    'properties': {}
}


def decode_audio(audio_language, self_inputindex,
                 self_outputindex, engine_args):
    Path(self_outputindex).touch()  # ensure the outputindex is created
    self_shared_dir = app.config['SHARED_DIR']
    decoder_shared_dir = app.config['DECODER_SHARED_DIR']
    inputindex = os.path.join(
        decoder_shared_dir,
        os.path.relpath(self_inputindex, self_shared_dir))
    outputindex = os.path.join(
        decoder_shared_dir,
        os.path.relpath(self_outputindex, self_shared_dir))
    client = docker.from_env()
    container = None
    try:
        container = client.containers.run(
            get_engine_config(
                'ENGINE_DOCKER_IMAGE', ENGINE_NAME, audio_language),
            environment={
                'DECODE_MODE': 'gpu',
                'AUDIO_LANG': audio_language,
                'INPUTINDEX': inputindex,
                'OUTPUTINDEX': outputindex,
            },
            volumes={
                app.config['ENGINE_DIAL_HOST_MODELS_DIR']: {
                    'bind': app.config['ENGINE_DIAL_MODELS_DIR'],
                    'mode': 'rw'
                },
                app.config['HOST_SHARED_DIR']: {
                    'bind': decoder_shared_dir,
                    'mode': 'rw'
                }
            },
            runtime='nvidia',
            remove=app.config['AUTOREMOVE_CONTAINERS'], detach=True)
        self_outputdir = os.path.dirname(self_outputindex)
        for line in follow_file(self_outputindex):
            outfile, duration, offset = line.strip().split()
            if outfile == '__done__':
                break
            yield (
                os.path.join(self_outputdir, outfile),
                float(duration), float(offset))
    finally:
        if container:
            try:
                container.kill()
            except docker.errors.APIError:
                pass


def read_transcript(transcript_path):
    with open(transcript_path) as jsonfile:
        yield from json.load(jsonfile)


@iter_with_timeout()
def xcel5_decode(chunks, audio_language, engine_args):
    shared_dir = app.config['SHARED_DIR']
    with TemporaryDirectory(dir=shared_dir) as workdir:
        inputindex = os.path.join(workdir, 'inputindex.txt')
        outputindex = os.path.join(workdir, 'outputindex.txt')
        outpaths = decode_audio(audio_language, inputindex,
                                outputindex, engine_args)
        thread = Thread(
            target=wavutils.save_chunks,
            args=(chunks, workdir, inputindex))
        thread.start()
        for outpath, _, _ in outpaths:
            yield from read_transcript(outpath)
