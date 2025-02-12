FROM ubuntu:22.04

RUN mkdir /tool && \
    apt update && \
    apt -y upgrade && \
    apt -y install openjdk-11-jdk

COPY ./tools/resttestgen/ /tool/
COPY ./apis/*/specifications/* /specifications/

CMD sh /tool/config.sh && \
    cd /tool && \
    while true; do java -jar resttestgen.jar; done