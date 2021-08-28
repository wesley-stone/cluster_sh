FROM ubuntu:18.04

RUN apt-get update && apt-get install -y wget
RUN apt install -y ssh

WORKDIR /etc/apt/sources.list.d
RUN wget http://packages.mccode.org/debian/mccode-bionic.list
RUN apt-get update

RUN apt-get install -y cp2k

RUN apt-get install -y git

WORKDIR /root
RUN git clone https://github.com/wesley-stone/cluster_sh.git