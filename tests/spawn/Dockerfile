FROM ubuntu:24.04

# Install necessary packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    sudo \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create rebbe user with sudo privileges
RUN useradd -m rebbe && \
    echo "rebbe ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/rebbe && \
    chmod 0440 /etc/sudoers.d/rebbe

# Set up working directory
WORKDIR /home/rebbe

# Switch to rebbe user
USER rebbe

# Set environment variables
ENV PATH="/home/rebbe/.local/bin:${PATH}"

# Default command
CMD ["/bin/bash"]
