# syntax=docker/dockerfile:1
#
# reposcan with Gitleaks and Semgrep, for running scans in an isolated container:
#
#   docker build -t reposcan .
#   docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
#     --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,noexec,nosuid,size=256m \
#     -v "$PWD":/src:ro -v "$PWD/out":/out reposcan \
#     scan /src --scanners gitleaks,semgrep --output-dir /out
#
# Trivy and OSV-Scanner are deliberately NOT included: they need their vulnerability databases
# (network on first use), which is the opposite of what an isolated container is for. Base images
# are pinned by digest (resolved 2026-10-17 through mirror.gcr.io); refresh them on a schedule.

FROM golang:1.24@sha256:d2d2bc1c84f7e60d7d2438a3836ae7d0c847f4888464e7ec9ba3a1339a1ee804 AS gitleaks
# Gitleaks 8.30.1 needs a newer Go than the base image; the toolchain is fetched at build time only.
ENV GOTOOLCHAIN=auto GOBIN=/out CGO_ENABLED=0
RUN go install -ldflags "-s -w -X github.com/zricethezav/gitleaks/v8/version.Version=8.30.1" \
    github.com/zricethezav/gitleaks/v8@v8.30.1

FROM python:3.14-slim@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONDONTWRITEBYTECODE=1 \
    HOME=/tmp SEMGREP_ENABLE_VERSION_CHECK=0 SEMGREP_SEND_METRICS=off
RUN pip install "semgrep==1.181.0"
COPY --from=gitleaks /out/gitleaks /usr/local/bin/gitleaks
COPY . /build
RUN pip install /build && rm -rf /build
# A one-shot CLI, not a service: say so explicitly (also what Trivy check DS-0026 asks for).
HEALTHCHECK NONE
USER 65532:65532
WORKDIR /tmp
ENTRYPOINT ["reposcan"]
CMD ["--help"]
