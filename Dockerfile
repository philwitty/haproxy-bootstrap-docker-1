FROM haproxy:1.6

RUN apt-get update && \
    apt-get install -y \
        git \
        openssl \
        python3 \
        python3-pip && \
    apt-get clean
RUN pip-3.2 install \
    pyyaml==3.11 \
    git+git://github.com/curoo/expend-python-commons.git@master#egg=ex_py_commons

ADD bootstrap.py /bootstrap/bootstrap.py

CMD python3 /bootstrap/bootstrap.py && haproxy -f /bootstrap/haproxy.cfg
