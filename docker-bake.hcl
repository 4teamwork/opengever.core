/*
# To build locally use:
GIT_SHA_TAG=$(git describe --tags) \
GIT_TAG=$(git describe --tags --candidates=0) \
LATEST_TAG=$(git describe --tags --abbrev=0 master) \
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD) \
docker buildx bake -f docker-bake.hcl --load
*/

variable "OGCORE_IMAGE" {
  default = "docker.io/4teamwork/ogcore"
}
variable "OGTESTSERVER_IMAGE" {
  default = "docker.io/4teamwork/ogtestserver"
}
variable "OGSOLR_IMAGE" {
  default = "docker.io/4teamwork/ogsolr"
}
variable "GIT_TAG" {
  default = ""
}
variable "GIT_SHA_TAG" {
  default = ""
}
variable "LATEST_TAG" {
  default = ""
}
variable "BRANCH_NAME" {
  default = ""
}
variable "OGSOLR_VERSION" {
  default = "9.10.1"
}
variable "OGSOLR_VERSION_SUFFIX" {
  default = ""
}

group "default" {
  targets = ["ogcore"]
}

target "ogcore" {
  dockerfile = "./docker/core/Dockerfile"
  context = "."
  tags = [
    strlen(GIT_TAG) > 0 ? "${OGCORE_IMAGE}:${GIT_TAG}" : "",
    equal(GIT_TAG, LATEST_TAG) ? "${OGCORE_IMAGE}:latest" : "",
    equal(GIT_TAG, "") && equal(BRANCH_NAME, "master") ? "${OGCORE_IMAGE}:edge" : "",
    notequal(BRANCH_NAME, "master") && strlen(GIT_TAG) < 1 ? "${OGCORE_IMAGE}:${GIT_SHA_TAG}" : "",
  ]
  platforms = [
    "linux/amd64",
    strlen(GIT_TAG) > 0 ? "linux/arm64" : "",
  ]
  secret = [
    {
      type = "env"
      id = "gldt"
      env = "GITLAB_DEPLOY_TOKEN"
    }
  ]
}

target "ogtestserver" {
  args = {
    OGCORE_VERSION = strlen(GIT_TAG) > 0 ? "${GIT_TAG}" : equal(BRANCH_NAME, "master") ? "edge" : "${GIT_SHA_TAG}",
  }
  dockerfile = "./docker/testserver/Dockerfile"
  context = "."
  tags = [
    strlen(GIT_TAG) > 0 ? "${OGTESTSERVER_IMAGE}:${GIT_TAG}" : "",
    equal(GIT_TAG, LATEST_TAG) ? "${OGTESTSERVER_IMAGE}:latest" : "",
    equal(GIT_TAG, "") && equal(BRANCH_NAME, "master") ? "${OGTESTSERVER_IMAGE}:edge" : "",
    notequal(BRANCH_NAME, "master") && strlen(GIT_TAG) < 1 ? "${OGTESTSERVER_IMAGE}:${GIT_SHA_TAG}" : "",
  ]
  platforms = [
    "linux/amd64",
    strlen(GIT_TAG) > 0 ? "linux/arm64" : "",
  ]
  secret = [
    {
      type = "env"
      id = "gldt"
      env = "GITLAB_DEPLOY_TOKEN"
    }
  ]
}

target "ogsolr" {
  args = {
    SOLR_VERSION = "${OGSOLR_VERSION}",
  }
  dockerfile = "./docker/solr/Dockerfile"
  context = "."
  tags = [
    "${OGSOLR_IMAGE}:${OGSOLR_VERSION}${OGSOLR_VERSION_SUFFIX}",
  ]
  platforms = [
    "linux/amd64",
    "linux/arm64",
  ]
}
