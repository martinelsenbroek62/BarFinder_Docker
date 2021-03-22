# cython: language_level=2
"""Inferer for DeepSpeech2 model."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys

reload(sys)
sys.setdefaultencoding('UTF8')

import argparse
import os
import json
import codecs
import soundfile
import functools
from subprocess import Popen, PIPE

import paddle.v2 as paddle
from data_utils.data import DataGenerator
from model_utils.model import DeepSpeech2Model
from utils.utility import add_arguments, print_arguments
from alphabet import Alphabet

# from words import Words

parser = argparse.ArgumentParser(description=__doc__)
add_arg = functools.partial(add_arguments, argparser=parser)
# yapf: disable
add_arg('num_samples', int, 10, "# of samples to infer.")
add_arg('trainer_count', int, 4, "# of Trainers (CPUs or GPUs).")
add_arg('beam_size', int, 500, "Beam search width.")
add_arg('num_proc_bsearch', int, 5, "# of CPUs for beam search.")
add_arg('num_conv_layers', int, 2, "# of convolution layers.")
add_arg('num_rnn_layers', int, 3, "# of recurrent layers.")
add_arg('rnn_layer_size', int, 1024, "# of recurrent cells per layer.")
add_arg('alpha', float, 0.75, "Coef of LM for beam search.")
add_arg('beta', float, 1.85, "Coef of WC for beam search.")
add_arg('cutoff_prob', float, 1.0, "Cutoff probability for pruning.")
add_arg('cutoff_top_n', int, 40, "Cutoff number for pruning.")
add_arg('use_gru', bool, True, "Use GRUs instead of simple RNNs.")
parser.add_argument('--use_gpu', action='store_true', help="Use GPU or not.")
add_arg('share_rnn_weights', bool, False,
        "Share input-hidden weights across "
        "bi-directional RNNs. Not for GRU.")
parser.add_argument('--inputindex', type=str, required=True,
                    help='Index file of input wav files.')
# add_arg('wav_dir',          str,
#         'data/import/',
#         "Directory for input wav files.")
# add_arg('decode_manifest',   str,
#         'data/librispeech/manifest.dev-clean',
#         "Filepath of manifest to infer.")
add_arg('mean_std_path', str,
        './models/en8k/mean_std.npz',
        "Filepath of normalizer's mean & std.")
add_arg('vocab_path', str,
        './models/en8k/vocab.txt',
        "Filepath of vocabulary.")
add_arg('lang_model_path', str,
        './models/lm/en8k.trie.klm',
        "Filepath for language model.")
add_arg('trie_path', str,
        './model/lm/trie',
        "Filepath for trie.")
add_arg('model_path', str,
        './models/en8k/params.tar.gz',
        "If None, the training starts from scratch, "
        "otherwise, it resumes from the pre-trained model.")
add_arg('decoding_method', str,
        'ctc_beam_search',
        "Decoding method. Options: ctc_beam_search",
        choices=['ctc_beam_search'])
add_arg('error_rate_type', str,
        'wer',
        "Error rate type for evaluation.",
        choices=['wer', 'cer'])
add_arg('specgram_type', str,
        'linear',
        "Audio feature type. Options: linear, mfcc.",
        choices=['linear', 'mfcc'])
parser.add_argument('--outputindex', type=str, required=True,
                    help='Index file of result csv files.')
# add_arg('result_dir',      str,
#         './export/decode/',
#         "Directory to save decoding result csv.")
# yapf: disable
args = parser.parse_args()


def generate_manifest(wav_path, manifest_path):
    wav_data, samplerate = soundfile.read(wav_path)
    duration = float(len(wav_data)) / samplerate
    with codecs.open(manifest_path, 'w', 'utf-8') as outfp:
        json.dump({
            'audio_filepath': wav_path,
            'duration': duration,
            'text': ""  # place holder
        }, outfp)
        outfp.write('\n')
    return manifest_path


def iter_manifests(inputindex):
    inputdir = os.path.dirname(inputindex)
    try:
        proc = Popen(['tail', '-f', '-n', '+1', inputindex], stdout=PIPE)
        while True:
            audiofile, duration, offset = (
                proc.stdout.readline().strip().split())
            if audiofile.strip() == '__done__':
                break
            audioname = os.path.splitext(audiofile)[0]
            manifest_path = os.path.join(
                inputdir, '{}.manifest.userdata'.format(audioname))
            yield audioname, generate_manifest(
                os.path.join(inputdir, audiofile),
                manifest_path), duration, offset
    finally:
        proc.kill()


def decode_all(manifests):
    data_generator = DataGenerator(
        vocab_filepath=args.vocab_path,
        mean_std_filepath=args.mean_std_path,
        augmentation_config='{}',
        specgram_type=args.specgram_type,
        num_threads=1,
        keep_transcription_text=True)

    ds2_model = DeepSpeech2Model(
        vocab_size=data_generator.vocab_size,
        num_conv_layers=args.num_conv_layers,
        num_rnn_layers=args.num_rnn_layers,
        rnn_layer_size=args.rnn_layer_size,
        use_gru=args.use_gru,
        pretrained_model_path=args.model_path,
        share_rnn_weights=args.share_rnn_weights)

    # decoders only accept string encoded in utf-8
    alphabet = Alphabet(args.vocab_path)
    ds2_model.logger.info("start decoding with extended output...")
    ds2_model.init_ext_scorer(args.alpha, args.beta,
                              args.lang_model_path, args.trie_path,
                              alphabet)

    for audioname, manifest_path, duration, offset in manifests:
        try:
            duration_f = float(duration)
            if duration_f < 1.:
                yield (audioname, manifest_path,
                       None, duration, offset)
                continue
        except (TypeError, ValueError):
            pass
        batch_reader = data_generator.batch_reader_creator(
            manifest_path=manifest_path,
            batch_size=args.num_samples,
            min_batch_size=1,
            sortagrad=False,
            shuffle_method=None)

        for decode_data in batch_reader():
            probs_split = ds2_model.infer_batch_probs(
                infer_data=decode_data,
                feeding_dict=data_generator.feeding)

            # note: we only perform single file decoding
            result_transcript = ds2_model.decode_beam_search(
                probs_split=probs_split,
                beam_size=args.beam_size,
                cutoff_prob=args.cutoff_prob,
                cutoff_top_n=args.cutoff_top_n,
                alphabet=alphabet)

            yield (audioname, manifest_path,
                   result_transcript, duration, offset)


def save_decode_result(result_transcript, result_path):
    if result_transcript:
        result_transcript.save_json(result_path)
    else:
        with open(result_path, 'w') as fp:
            json.dump({
                'raw_output': '',
                'extended_output': []
            }, fp)


def main():
    print_arguments(args)
    paddle.init(use_gpu=args.use_gpu,
                rnn_use_batch=True,
                trainer_count=args.trainer_count)

    indir = os.path.dirname(args.inputindex)
    outdir = os.path.dirname(args.outputindex)
    try:
        os.makedirs(indir)
    except OSError:
        pass
    os.system('touch {}'.format(args.inputindex))
    try:
        os.makedirs(outdir)
    except OSError:
        pass

    # generate manifest using input wav files
    with codecs.open(args.outputindex, 'w', 'utf-8') as outfp:
        manifests = iter_manifests(args.inputindex)

        for (audioname, manifest_path,
             result_transcript,
             duration, offset) in decode_all(manifests):
            # save decoding
            result_filename = '{}.result.json'.format(audioname)
            save_decode_result(
                result_transcript,
                os.path.join(outdir, result_filename))
            outfp.write('{} {} {}\n'.format(result_filename, duration, offset))
            print("decoding result saved: {}.".format(result_filename))
        outfp.write('__done__ -1 -1\n')


if __name__ == '__main__':
    main()
