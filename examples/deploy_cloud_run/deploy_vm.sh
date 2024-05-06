#!/bin/bash

# Variables
VM_NAME="dagster-vm"
ZONE="northamerica-northeast1-a"
PROJECT_ID="dagster-420313"
LOCAL_FILE_PATH="./vm_config/*"
DAGSTER_GCP_PATH="../../python_modules/libraries/dagster-gcp/*"
REMOTE_DAGSTER_GCP_PATH="/opt/dagster/app/python_modules/libraries/dagster_gcp"
REMOTE_DIR="/opt/dagster/app"

# Create a Google Cloud VM instance
gcloud compute instances create $VM_NAME \
    --zone=$ZONE \
    --machine-type=e2-micro \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --project=$PROJECT_ID

# echo "waiting for VM to be created..."
# sleep 10

gcloud compute ssh $VM_NAME --zone=$ZONE --command="
    sudo mkdir -p $REMOTE_DIR $REMOTE_DAGSTER_GCP_PATH
    sudo chown -R $USER $REMOTE_DIR $REMOTE_DAGSTER_GCP_PATH
" --project=$PROJECT_ID


gcloud compute scp $LOCAL_FILE_PATH ${VM_NAME}:$REMOTE_DIR \
    --zone=$ZONE \
    --project=$PROJECT_ID

gcloud compute scp --recurse $DAGSTER_GCP_PATH ${VM_NAME}:$REMOTE_DAGSTER_GCP_PATH \
    --zone=$ZONE \
    --project=$PROJECT_ID

# SSH into the VM and run setup commands
gcloud compute ssh $VM_NAME --zone=$ZONE --command="
    # Update package list and install prerequisites
    sudo apt-get update
    sudo apt-get install -y python3.10 python3-venv python3-pip python3.10-distutils

    python3 -m pip install --upgrade pip

    # Create and activate a virtual environment with Python 3.10
    python3 -m venv .venv
    source .venv/bin/activate

    # Install Dagster
    pip install dagster-postgres dagster-webserver
    # install dagster-gcp
    pip install $REMOTE_DAGSTER_GCP_PATH

    echo 'installed dagster'

    export DAGSTER_HOME=$REMOTE_DIR
    cd $REMOTE_DIR


    echo 'starting dagster daemon'
    # Start the Dagster daemon
    nohup dagster-daemon run &

    echo 'starting dagster daemon webserver'
    # Start the dagster webserver
    nohup dagster-webserver -h 0.0.0.0 -p 3000


" --project=$PROJECT_ID
