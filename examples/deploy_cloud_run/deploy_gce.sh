#!/bin/bash

# Variables
VM_NAME="dagster-vm"
ZONE="northamerica-northeast1-1"
PROJECT_ID="dagster-420313"
LOCAL_FILE_PATH="/path/to/your/local/config/files"
REMOTE_DIR="/opt/dagster/app"
STARTUP_SCRIPT="startup-script.sh"

# Create a Google Cloud VM instance
gcloud compute instances create $VM_NAME \
    --zone=$ZONE \
    --machine-type=n1-standard-1 \
    --image-family=debian-10 \
    --image-project=debian-cloud \
    --metadata=startup-script=$STARTUP_SCRIPT \
    --project=$PROJECT_ID

# Wait for the instance to start
echo "Waiting for the instance to start..."
sleep 60

# Copy local configuration files to the VM
gcloud compute scp --recurse $LOCAL_FILE_PATH ${VM_NAME}:$REMOTE_DIR \
    --zone=$ZONE \
    --project=$PROJECT_ID

# SSH into the VM and run setup commands
gcloud compute ssh $VM_NAME --zone=$ZONE --command="
    # Install Python and pip
    sudo apt-get update
    sudo apt-get install -y python3-pip

    # Install Dagster, Dagit, and Dagster-Daemon
    pip3 install dagster dagit dagster-daemon

    # Navigate to the application directory
    cd $REMOTE_DIR

    # Start the Dagster daemon
    nohup dagster-daemon run &

    # Start the Dagit webserver
    nohup dagit -h 0.0.0.0 -p 3000 &
" --project=$PROJECT_ID

echo "Dagster is now running on the VM. Access Dagit at http://${VM_NAME}:3000"