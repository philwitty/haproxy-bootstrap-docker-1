#!/bin/sh
set -e

DOCKER=`sh /etc/profile; which docker`
GIT=`sh /etc/profile; which git`

DOCKER_REGISTRY="docker-registry.expend.io"
IMAGE_NAME="haproxy-bootstrap-docker"
BUILD_NUMBER=`$GIT rev-list HEAD --count`
echo "BUILD NUMBER "$BUILD_NUMBER

IMAGE_TAG=${DOCKER_REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER}
LATEST_TAG=${DOCKER_REGISTRY}/${IMAGE_NAME}:latest
"${DOCKER}" build -t ${IMAGE_TAG} .
"${DOCKER}" tag -f ${IMAGE_TAG} ${LATEST_TAG}
echo "..docker build ${IMAGE_TAG} completed"


if [ "$DRONE_BRANCH" = "master" ] && [ "$DRONE_PULL_REQUEST" = "" ]; then
    "${DOCKER}" push ${IMAGE_TAG}
    "${DOCKER}" push ${LATEST_TAG}
    echo "..docker push ${IMAGE_TAG} completed"
fi

# Cleanup the image to avoid space leakage
"${DOCKER}" rmi $(docker images -q ${DOCKER_REGISTRY}/${IMAGE_NAME} | head -n 1)

# Cleanup eventual dangling images
images=$("${DOCKER}" images -f "dangling=true" -q)
if [ -n "$images" ]; then
    "${DOCKER}" rmi $images
fi
