#FROM java:8-jdk
FROM nimmis/ubuntu:16.04

# Reference: nimmis/java:openjdk-8-jdk
# disable interactive functions
ENV DEBIAN_FRONTEND noninteractive

# set default java environment variable
ENV JAVA_VERSION_MAJOR=8 \
    JAVA_VERSION_MINOR=111 \
    JAVA_HOME=/usr/lib/jvm/default-jvm \
    PATH=${PATH}:/usr/lib/jvm/default-jvm/bin/

RUN add-apt-repository ppa:openjdk-r/ppa -y && \
    # update data from repositories
    apt-get update && \
    # upgrade OS
    apt-get -y dist-upgrade && \
    # Make info file about this build
    printf "Build of nimmis/java:openjdk-8-jdk, date: %s\n"  `date -u +"%Y-%m-%dT%H:%M:%SZ"` > /etc/BUILDS/java && \
    # install application
    apt-get install -y --no-install-recommends openjdk-8-jdk && \
    # fix default setting
    ln -s java-8-openjdk-amd64  /usr/lib/jvm/default-jvm && \
    # remove apt cache from image
    apt-get clean all

RUN java -version && \
    javac -version

# Install linux packages
RUN apt-get update
RUN apt-get -qq -y install git curl build-essential subversion perl wget unzip vim

RUN cd /usr/local/ && mkdir apache-maven/ && \
    cd apache-maven/ && \
    wget http://mirror.navercorp.com/apache/maven/maven-3/3.6.3/binaries/apache-maven-3.6.3-bin.tar.gz && \
    tar -zxvf apache-maven-3.6.3-bin.tar.gz

# Setup Apache Maven
ENV M2_HOME="/usr/local/apache-maven/apache-maven-3.6.3"
ENV M2="$M2_HOME/bin"
ENV MAVEN_OPTS="-Xms256m -Xmx512m"
ENV PATH="$M2:$PATH"

# Check Maven version
RUN mvn -version

WORKDIR /root

RUN add-apt-repository -y ppa:fkrull/deadsnakes
RUN apt-get update
RUN apt-get install -y --no-install-recommends python3.6 python3.6-dev python3-pip python3-setuptools python3-wheel gcc
RUN python3.6 -m pip install pip --upgrade

RUN apt-get install bc
COPY resources/vimrc .vimrc

# D4J Setup
COPY resources/d4j_install.sh d4j_install.sh
RUN chmod +x d4j_install.sh
RUN ./d4j_install.sh
ENV PATH="${PATH}:/root/defects4j/framework/bin"

# Expr Env Setup
COPY resources/d4j_expr d4j_expr
ENV D4J_EXPR="/root/d4j_expr"

RUN cd $D4J_EXPR && pip3 install -r requirements.txt
# Evosuite Setup
COPY resources/evosuite-master-1.0.7-SNAPSHOT.jar evosuite-master-1.0.7-SNAPSHOT.jar

ENV EVOSUITE="java -jar /root/evosuite-master-1.0.7-SNAPSHOT.jar"
ENV EVOSUITE_DEFAULT_CONFIG="$D4J_EXPR/evosuite-config"

ENV D4J_EXPR_RESULTS="$D4J_EXPR/results"
ENV D4J_METADATA="$D4J_EXPR_RESULTS/metadata/"
ENV EVOSUITE_CONFIG="$D4J_EXPR_RESULTS/evosuite_config/"
ENV EVOSUITE_TEST="$D4J_EXPR_RESULTS/evosuite_test/"
ENV EVOSUITE_REPORT="$D4J_EXPR_RESULTS/evosuite_report/"
ENV EVOSUITE_COVERAGE="$D4J_EXPR_RESULTS/evosuite_coverages/"
ENV EVOSUITE_ORACLE="$D4J_EXPR_RESULTS/evosuite_oracles/"

COPY resources/setup.sh /root/setup.sh
RUN cd /root && sh setup.sh
#RUN pip install torch
