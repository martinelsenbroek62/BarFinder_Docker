#! /usr/bin/env python
from __future__ import print_function
from __future__ import unicode_literals

import os
import re
import sys
import json
import time

from collections import namedtuple

PATTERN_AUDIOFILE = re.compile(
    r'^Stat: adin_file: input speechfile: (.+?\.wav)$'
)
PATTERN_CHUNKINFO = re.compile(
    r'^sent: \d+ samples \((\d+\.\d+) sec.\) '
    r'\[\s*\d+ \(\s*(\d+\.\d+)s\) -\s*'
    r'\d+ \(\s*(\d+\.\d+)s\)\]$'
)
PATTERN_SENTENCE = re.compile(r'^sentence1: (.*)$')
PATTERN_WORDGRAPH_IDXTS = re.compile(r'^(\d+): \[(\d+)\.\.(\d+)\]')
PATTERN_WORDGRAPH_LEFT = re.compile(r' left=([,\d]+) ')
PATTERN_WORDGRAPH_RIGHT = re.compile(r' right=([,\d]+) ')
PATTERN_WORDGRAPH_NAME = re.compile(r' name="([^"]*)" ')
PATTERN_WORDGRAPH_SCORE = re.compile(r' cmscore=(\d+\.\d+) ')

AudioChunk = namedtuple('AudioChunk', ['audiopath', 'start', 'duration'])
WordGraphData = namedtuple(
    'WordGraphData', ['index', 'name',
                      'start', 'end',
                      'left', 'right',
                      'duration', 'score'])
Word = namedtuple('Word', ['start', 'end', 'duration', 'text', 'confidence'])


def follow_file(filename, timeout=None):
    where = 0
    total_wait = 0
    if timeout is None:
        timeout = [0]
    while True:
        # check inode every run, because sometime the inode changed
        # but fp was still tracking to the old inode
        with open(filename, 'rb') as fp:
            fp.seek(where)
            line = fp.readline()
            line = line.decode('UTF-8')
            if not line or not line.endswith('\n'):
                time.sleep(1)
                total_wait += 1
                if timeout[0] > 0 and total_wait > timeout[0]:
                    break
            else:
                yield line
                # reset total_wait
                total_wait = 0
                where = fp.tell()


def read_inputindex(path):
    for line in follow_file(path):
        wavfile, duration, offset = line.split()
        if wavfile == '__done__':
            break
        yield wavfile, float(duration), float(offset)


def read_adintool_result(path, dynamic_timeout):
    audiopath = None
    for line in follow_file(path, dynamic_timeout):
        line = line.strip()
        if line.startswith('Stat: adin_file: input speechfile: '):
            match = PATTERN_AUDIOFILE.match(line)
            audiopath = match.group(1)
        elif line.startswith('sent'):
            match = PATTERN_CHUNKINFO.match(line)
            duration, start_time, end_time = [
                float(v) for v in match.groups()]
            assert duration - end_time + start_time < 0.02, \
                ('Duration not matched: {}s vs {}s-{}s ({})'
                 .format(duration, start_time, end_time, audiopath))
            yield AudioChunk(
                audiopath,
                start_time,
                duration
            )


def parse_wordgraph_data(line):
    idxts_match = PATTERN_WORDGRAPH_IDXTS.match(line)
    left_match = PATTERN_WORDGRAPH_LEFT.search(line)
    right_match = PATTERN_WORDGRAPH_RIGHT.search(line)
    name_match = PATTERN_WORDGRAPH_NAME.search(line)
    score_match = PATTERN_WORDGRAPH_SCORE.search(line)
    idx, start, end = idxts_match.groups()
    start = float(start)
    end = float(end)
    left = tuple()
    right = tuple()
    if left_match:
        left = tuple(int(i) for i in left_match.group(1).split(','))
    if right_match:
        right = tuple(int(i) for i in right_match.group(1).split(','))
    return WordGraphData(
        int(idx),
        name_match.group(1),
        round(start / 100, 3),
        round(end / 100, 3),
        left, right,
        round((end - start) / 100, 3),
        min(1., float(score_match.group(1)))
    )


def find_sentence_path(sentence, wordgraphs):
    sentence_len = len(sentence)

    wordpath = []
    wgword_indices_stack = []
    sentence_index_stack = []

    sentence_index = 0
    wgword_indices = [w.index for w in wordgraphs if not w.left]
    while sentence_index < sentence_len and \
            wgword_indices_stack or wgword_indices:
        if wgword_indices:
            wgidx = wgword_indices.pop()
            wordgraph = wordgraphs[wgidx]
            isleaf = not wordgraph.right
            is_sentence_end = sentence_index + 1 == sentence_len
            wordname = wordgraph.name
            if isleaf is not is_sentence_end and wordname != '':
                # not both reached ends
                continue
            prevword = (
                sentence[sentence_index - 1]
                if sentence_index > 0 else ''
            )
            curword = sentence[sentence_index]
            if wordname in ('', prevword, curword):
                wordpath.append(wgidx)
                wgword_indices_stack.append(wgword_indices)
                sentence_index_stack.append(sentence_index)
                wgword_indices = list(wordgraph.right)
                if wordname == curword:
                    sentence_index += 1
        else:
            # dead end, return to previous step
            wordpath.pop()
            wgword_indices = wgword_indices_stack.pop()
            sentence_index = sentence_index_stack.pop()

    pointer = 0
    curword = sentence[pointer]
    result_words = []
    merge_to_prev = False
    for idx in wordpath:
        wordgraph = wordgraphs[idx]
        wordtext = wordgraph.name
        if wordtext not in ('', curword) or merge_to_prev:
            start, end, duration, name, score = result_words[-1]
            result_words[-1] = Word(
                start, wordgraph.end,
                round(wordgraph.end - start, 3),
                wordgraph.name, wordgraph.score)
            merge_to_prev = False
        elif wordtext in ('', curword):
            result_words.append(Word(
                wordgraph.start,
                wordgraph.end,
                wordgraph.duration,
                wordgraph.name,
                wordgraph.score
            ))
            pointer += 1
            curword = sentence[pointer] if pointer < sentence_len else ''
            merge_to_prev = wordtext == ''
    return result_words


def read_julius_result(path, dynamic_timeout):
    cur_sentence = []
    wordgraphs = []
    in_wordgraph_data = False
    for line in follow_file(path, dynamic_timeout):
        line = line.strip()
        if '<input rejected by short input>' in line:
            yield None, None

        elif line.startswith('sentence1'):
            match = PATTERN_SENTENCE.match(line)
            cur_sentence = match.group(1).split()
            wordgraphs = []
        elif line.startswith('--- begin wordgraph data ---'):
            in_wordgraph_data = True
        elif line.endswith('--- end wordgraph data ---'):
            in_wordgraph_data = False
            words = find_sentence_path(cur_sentence, wordgraphs)
            yield cur_sentence, words
        elif in_wordgraph_data:
            wordgraphs.append(parse_wordgraph_data(line))


def main():
    if len(sys.argv) != 5:
        print('Usage: {} <INPUTINDEX> <ADINTOOL_RESULT> '
              '<JULIUS_RESULT> <OUTPUTINDEX>'
              .format(sys.argv[0]), file=sys.stderr)
        exit(1)
    inputindex, adintool_result, julius_result, outputindex = sys.argv[1:]
    outputdir = os.path.dirname(outputindex)

    inputindex = read_inputindex(inputindex)
    dynamic_timeout = [0]  # infinite time by default
    julius_result = read_julius_result(julius_result, dynamic_timeout)
    with open(outputindex, 'wb') as outputindex:
        for wavfile, in_duration, in_offset in inputindex:
            jsonfile = os.path.splitext(wavfile)[0] + '.json'
            with open(os.path.join(outputdir, jsonfile), 'wb') as fp:
                transcripts = []
                adintool_stream = read_adintool_result(
                    adintool_result, dynamic_timeout)
                entered = False
                for audiopath, start_time, duration in adintool_stream:
                    _, audiopath = os.path.split(audiopath)
                    if audiopath != wavfile:
                        if entered:
                            break
                        else:
                            continue
                    entered = True
                    sentence, words = next(julius_result)
                    # first sentence generated,
                    # don't tolerent more than 2 + 2x remaining duration delays
                    dynamic_timeout[0] = 2 + \
                                         (in_duration - duration - start_time) * 2
                    if not sentence or not words:
                        continue
                    sentence_duration = words[-1].end - words[0].start
                    if sentence_duration > duration:
                        print(
                            'Warning: sentence duration longer than chunk '
                            'duration may indicate mimatches: {} {} ({} > {})'
                                .format(
                                audiopath, ' '.join(sentence),
                                sentence_duration, duration
                            ),
                            file=sys.stderr
                        )
                    transcripts.append({
                        'stime': in_offset + start_time,
                        'duration': sentence_duration,
                        'content': ' '.join(sentence),
                        'word_chunks': [{
                            'stime':
                                round(in_offset + w.start + start_time, 3),
                            'duration': w.duration,
                            'content': w.text,
                            'confidence': w.confidence
                        } for w in words]
                    })
                json.dump(transcripts, fp, indent=2)
            outputindex.write(
                '{} {} {}\n'.format(jsonfile, in_duration, in_offset))
            outputindex.flush()
            # starts a new file, give infinite time for process
            dynamic_timeout[0] = 0
        outputindex.write('__done__ -1 -1\n')


if __name__ == '__main__':
    main()
