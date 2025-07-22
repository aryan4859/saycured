# Base image
FROM ubuntu:22.04

ARG GECKOVERSION=0.33.0
ARG GOVERSION=1.21.5

# Check supported architecture
RUN ARCH=$(dpkg --print-architecture) \
    && if [ "$ARCH" != "arm64" ] && [ "$ARCH" != "amd64" ]; then \
        echo "saycuRed not supported, encountered unknown architecture: $ARCH" && exit 1; \
    fi

# Labels and Credits
LABEL \
    name="saycuRed" \
    author="saycured" \
    description="Saycured is an ML-powered web vulnerability scanner that detects and classifies security flaws intelligently."

# Environment Variables
ENV DEBIAN_FRONTEND="noninteractive" \
    DATABASE="postgres" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GOROOT="/usr/local/go" \
    GOPATH="/root/go" \
    PATH="${PATH}:/usr/local/go/bin:/root/go/bin"

# Install dependencies
RUN apt update -y && apt install -y --no-install-recommends \
    python3.10 python3-dev python3-pip \
    build-essential cmake geoip-bin geoip-database gcc git libpq-dev \
    libpango-1.0-0 libpangoft2-1.0-0 libpcap-dev netcat nmap \
    x11-utils xvfb wget curl python3-netaddr software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Install gnupg2 and dirmngr needed for add-apt-repository
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg2 \
    dirmngr \
    software-properties-common

# Add the Mozilla team PPA
RUN add-apt-repository -y ppa:mozillateam/ppa

# Install Go
RUN ARCH=$(dpkg --print-architecture) \
    && curl -L https://go.dev/dl/go${GOVERSION}.linux-${ARCH}.tar.gz | tar -xzC /usr/local

# Install geckodriver 
RUN ARCH=$(dpkg --print-architecture) \
    && if [ "$ARCH" = "arm64" ]; then \
        GECKOPATH="geckodriver-v${GECKOVERSION}-linux-aarch64.tar.gz"; \
    elif [ "$ARCH" = "amd64" ]; then \
        GECKOPATH="geckodriver-v${GECKOVERSION}-linux64.tar.gz"; \
    else \
        echo "Unsupported arch $ARCH"; exit 1; \
    fi \
    && wget https://github.com/mozilla/geckodriver/releases/download/v${GECKOVERSION}/$GECKOPATH \
    && tar -xvf $GECKOPATH \
    && rm $GECKOPATH \
    && mv geckodriver /usr/bin

# Install Rust for orjson
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN pip3 install maturin

# Prepare work directory
WORKDIR /usr/src/app

# Install Go-based recon tools
ENV GO111MODULE=on 
RUN printf "\
    github.com/jaeles-project/gospider@latest\n\
    github.com/tomnomnom/gf@latest\n\
    github.com/tomnomnom/unfurl@latest\n\
    github.com/tomnomnom/waybackurls@latest\n\
    github.com/projectdiscovery/httpx/cmd/httpx@latest\n\
    github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest\n\
    github.com/projectdiscovery/chaos-client/cmd/chaos@latest\n\
    github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest\n\
    github.com/projectdiscovery/naabu/v2/cmd/naabu@latest\n\
    github.com/hakluke/hakrawler@latest\n\
    github.com/lc/gau/v2/cmd/gau@latest\n\
    github.com/owasp-amass/amass/v3/...@latest\n\
    github.com/ffuf/ffuf@latest\n\
    github.com/projectdiscovery/tlsx/cmd/tlsx@latest\n\
    github.com/hahwul/dalfox/v2@latest\n\
    github.com/projectdiscovery/katana/cmd/katana@latest\n\
    github.com/dwisiswant0/crlfuzz/cmd/crlfuzz@latest\n\
    github.com/sa7mon/s3scanner@latest\n" | \
    xargs -L1 go install -ldflags="-s -w" -v \
    && rm -rf /go/pkg/* && rm -rf /root/.cache/go-build

# Update Nuclei and Chaos
RUN nuclei -update-templates
RUN chaos -update

# Install Python dependencies
COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade setuptools==72.1.0
RUN pip3 install -r /tmp/requirements.txt --no-cache-dir

# Additional Python tools
RUN pip3 install --no-cache-dir \
    fuzzywuzzy \
    selenium==4.9.1 \
    python-Levenshtein \
    pyvirtualdisplay \
    netaddr

# Copy project files
COPY . /usr/src/app/
