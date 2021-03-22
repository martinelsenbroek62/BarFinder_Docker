# cython: language_level=3
import os
import io
import struct
from tempfile import TemporaryDirectory

import soundfile
from webrtcvad import Vad
from subprocess import PIPE, Popen

from flask import current_app as app

from .iter_with_timeout import iter_with_timeout


def wavinfo(stream):
    wavdata, framerate = soundfile.read(stream)
    duration = len(wavdata) / framerate
    # return pointer to the beginning of file
    stream.seek(0)
    return {
        'framerate': framerate,
        'duration': duration
    }


def read_framerate(header):
    # sample rate /frame rate
    if hasattr(header, 'read'):
        stream = header
        header = stream.read(28)
        stream.seek(0)
    return struct.unpack('<L', header[24:28])[0]


def read_byterate(header):
    # byte length of a second
    if hasattr(header, 'read'):
        stream = header
        header = stream.read(32)
        stream.seek(0)
    return struct.unpack('<L', header[28:32])[0]


def save_chunks(chunks, workdir, indexfile):
    resultpaths = []
    with open(indexfile, 'w') as indexfp:
        for idx, (header, data, duration, offset) in enumerate(chunks):
            filename = 'chunk.{}.wav'.format(idx)
            outpath = os.path.join(workdir, filename)
            with open(outpath, 'wb') as fp:
                fp.write(header + data)
            indexfp.write('{} {} {}\n'.format(filename, duration, offset))
            indexfp.flush()
            resultpaths.append(outpath)
        indexfp.write('__done__ -1 -1\n')
        indexfp.flush()
        return resultpaths


def concat_wavchunks(chunks, framerate, output_format='wav'):
    stream = []
    for idx, (header, data, *_) in enumerate(chunks):
        if idx == 0:
            stream.append(header)
        stream.append(data)

    stream = b''.join(stream)
    orig_framerate = read_framerate(stream)
    if orig_framerate == framerate and output_format == 'wav':
        # no need to resample
        return io.BytesIO(stream)
    else:
        out = resample_audio(stream, framerate,
                             output_format=output_format)
        return out


def resample_audio(stream, framerate, input_format='wav', output_format='wav'):
    data = stream
    if hasattr(stream, 'read'):
        data = stream.read()
    with TemporaryDirectory() as workdir:
        outpath = os.path.join(workdir, '.audioout')
        output_acodec = {
            'wav': 'pcm_s16le',
            'mp3': 'mp3',
            'flac': 'flac'
        }[output_format]
        add_acodec_option = []
        if output_format == 'mp3':
            add_acodec_option = ['-q:a', '0']
        elif output_format == 'flac':
            add_acodec_option = ['-compression_level', '12']
        with Popen([app.config['FFMPEG_CMD'], '-f', input_format, '-i', '-',
                    '-acodec', output_acodec, *add_acodec_option, '-ac', '1',
                    '-ar', str(framerate), '-vn',
                    '-f', output_format, outpath],
                   stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
            _, err = proc.communicate(
                data, timeout=app.config['FFMPEG_TIMEOUT'])
        app.logger.debug('FFMPEG: %s', err.decode('U8'))
        if proc.returncode:
            raise RuntimeError('ffmpeg error: {}'.format(err))
        with open(outpath, 'rb') as fp:
            return io.BytesIO(fp.read())


def stream2wav(input_uri, input_format, framerate):
    command = [app.config['FFMPEG_CMD']]

    lower_uri = input_uri.lower()
    if lower_uri.startswith('rtmp://'):
        input_format = 'flv'
    elif lower_uri.startswith('rtp://'):
        command.extend(['-protocol_whitelist', 'file,rtp,udp'])

    if input_format:
        command.extend(['-f', input_format])

    command.extend([
        '-i', input_uri,  # can be a file or URL
        '-vn',  # disable video
        '-acodec', 'pcm_s16le',  # set audio codec to be PCM
        '-ac', '1',  # set to single audio channel
        '-ar', str(framerate),  # set sampling rate
        '-f', 'wav',
        'pipe:stdout'])

    with Popen(command, stdout=PIPE, stderr=PIPE, shell=False) as proc:
        # 78 is usually the length of a header;
        # 4 is usually the size of a block_align
        firstchunk = proc.stdout.read(4 * framerate + 78)

        # Subchunk2ID + Subchunk2Size = 8
        headerlen = firstchunk.find(b'data') + 8

        header = firstchunk[:headerlen]
        try:
            chunksize = read_byterate(header)
        except struct.error:
            # stop iteration
            yield False, proc.stderr.read().decode('UTF-8')
            return
        chunk = firstchunk[headerlen:]
        while len(chunk) >= chunksize:
            yield True, header, chunk, 1.0, chunksize
            chunk = chunk[chunksize:]

        if chunk:
            # tweak to exactly 1 second
            chunk += proc.stdout.read(chunksize - len(chunk))
            yield True, header, chunk, len(chunk) / chunksize, chunksize

        for chunk in iter(lambda: proc.stdout.read(chunksize), b''):
            yield True, header, chunk, len(chunk) / chunksize, chunksize


@iter_with_timeout()
def iter_wav_chunks(input_uri, input_format, framerate=16000,
                    vad_duration=0.02, min_chunk_len=2, max_chunk_len=10):
    vad = Vad(2)
    bufferbytes = io.BytesIO()
    buffersize = 0
    bufferduration = 0
    remains = b''
    audio_offset = .0
    for ok, *payload in \
            stream2wav(input_uri, input_format, framerate):
        if not ok:
            raise RuntimeError(payload[0])
        header, body, _, secondsize = payload
        chunksize = round(secondsize * 0.02)  # 20ms
        body = remains + body
        if min_chunk_len < 0:
            # no limit
            bufferbytes.write(body)
            buffersize += len(body)
            bufferduration = buffersize / secondsize
            continue
        for offset in range(0, len(body), chunksize):
            chunk = body[offset:offset + chunksize]
            if len(chunk) < chunksize:
                remains = chunk
                break
            if bufferduration < min_chunk_len or \
                    (bufferduration < max_chunk_len and
                     vad.is_speech(chunk, framerate)):
                bufferbytes.write(chunk)
                buffersize += chunksize
                bufferduration += chunksize / secondsize
            elif buffersize > 0:
                audiodata = bufferbytes.getvalue() + chunk
                duration = len(audiodata) / secondsize
                yield (header, audiodata,
                       duration, audio_offset)
                audio_offset += duration
                bufferbytes = io.BytesIO()
                buffersize = 0
                bufferduration = 0
    if buffersize > 0:
        audiodata = bufferbytes.getvalue() + remains
        duration = len(audiodata) / secondsize
        yield (header, audiodata,
               duration, audio_offset)


def chunks_get_duration(chunks):
    return sum(duration for _, _, duration, _ in chunks)
