# Use official Dex image based on Alpine
FROM ghcr.io/dexidp/dex:v2.37.0

USER root

# Use Alpine package manager (apk) instead of apt-get
RUN apk add --no-cache gettext

USER 1000