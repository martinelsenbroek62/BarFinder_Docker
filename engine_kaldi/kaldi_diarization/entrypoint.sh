#! /bin/bash

. ./cmd.sh
. ./path.sh
set -e

# inputs
audio_path=$1
segment_path=$2
window=1.5
period=0.75
min_segment=0.5
target_energy=0.9
cluster_mode=$4  # 0~threshold cluster 1~number based cluster
threshold=0.25
num_speaker=$5

# configs
name=diaaudio
nnet_dir=exp/xvector_nnet_1a
plda_name=xvectors_callhome2

nj=1
stage=1

if [ $stage -le 1 ]; then

  # stage 1: initial file preparation
  mkdir -p data/$name 
  # segments
  cp $segment_path data/$name
  # wav.scp 
  echo "sample $audio_path" > data/$name/wav.scp
  # utt2spk
  awk {'print $1 " " $2'} data/$name/segments > data/$name/utt2spk
  # spk2utt
  #utils/fix_data_dir.sh data/$name
  utils/utt2spk_to_spk2utt.pl data/$name/utt2spk > data/$name/spk2utt

  steps/make_mfcc.sh --mfcc-config conf/mfcc.conf --nj $nj data/$name
  echo "[INFO] initial file preparation complete"

fi

if [ $stage -le 2 ]; then

  # stage 2: cmvn for segmented data
  local/nnet3/xvector/prepare_feats.sh --nj $nj \
    data/$name data/${name}_cmn exp/${name}_cmn
  cp data/$name/segments data/${name}_cmn/ 
  echo "[INFO] cmvn calculated for segmented data complete"

fi

if [ $stage -le 3 ]; then
  # stage 3: embedding
  diarization/nnet3/xvector/extract_xvectors.sh --nj $nj \
    --window $window --period $period --apply-cmn false --min-segment $min_segment \
    $nnet_dir data/${name}_cmn/ $nnet_dir/xvectors_${name}
  echo "[INFO] embedding complete"
fi

if [ $stage -le 4 ]; then
  # stage 4: plda scoring
  diarization/nnet3/xvector/score_plda.sh --target-energy $target_energy --nj $nj \
    $nnet_dir/$plda_name $nnet_dir/xvectors_${name} \
    $nnet_dir/xvectors_${name}/plda_scores
  echo "[INFO] plda scoring complete"
fi

if [ $stage -le 5 ]; then
  # stage 5: clustering and report result

  mkdir -p result

  if [ $cluster_mode -eq 0 ]; then
    echo "[INFO] start threshold based clustering..."
    diarization/cluster.sh --nj $nj --threshold $threshold \
      $nnet_dir/xvectors_${name}/plda_scores \
      $nnet_dir/xvectors_${name}/plda_scores_threshold_${threshold}
    cp $nnet_dir/xvectors_${name}/plda_scores_threshold_${threshold}/rttm result/
  else
    echo "[INFO] start cluster number based clustering..."
    echo "sample $num_speaker" > data/${name}_cmn/reco2num_spk
    diarization/cluster.sh --nj $nj --reco2num-spk data/${name}_cmn/reco2num_spk \
      $nnet_dir/xvectors_${name}/plda_scores \
      $nnet_dir/xvectors_${name}/plda_scores_num_speakers
    cp $nnet_dir/xvectors_${name}/plda_scores_num_speakers/rttm result/
  fi
  echo "[INFO] clustering complete"
fi

cp result/rttm $3
