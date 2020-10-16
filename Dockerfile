FROM python:3.8-slim-buster

RUN pip install flywheel-sdk flywheel_gear_toolkit~=0.1.0

COPY run.py /flywheel/v0/run.py
COPY utils /flywheel/v0/utils
# Configure entrypoint
ENTRYPOINT ["/bin/bash"]
