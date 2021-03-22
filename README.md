# Usage

## Start service

1. Install `git-lfs`:
   ```shell
   sudo apt install git-lfs
   git lfs install
   ```
2. Create `docker-compose.yml` based on the template:
   ```shell
   cp docker-compose.yml.template docker-compose.yml
   editor docker-compose.yml  # just use your favorite editor
   ```
3. In `docker-compose.yml` file you just opened, find the line with "`JWT_SECRET_KEY`" and change its value to a secret random key.
   Here is a way to quickly generate a random string in Linux:
   ```shell
   cat /dev/urandom | tr -dc 'a-zA-Z0-9+/' | fold -w 40 | head -n 1
   ```
4. Place the "`models`" folder from `engine_dial_dockertest.zip` under "`engine_dial/payload/models`". The files in "`models`" folder
   should have a path like "`engine_dial/payload/models/lm/en8k.trie.klm`". Run following command to build the runtime image:
   ```shell
   make build-dial
   ```
5. Place the Kaldi tarball file (`0001_aspire_chain_model.tar.gz`) under folder `engine_kaldi`. Then run following commands:
   ```shell
   make build-kaldi
   ```
6. Run `make up` or `make run` to build the frontend Docker image and start an instance. The different between `up` and `run` is
   `run` will display Gunicorn logs. You can also edit `docker-compose.yml` file to config the app.
7. The service is now accessiable at http://localhost:5000/.

## Create user

You need to create at least one user account to retrieve the access token. After you started the service:

```shell
make create-user
```

Follow the instruction entering email and password (twice). A user will be created.

### Change password

This way will overwrite an user's password forcefully.

```shell
make change-password
```

## Retrieve access token

Once you created an user, it is quite easy to retrieve the JWT access token:

```shell
curl -F "email=<YOUR_EMAIL>" -F "password=<YOUR_PASSWORD>" http://localhost:5000/access_token
```

You will receive a JSON format response included the account email and access token.

## Access APIs using access token

To access an API required authentication, the access token must be attached with the request. For example:

```shell
   curl -H "Authorization: Bearer <TOKEN>" -F "engine=xcel-1" -F "file=@test.wav" http://localhost:5000/convert_audio
```

# APIs

## `/convert_audio`

This API requires authentication.

### POST method

Following parameters can be specified for the POST request:

- **engine**: (Required) specify the decoder engine. Accept `xcel-1` (GPU),
  `xcel-2` (GPU), `xcel-3` (CPU version of `xcel-1`), or `xcel-4` (CPU version
  of `xcel-2`)
- **file**: (Required) Audio file to be uploaded. Accept a WAV or MP3 file.
- **language**: (Optional) Language engine to be used. Accept `en` (English) or
  `zh` (Chinese Mandarin). Default value: `en`.
- **cluster_mode**: (Optional) Diarization clustering mode. Accept `0`
  (auto-detect number of speakers) or `1` (fixed number of speakers). Default
  value: `0`.
- **num_speakers**: (Optional) Number of speakers (only works when
  `cluster_mode=1`). Default value: `2`.

Examples:

```shell
   curl -H "Authorization: Bearer <TOKEN>" -F "engine=xcel-1" -F "file=@test.wav" -F "language=zh" http://localhost:5000/convert_audio
   curl -H "Authorization: Bearer <TOKEN>" -F "engine=xcel-2" -F "file=@test.wav" -F "cluster_mode=1" -F "num_speakers=4" http://localhost:5000/convert_audio
```

The JSON format response contains two values:

- **status**: `PENDING`.
- **task_url**: URL for fetching the decoding status and result.

### GET method

The GET method is provided as the **task_url** returned by POST method. For GET
method, a task ID must be placed after the entrypoint path. For example:
`/convert_audio/9b93953b-3d5b-4663-ba3a-646e5e440b56`.

A successful JSON response consistents by following values:

- **status**: `SUCCESS`.
- **task_url**: Same URL as the request.
- **task_result**:
  - **engine**: The decoder engine name. Same as the POST input.
  - **duration**: Audio total duration in seconds.
  - **filename**: Original WAV file name.
  - **transcripts**: List of transcripts grouped by speakers:
    - **speaker**: Speaker ID
    - **stime**: Audio chunk start time
    - **duration**: Audio chunk duration
    - **content**: Concatenated content of this chunk of audio
    - **word_chunks**: Timepoint of each word

For each word:
- **stime**: Start time of this word
- **duration**: Duration of this word
- **content**: The word
- **confidence**: A confidence number of the detection. Range from 0.0 to 1.0.
  

# Misc

## Access the PostgreSQL database

```shell
make psql
```

## View logs

1. API Collection logs: `docker logs dialdocker_api_1` or `make logs`
2. Celery logs: `docker logs dialdocker_celery_1`
3. RabbitMQ logs: `docker logs dialdocker_rabbitmq_1`
4. PostgreSQL logs: `docker logs dialdocker_pgdb_1`
