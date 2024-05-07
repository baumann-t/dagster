#!/bin/bash

PROJECT_ID="dagster-420313"
IMAGE_NAME="dagster"
FOLDER_NAME="dagster"
REGION="northamerica-northeast1"
JOB_NAME="dagster-job"

echo "Building Docker image..."
docker build -t $IMAGE_NAME . --platform=linux/amd64

echo "Tag image"
docker tag $IMAGE_NAME $REGION-docker.pkg.dev/$PROJECT_ID/$FOLDER_NAME/$IMAGE_NAME:latest

echo "Pushing image to Google Artifact Registry..."
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$FOLDER_NAME/$IMAGE_NAME:latest

echo "Creating Cloud Run job..."
gcloud beta run jobs create $JOB_NAME \
    --image=$REGION-docker.pkg.dev/$PROJECT_ID/$FOLDER_NAME/$IMAGE_NAME:latest \
    --region=$REGION \
    --service-account=$SERVICE_ACCOUNT \
    --project=$PROJECT_ID

echo "Cloud Run job created successfully."