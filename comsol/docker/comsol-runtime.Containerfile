FROM python:3.11-slim-bookworm AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get -o Acquire::Retries=5 -o Acquire::http::Timeout=30 update \
    && apt-get -o Acquire::Retries=5 -o Acquire::http::Timeout=30 install -y --no-install-recommends \
    bash \
    ca-certificates \
    fontconfig \
    libasound2 \
    libglib2.0-0 \
    libgomp1 \
    libnss3 \
    libx11-6 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxinerama1 \
    libxrandr2 \
    libxrender1 \
    libxtst6 \
    procps \
    tar \
    unzip \
    && rm -rf /var/lib/apt/lists/*

COPY Setup/ /tmp/comsol-setup/
COPY setupconfig-docker.ini /tmp/setupconfig-docker.ini

RUN --mount=type=secret,id=comsol_license,target=/run/secrets/comsol_license,required=false \
    bash -lc ' \
      mkdir -p /usr/share/applications; \
      chmod +x /tmp/comsol-setup/setup; \
      set +e; \
      /tmp/comsol-setup/setup -s /tmp/setupconfig-docker.ini > /tmp/comsol-install.log 2>&1; \
      status=$?; \
      if [ "$status" -ne 0 ]; then \
        echo "COMSOL installer failed with exit ${status}"; \
        find /tmp -maxdepth 2 -type f \( -name "*.log" -o -name "*.txt" -o -name "*.ini" \) -print; \
        for f in /tmp/comsol-install.log /tmp/*.log /tmp/*/*.log; do \
          if [ -f "$f" ]; then \
            echo "===== $f ====="; \
            tail -n 200 "$f"; \
          fi; \
        done; \
        exit "$status"; \
      fi; \
      set -e; \
      find /opt/comsol -iname "license.dat" -o -iname "license.trial" -o -iname "licenseinfo.ini" | xargs -r rm -f; \
      rm -rf /tmp/comsol-setup /tmp/setupconfig-docker.ini /tmp/comsol-install.log; \
    '

FROM builder AS runtime

ENV DEBIAN_FRONTEND=noninteractive
ENV COMSOL_ROOT=/opt/comsol/COMSOL63/Multiphysics
ENV PATH=/opt/comsol/COMSOL63/Multiphysics/bin:${PATH}

RUN ln -sf /opt/comsol/COMSOL63/Multiphysics/bin/comsol /usr/local/bin/comsol \
    && python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir numpy scipy pandas matplotlib h5py meshio mph JPype1 \
    && find /opt/comsol -iname 'license.dat' -o -iname 'license.trial' -o -iname 'licenseinfo.ini' | xargs -r rm -f

WORKDIR /work

CMD ["comsol", "-version"]
