# cython: language_level=3
import os

import docker
from tempfile import TemporaryDirectory
from flask import current_app as app

from ..utils import wavutils
from . import test

ENGINE_NAME = 'diarization'


# adds channels
def add_channel(trans):
    len_transcripts = len(trans)
    for i in range(len_transcripts):
        delta = abs(bookmarks[1]['pos'] - trans[i]['stime'])
        pos = bookmarks[1]['value']
        stime = bookmarks[1]['pos']

        for j in range(2, len(bookmarks) - 1):
            # finds nearest item
            if delta >= abs(bookmarks[j]['pos'] - trans[i]['stime']):
                delta = abs(bookmarks[j]['pos'] - trans[i]['stime'])
                pos = bookmarks[j]['value']
                stime = bookmarks[j]['pos']
            else:
                break
        trans[i]['channel'] = pos
        trans[i]['stime'] = stime

    result = list()
    node = trans[0]
    print('node:', node)
    for i in range(1, len_transcripts):
        if node['channel'] == trans[i]['channel']:
            print('same:', i)
            node['content'] = node['content'] + ' ' + trans[i]['content']
            node['word_chunks'].extend(trans[i]['word_chunks'])
        else:
            print('diff:', i)
            node['duration'] = trans[i]['stime'] - node['stime']

            if 'speaker' in node:
                print('speaker:', i)
                del node['speaker']

            result.append(node)
            node = trans[i]

    # for i in range(len_transcripts):
    #     print('speaker: {:>1} \t stime: {:10} \t {:6}'.format(trans[i]['speaker'], trans[i]['stime'], trans[i]['channel']))
    return result


def prepare_segmentdata(transcripts, workdir):
    outpath = os.path.join(workdir, 'segments')
    is_empty = True
    with open(outpath, 'w') as fp:
        start = .0
        for row in transcripts:
            end = round(row['stime'] + row['duration'], 2)
            if end - start < 2:
                # the sufficient length of a segment
                # should be at least 2 seconds
                continue
            is_empty = False
            fp.write('sample-{:06d}-{:06d} sample {} {}\n'
                     .format(round(start * 100),
                             round(end * 100),
                             start, end))
            start = end
    return outpath, is_empty


def _diarization(self_audiopath, self_segmentpath,
                 self_outpath, cluster_mode, num_speakers):
    self_shared_dir = app.config['SHARED_DIR']
    decoder_shared_dir = app.config['DECODER_SHARED_DIR']
    audiopath = os.path.join(
        decoder_shared_dir,
        os.path.relpath(self_audiopath, self_shared_dir))
    segmentpath = os.path.join(
        decoder_shared_dir,
        os.path.relpath(self_segmentpath, self_shared_dir))
    client = docker.from_env()
    outpath = os.path.join(
        decoder_shared_dir,
        os.path.relpath(self_outpath, self_shared_dir))
    client.containers.run(
        app.config['ENGINE_DOCKER_IMAGE'][ENGINE_NAME],
        [app.config['ENGINE_CMD'][ENGINE_NAME],
         audiopath, segmentpath, outpath,
         str(cluster_mode), str(num_speakers)],
        volumes={
            app.config['HOST_SHARED_DIR']: {
                'bind': decoder_shared_dir,
                'mode': 'rw'
            }
        }, remove=app.config['AUTOREMOVE_CONTAINERS'])


def parse_rttm(rttm_text, transcripts):
    ts_offset = 0
    result = []
    for line in rttm_text.splitlines():
        _, _, _, start, duration, _, _, speaker_id, _, _ = line.split()
        start = round(float(start), 3)
        duration = round(float(duration), 3)
        end = round(start + duration, 3)
        word_chunks = []
        for idx in range(ts_offset, len(transcripts)):
            ts = transcripts[idx]
            if ts['stime'] < end:
                word_chunks.append(ts)
                if ts['stime'] + ts['duration'] > end:
                    ts_offset = idx + 1
                    break
            else:
                ts_offset = idx
                break
        if word_chunks:
            result.append({
                'speaker': speaker_id,
                'stime': start,
                'duration': duration,
                'content': ' '.join(ts['content'] for ts in word_chunks),
                'word_chunks': word_chunks,
            })
        elif result:
            last_one = result[-1]
            last_one['duration'] = last_one['duration'] + duration

    result = add_channel(result)
    return result


def get_speaker_id(timeline, t_start, t_end):
    """TODO: use binary search"""
    for start, end, speaker_id in timeline:
        if start <= t_start < end:
            # .--------.--------------------.
            # ^        ^                    ^
            # start    t_start              end
            return speaker_id
        elif start < t_end <= end:
            # .----------------------.-------.
            # ^                      ^       ^
            # start                  t_end   end
            return speaker_id
        elif t_start <= start < end <= t_end:
            # .--------.-------------.-------.
            # ^        ^             ^       ^
            # t_start  start         end     t_end
            return speaker_id


def parse_rttm_known_word_chunks(rttm_text, transcripts):
    timeline = []
    for line in rttm_text.splitlines():
        _, _, _, start, duration, _, _, speaker_id, _, _ = line.split()
        start = round(float(start), 3)
        duration = round(float(duration), 3)
        end = round(start + duration, 3)
        timeline.append((start, end, speaker_id))
    result = []
    for ts in transcripts:
        t_start = ts['stime']
        t_end = ts['stime'] + ts['duration']
        result.append({
            'speaker': get_speaker_id(timeline, t_start, t_end),
            **ts
        })

    result = add_channel(result)
    return result


def has_word_chunk(transcripts):
    """
    Some engine output (e.g. Julius) already includes word chunks.
    This function detects it.
    """
    return transcripts and 'word_chunks' in transcripts[0]


def fallback_diarization(transcripts, duration):
    if has_word_chunk(transcripts):
        result = [{'channel': 'Start Recording', **ts} for ts in transcripts]
        for each in result:
            if 'speaker' in each:
                del each['speaker']
        return result
    else:
        result = [{
            'channel': 'Start Recording',
            'stime': 0,
            'duration': duration,
            'content': ' '.join(ts['content'] for ts in transcripts),
            'word_chunks': [*transcripts]
        }]
        for each in result:
            if 'speaker' in each:
                del each['speaker']
        return result


def diarization(chunks, transcripts, cluster_mode, num_speakers, file_path):
    total_duration = wavutils.chunks_get_duration(chunks)
    if (cluster_mode == 0 and num_speakers == 1) or \
            total_duration < 10 or len(transcripts) < 10:
        return fallback_diarization(transcripts, total_duration)
    shared_dir = app.config['SHARED_DIR']
    with TemporaryDirectory(dir=shared_dir) as workdir:
        audiopath = os.path.join(workdir, 'audio.wav')
        with open(audiopath, 'wb') as fp:
            fp.write(wavutils.concat_wavchunks(
                chunks,
                app.config['WAV_MAX_FRAMERATE']['diarization']
            ).read())

        global bookmarks
        print('diarization: ', file_path)
        bookmarks = test.get_timestamp(file_path)

        segmentpath, is_empty = prepare_segmentdata(transcripts, workdir)
        if is_empty:
            return fallback_diarization(transcripts, total_duration)
        outpath = os.path.join(workdir, 'rttm_output')
        _diarization(audiopath, segmentpath, outpath,
                     cluster_mode, num_speakers)
        with open(outpath) as fp:
            rttm = fp.read()
            if has_word_chunk(transcripts):
                return parse_rttm_known_word_chunks(rttm, transcripts)
            else:
                return parse_rttm(rttm, transcripts)
