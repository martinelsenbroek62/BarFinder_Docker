## Steps

1. Edit `sources.yml` to include Youtube users/playlists you want to include.
2. Use `download-youtube.sh` to download video. (hint: run multiple `download-youtube.sh` on diffierent users/playlists simultaneously can save you some time).
3. In `shared` folder, create `training_data` and `spectrogram_data` folder. In `training_data` folder create language folders. In language folders, create symlinks to Youtube language folders. For example:
   ```sh
   cd training_data/
   mkdir chinese/
   mkdir english/
   cd chinese/
   ln -s ../../raw/chinese
   cd ../english/
   ln -s ../../raw/english
   ```
4. Use `wav_to_spectrogram.sh` to convert WAV file to PNG images.
5. Edit `config.yaml` file. This file is corresponding to `crnn-lid/keras/config.yaml`.
6. Run `train.sh` and wait for the result. This step requires as many as CPUs you have. It requires about 20GB RAM.
