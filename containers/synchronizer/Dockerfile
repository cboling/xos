FROM       adtran/xos

# Supervisor
COPY conf/synchronizer.conf /etc/supervisor/conf.d/

ENV PYTHONPATH /usr/local/lib/python2.7/site-packages:/usr/lib/python2.7/dist-packages:/opt/xos:/usr/local/lib/python2.7/site-packages/pydevd
ENV TERM xterm

CMD /usr/bin/supervisord -c /etc/supervisor/conf.d/synchronizer.conf
