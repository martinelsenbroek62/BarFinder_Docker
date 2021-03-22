Steps for deploying DialDocker to an AWS server

1. Install `python3` locally:
   ```sh
   sudo apt update && sudo apt install python3 python3-dev
   ```
2. Install `pip3` locally:
   ```sh
   curl https://bootstrap.pypa.io/get-pip.py | sudo python3 -
   ```
3. Install `awscli` on your local machine:
   ```sh
   sudo pip3 install awscli
   ```
4. Get your AWS credential and save it at `deployment/general/env.sh`.
   For example:
   ```sh
   #! /bin/sh
   export AWS_ACCESS_KEY_ID=AAAAAAAAAAAAAAAAA
   export AWS_SECRET_ACCESS_KEY=BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
   ```
5. Create an AWS EC2 instance:
   - System: Ubuntu 18.04
   - Minimal instance type: c5.2xlarge
   - Minimal disk volume size: 50G
   - Required accessible ports:
     - TCP 22 (0.0.0.0/0)
     - TCP 5000 (0.0.0.0/0)
     - TCP 5001 (0.0.0.0/0)
6. At the last step of creating EC2 instance, AWS will prompt you a
   dialog for creating and downloading a new SSH private key, or using
   one already exists. Either way is fine as long as you have access
   to the private key file. Save the key file locally and run this command:
   ```sh
   chmod 600 PATH/TO/AWS_PRIVATE_KEY.pem  # DO NOT run under root or use sudo
   ```
7. Allocate an Elastic IP to the EC2 instance.
8. Edit your local `~/.ssh/config` file, add following config:
   ```
   Host AN_UNIQUE_SERVER_NAME
     Hostname ELASTIC_IP_ADDRESS
     User ubuntu
     IdentityFile PATH/TO/AWS_PRIVATE_KEY.pem
   ```
   Only change all uppercase strings to corresponding values.
9. Use this command to log in the EC2 instance:
   ```
   ssh AN_UNIQUE_SERVER_NAME
   ```
   You may need to type "yes" if it's the first time you log in the server.
   The server shouldn't ask you to enter any password.
10. Once you can log in the server, follow these two documents to install
    Docker and docker-compose:
    - https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-engine---community-1
    - https://docs.docker.com/compose/install/
11. Log out from the server (by typing `exit`).
12. Run following command to deploy latest image to the server:
    ```sh
    cd deployment/general
    ./deploy-aws.sh AN_UNIQUE_SERVER_NAME
    ```
13. After the server has been deployed, wait for 1 minute.
14. Log into the server and run this to create an user:
    ```
    cd ~/DialDocker
    ./create_user.sh
    ```
15. To enable DeepSpeech engine, you need to upload the models to the server
    (for Kaldi engine the model is shipped with the Docker image). The models
    should be saved at `~/DialDocker/engine_dial/payload/models` on the server.
    After placing the model files in correct location, you should have a file
    exists at `~/DialDocker/engine_dial/payload/models/lm/en8k.trie.klm`.
16. You can then have access to the APIs. Please follow the API document to use it.
    - `http://ELASTIC_IP_ACCESS:5000/access_token`
    - `http://ELASTIC_IP_ACCESS:5000/convert_audio`
