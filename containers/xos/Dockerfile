FROM xosproject/xos-base

# Include certificates from Openstack
ADD local_certs.crt /usr/local/share/ca-certificates/local_certs.crt
RUN update-ca-certificates

# Install and boostrap XOS and Tosca
ENV XOS_GIT_REPO https://github.com/cboling/xos.git
ENV XOS_GIT_BRANCH master

RUN git clone $XOS_GIT_REPO -b $XOS_GIT_BRANCH /tmp/xos && \
    mv /tmp/xos/xos /opt/ && \
    chmod +x /opt/xos/tools/xos-manage && \
    /opt/xos/tools/xos-manage genkeys

EXPOSE 8000

# Set environment variables
ENV HOME /root
ENV PYTHONPATH /usr/local/lib/python2.7/site-packages:/usr/lib/python2.7/dist-packages:/opt/xos:/usr/local/lib/python2.7/site-packages/pydevd
ENV TERM xterm

# Define working directory
WORKDIR /opt/xos

# Define default command
CMD python /opt/xos/manage.py runserver 0.0.0.0:8000 --insecure --makemigrations

