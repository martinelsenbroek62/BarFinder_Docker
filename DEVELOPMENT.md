# Development Document

## Directories and files

- `api_collection`: Main backend code. Written in Python (Flask framework). Includes:
  - `apis`: implementation of all HTTP RESTful APIs
    - `__init__.py`: Where we register all RESTful APIs to Flask
    - `access_token.py`: User authorization
    - `convert_audio.py`:
      Submit an audio and create processing task (POST),
      and retrieve processing result (GET)
    - `task_subscription.py`:
      Subscript multiple processing tasks (POST, tasks must previously created by `convert_audio`),
      and retrieve multiple processing results (GET)
    - `usage_stat.py`: Fetch usage results
  - `socketio_apis`: implementation of all SocketIO APIs
    - `__init__.py`: Where we register all SocketIO APIs to Flask
    - `livestream.py`:
      Implementation of server side live streaming decoding process. You can find a simple
      client implementation at `examples/livestream.html` and `examples/livestream.png`.
  - `commands`: Commands created for `flask-cli`:
    - `users.py`: Create user, change user password
  - `engines`: Implementation of Python calling decoding engines
  - `models`: Implenetation of SQLAlchemy database tables
- `deployment`: Code for deployment
- `dial_frontend`: Code of frontend. Where the "sandbox" is.
- `engine_dial`, `engine_kaldi`, `engine_langcf`, `engine_julius`:
  Where the decoding engines are. We have created stable environment for all these engines
  using Docker.


## General usage

All following commands are defined in `Makefile`:

### Build engines

```bash
make build-dial
make build-kaldi
make build-julius
```

### Build frontend & backend

```bash
make build
```

### Build frontend & backend and start service

```bash
make up
```

## Development environment

You need to have Docker installed for backend, NPM + yarn installed for frontend.

For backend we don't recommend to run directly using Python. We recommend using Docker:

```bash
make up log
```

(The Docker command can be found in `Makefile`)

For frontend we recommend using NPM + yarn to start environment for debugging:

```bash
cd dial_frontend
yarn install
yarn start
```


## Deployment

All necessary deployment code including AWS credential are located in `deployment`
directory.

DON'T MAKE THIS REPOSITORY PUBLIC OR YOU'LL EXPOSE AWS CREDENTIALS!!!

The credential is located in `deployment/env.sh`.

To deployment to aws-cpu.xcellence.tech server:

```bash
cd deployment
make deploy-cpu
```

## Build engine Docker images

All engine Docker images building process are recorded in `Makefile` located in
the corresponding subdirectory. The command is usually `make build` but you are
encourage to read the `Makefile` before you run any command. Alternatively, you
can build and push the latest engine images to AWS ECR in `deployment` directory:

```bash
cd deployment
make release
```


## AWS Admin

You need username and password to access Authenticity's AWS account. Please ask
Peter for this information.
