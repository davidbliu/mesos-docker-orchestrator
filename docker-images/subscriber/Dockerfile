FROM davidbliu/etcd_base

#
# install virtualenv stuff
#
RUN pip install Flask

#
# install marathon
#
RUN pip install marathon


ADD . /opt/subscriber
WORKDIR /opt/subscriber

EXPOSE 5000

CMD python -u subscriber.py