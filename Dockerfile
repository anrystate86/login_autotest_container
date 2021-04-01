FROM oraclelinux:7-slim

LABEL maintainer="nazarov.andrey@otr.ru" \
    org.label-schema.schema-version="1.0" \
    org.label-schema.build-date=$BUILD_DATE \
    org.label-schema.vcs-ref=$VCS_REF \
    org.label-schema.name="autotest_image" \
    org.label-schema.description="zabbix autotest image with devcron, " \
    org.label-schema.url="https://git" \
    org.label-schema.vcs-url="https://git" \
    org.label-schema.vendor=""

RUN yum install -y wget && \
    wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && \
    rpm -i epel-release-latest-7.noarch.rpm && \
    rm epel-release-latest-7.noarch.rpm && \
    yum install -y \
    rsync \
    python3 \
    libxcb \
    http://mirror.centos.org/centos/7/os/x86_64/Packages/vulkan-filesystem-1.1.97.0-1.el7.noarch.rpm \
    http://mirror.centos.org/centos/7/os/x86_64/Packages/vulkan-1.1.97.0-1.el7.x86_64.rpm \
    https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm && \
    pip3 install urllib3 devcron && \
    mkdir /build

COPY . /build/

RUN chmod +x /build/ufos_autotest.py && \
    chmod +x /build/chromedriver && \
    cd /build && \
    python3 crontab_make.py
#ENTRYPOINT ["/build"]
CMD ["devcron.py","/build/crontab"]