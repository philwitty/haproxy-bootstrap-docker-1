FROM phusion/baseimage:0.9.18

RUN add-apt-repository ppa:vbernat/haproxy-1.6

RUN apt-get update && \
    apt-get install -y \
        haproxy \
        git \
        openssl \
        python3 \
        python3-pip && \
    apt-get clean
RUN pip3 install \
    pyyaml==3.11 \
    git+git://github.com/curoo/expend-python-commons.git@master#egg=ex_py_commons

ADD bootstrap.py /bootstrap/bootstrap.py

ADD ./scripts/haproxy.sh /etc/service/haproxy/run

ADD ./scripts/haproxy-log.conf /etc/syslog-ng/conf.d/haproxy.conf
