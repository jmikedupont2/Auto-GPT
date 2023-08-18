# Use an official Python base image from the Docker Hub
# Add --platform=linux/amd64 for the M1 Mac (https://stackoverflow.com/a/71611002)
FROM --platform=linux/amd64 python:3.10

# Install browsers
RUN apt-get update && apt-get install -y \
    chromium-driver firefox-esr \
    ca-certificates

# Install utilities
RUN apt-get install -y curl jq wget git

# Declare working directory
WORKDIR /workspace/Auto-GPT
