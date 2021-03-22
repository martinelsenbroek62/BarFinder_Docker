# cython: language_level=3
import os
from pathlib import Path
from threading import Thread

import docker
from tempfile import TemporaryDirectory

from flask import current_app as app

from ..utils import wavutils

from .xcel2_decode import read_transcript
from ..utils.engineutils import get_engine_config
from ..utils.follow_file import follow_file
from ..utils.iter_with_timeout import iter_with_timeout

ENGINE_NAME = 'xcel-4'

xcel4_args_schema = {
    'type': 'object',
    'properties': {
        'subsampling_factor': {
            'type': 'string',
            'enum': ['1', '2', '3', '4', '5']
        }
    }
}


def decode_audio(audio_language, self_inputindex,
                 self_outputindex, subsampling_factor):
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
            [app.config['ENGINE_CMD'][ENGINE_NAME], 'cpu',
             inputindex, outputindex],
            environment={
                'FRAME_SUBSAMPLING_FACTOR': subsampling_factor
            },
            volumes={
                app.config['HOST_SHARED_DIR']: {
                    'bind': decoder_shared_dir,
                    'mode': 'rw'
                }
            },
            remove=app.config['AUTOREMOVE_CONTAINERS'], detach=True)
        self_outputdir = os.path.dirname(self_outputindex)
        for line in follow_file(self_outputindex):
            outfile, duration, offset = line.strip().split()
            if outfile == '__done__':
                break
            yield (os.path.join(self_outputdir, outfile),
                   float(duration), float(offset))
    finally:
        if container:
            try:
                container.kill()
            except docker.errors.APIError:
                pass


@iter_with_timeout()
def xcel4_decode(chunks, audio_language, engine_args):
    shared_dir = app.config['SHARED_DIR']
    ss_factor = engine_args.get(
        'subsampling_factor',
        get_engine_config(
            'ENGINE_SUBSAMPLING_FACTOR',
            ENGINE_NAME, audio_language, 1))
    with TemporaryDirectory(dir=shared_dir) as workdir:
        inputindex = os.path.join(workdir, 'inputindex.txt')
        outputindex = os.path.join(workdir, 'outputindex.txt')
        outpaths = decode_audio(audio_language, inputindex,
                                outputindex, ss_factor)
        thread = Thread(
            target=wavutils.save_chunks,
            args=(chunks, workdir, inputindex))
        thread.start()
        for outpath, duration, offset in outpaths:
            yield from read_transcript(outpath, duration, offset, ss_factor)
