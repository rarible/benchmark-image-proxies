FROM debian:bullseye

RUN apt-get update -y && \
    apt-get install --no-install-recommends -y python3 python3-pip python3-dev python3-pycurl gcc g++ libboost-python-dev libexiv2-dev libcairo2 && \ 
    rm -rf /var/lib/apt /var/lib/dpkg/info /var/cache/* /var/log/*

RUN ln -s /usr/lib/x86_64-linux-gnu/libboost_python39.so /usr/lib/libboost_python3.so

RUN pip install thumbor[all]

ADD thumbor.conf /

CMD thumbor -c thumbor.conf