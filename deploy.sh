#!/bin/bash
set -e

IMAGE=gcr.io/$PROJECT/scene-generator-$ENVIRONMENT
docker build -t $IMAGE .
docker push $IMAGE

helm upgrade --install scene-generator ./helm \
    --namespace=air-tracker-$ENVIRONMENT --create-namespace \
    --set scenes_api_url=$SCENES_API_URL \
    --set loguru_level=$LOGURU_LEVEL \
    --set image=$IMAGE
