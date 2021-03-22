# cython: language_level=3
import os
import math

from subprocess import PIPE, Popen

from flask import current_app as app


def split_audio(wavdata, audioinfo, workdir, chunksize):
    duration = audioinfo['duration']

    if duration <= chunksize:
        # no need to split
        outpath = os.path.join(workdir, 'chunk.0.wav')
        with open(outpath, 'wb') as wavfile:
            wavfile.write(wavdata)
        return [outpath]

    chunkpaths = []
    for idx, start in enumerate(
            range(0, int(math.ceil(duration)), chunksize)):
        if duration - start < app.config['WAV_MIN_DURATION']:
            break
        outpath = os.path.join(workdir, 'chunk.{}.wav'.format(idx))
        with Popen([app.config['FFMPEG_CMD'], '-i', '-', '-acodec', 'copy',
                    '-ss', str(start), '-t', str(chunksize), outpath],
                   stdin=PIPE, stderr=PIPE) as proc:
            _, err = proc.communicate(wavdata,
                                      timeout=app.config['FFMPEG_TIMEOUT'])
        if proc.returncode:
            raise RuntimeError('ffmpeg error: {}'.format(err))
        chunkpaths.append(outpath)
    return chunkpaths
