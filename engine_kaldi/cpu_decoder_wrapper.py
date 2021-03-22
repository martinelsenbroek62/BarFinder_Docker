#! /usr/bin/env python3
"""Xcel2 Wrapper

Usage:
  xcel2.py
    --input-audio-path=<input_audio_path>
    [--output-vlf-path=<output_vlf_path>]
    [--acoustic-scale=<acoustic_scale>]
    [--beam-width=<beam_width>]
    [--frame-subsampling-factor=<frame_subsampling_factor>]
    [--lattice-beam=<lattice_beam>]
    [--lm-scale=<lm_scale>]
    [--max-active=<max_active>]

Options:
    -h --help     Show this screen.
    --version     Show version.
"""
from docopt import docopt
import json
import os
import subprocess


def run_xcel2(input_audio_path: str,
              decode_model_path: str = "/DecodeModel",
              time_offset: int = 0,
              output_vlf_path: str = "/tmp/result-vlf.json",
              acoustic_scale: float = 1.0,
              beam_width: float = 15.0,
              frame_subsampling_factor: int = 1,
              lattice_beam: float = 6.0,
              lm_scale: float = 15.0,
              max_active: int = 7000):
    config_path = os.path.join(
        decode_model_path, "conf/online.conf"
    )
    words_path = os.path.join(
        decode_model_path, "graph_pp/words.txt"
    )
    final_model_path = os.path.join(
        decode_model_path, "final.mdl"
    )
    hclg_path = os.path.join(
        decode_model_path, "graph_pp/HCLG.fst"
    )

    command = (
        'wav-cpu-decoder '
        '--verbose=1 '
        '--online=false '
        '--do-endpointing=false '
        '--frame-subsampling-factor={frame_subsampling_factor} '
        '--config={config_path} '
        '--max-active={max_active} '
        '--beam={beam_width} '
        '--lattice-beam={lattice_beam} '
        '--acoustic-scale={acoustic_scale} '
        '--word-symbol-table={words_path} '
        '{final_model_path}  '
        '{hclg_path} '
        "'ark:echo utterance-id1 utterance-id1|' "
        "'scp:echo utterance-id1 {input_audio_path}|' "
        'ark:- | lattice-to-ctm-conf --lm-scale={lm_scale} '
        'ark: - | int2sym.pl -f 5 {words_path}'
    ).format(
        acoustic_scale=acoustic_scale,
        beam_width=beam_width,
        config_path=config_path,
        final_model_path=final_model_path,
        frame_subsampling_factor=frame_subsampling_factor,
        hclg_path=hclg_path,
        input_audio_path=input_audio_path,
        lattice_beam=lattice_beam,
        lm_scale=lm_scale,
        max_active=max_active,
        words_path=words_path
    )
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    out = out.decode("utf-8")

    vlf_output = {}
    vlf_output["series"] = []

    for line in out.split("\n"):
        if len(line) == 0:
            continue
        _, _, start, word_len, word, conf = line.split()
        start = float(start)
        end = start + float(word_len)
        start_time = start
        end_time = end
        vlf_output["series"] += [{
            "stime": start_time,
            "duration": end_time - start_time,
            "content": word,
            "confidence": conf
        }]

    with open(output_vlf_path, "w", encoding="utf-8") as out_file:
        out_file.write(json.dumps(vlf_output))

    print(json.dumps(vlf_output))


if __name__ == "__main__":
    arguments = docopt(__doc__)
    acoustic_scale_ = arguments.get("--acoustic-scale")
    beam_width_ = arguments.get("--beam-width")
    frame_subsampling_factor_ = arguments.get("--frame-subsampling-factor")
    lattice_beam_ = arguments.get("--lattice-beam")
    lm_scale_ = arguments.get("--lm-scale")
    max_active_ = arguments.get("--max-active")
    output_vlf_path_ = arguments.get("--output-vlf-path")
    kwargs = {
        "acoustic_scale": float(acoustic_scale_) if acoustic_scale_ else None,
        "beam_width": float(beam_width_) if beam_width_ else None,
        "frame_subsampling_factor": (
            float(frame_subsampling_factor_)
            if frame_subsampling_factor_ else None
        ),
        "lattice_beam": float(lattice_beam_) if lattice_beam_ else None,
        "lm_scale": float(lm_scale_) if lm_scale_ else None,
        "max_active": int(max_active_) if max_active_ else None,
        "output_vlf_path": output_vlf_path_ if output_vlf_path_ else None
    }
    kwargs = {k: v for k, v in kwargs.items() if v is not None}

    run_xcel2(
        input_audio_path=arguments["--input-audio-path"],
        **kwargs
    )
