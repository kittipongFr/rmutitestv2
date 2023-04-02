#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2012-06-03

@author: Sergey Prokhorov <me@seriyps.ru>

Скрипт для создания архива, содержащего все пакеты, необходимые для оффлайн
установки l2tp плагина NetworkManager на Ubuntu.
'''
import logging
import urllib
import os
import os.path
import sys
import bz2
import tarfile
import time


PACKETS_DIR = 'nm-l2tp'

__version__ = '0.0.7'

DISTROS = [
    (u"14.10", u"utopic"),
    (u"14.04", u"trusty"),
    (u"13.10", u"saucy"),
    (u"13.04", u"raring"),
    (u"12.10", u"quantal"),
    (u"12.04", u"precise"),
    (u"11.10", u"oneiric"),
    (u"10.04", u"lucid")]

ARCHS = [
    (u"i386", u"32-битный"),
    (u"amd64", u"64-битный")]

logger = logging.getLogger(__name__)

ENC = sys.stdout.encoding

README = u"""
Архив L2TP плагина и зависимостей на Ubuntu для тех, у кого без L2TP интернет
не работает.
Если у вас интернет работает и без L2TP, то этот архив вам не нужен. Читайте
инструкцию на
 http://seriyps.ru/blog/2012/01/31/plagin-l2tp-dlya-networkmanager/

Установка
=========

Выполнить в папке с распаковынными пакетами команду:

    sudo dpkg -i *.deb

Или подробнее:

Скачали архив. Распаковали его, скажем, в домашнюю папку. У вас в домашней
папке теперь есть папочка "nm-l2tp", в папочке пакеты и этот файл README.
Открываете терминал, в нем пишете:

    cd ~/nm-l2tp
    sudo dpkg -i *.deb


Получаем обновления
===================

Открываем терминал, в нем выполняем команды

    sudo apt-add-repository ppa:seriy-pr/network-manager-l2tp
    sudo apt-get update
    sudo apt-get upgrade


Примечание
==========

Старайтесь этот архив не выкладывать в интернет. Это может привести к тому,
что люди со временем будут устанавливать устаревшие версии плагина.
Выкладывайте сам скрипт l2tp-downloader.py

Помощь
======

Форум для beeline:
 http://homenet.beeline.ru/index.php?showtopic=302878&st=0
Форум ubuntu:
 http://forum.ubuntu.ru/index.php?topic=181916.0
Наиболее актуальная информация + что делать в случае проблем:
 http://seriyps.ru/blog/2012/01/31/plagin-l2tp-dlya-networkmanager/
"""


def get_distro():
    prompt = u"Версия дистрибутива:\n{0}\n$ ".format(
        u"\n".join([u"{0}) {1} {2}".format(i, num, name)
                    for i, (num, name) in enumerate(DISTROS)]))
    distro = raw_input(prompt.encode(ENC))
    return DISTROS[int(distro)]


def get_arch():
    prompt = u"Тип процессора:\n{0}\n$ ".format(
        u"\n".join([u"{0}) {1} ({2})".format(i, num, name)
                    for i, (num, name) in enumerate(ARCHS)]))
    arch = raw_input(prompt.encode(ENC))
    return ARCHS[int(arch)][0]


def read_package(bzfile):
    lines = {}
    while True:
        l = bzfile.readline()
        if l == '\n':
            return lines
        elif l == '':
            return None
        elif ': ' not in l:  # hack
            # print l
            continue
        name, value = l.split(': ', 1)
        lines[name] = value.strip()


def download_packets(repo_url, repo_component, distro, arch, packets):
    packages = ('{repo_url}ubuntu/dists/{distro_name}/{repo_component}/'
                'binary-{arch}/Packages.bz2'.format(
            distro_name=distro[1], **locals()))
    packages_file = os.path.join(PACKETS_DIR, '.packages.bz2')
    logger.info("Download repository index from %s", packages)
    urllib.urlretrieve(packages, packages_file)
    bzfile = bz2.BZ2File(packages_file)
    _packets = set(packets)
    while _packets:
        package_dict = read_package(bzfile)
        if package_dict is None:
            raise ValueError("Can't find packages %s", _packets)
        pkg_name = package_dict['Package']
        if pkg_name in _packets:
            _packets.remove(pkg_name)
            filename = package_dict['Filename']
            _, pkg_filename = os.path.split(filename)
            pkg_url = '{repo_url}ubuntu/{filename}'.format(
                repo_url=repo_url,
                filename=filename)
            logger.info("Download package '%s' from url %s",
                        pkg_name,
                        pkg_url)
            urllib.urlretrieve(
                pkg_url, os.path.join(PACKETS_DIR, pkg_filename))
    bzfile.close()
    os.unlink(packages_file)


def write_readme():
    logger.info('Add README.txt')
    with open(os.path.join(PACKETS_DIR, 'README.txt'), 'w') as f:
        f.write(README.encode(ENC))


def write_self():
    logger.info('Add self')
    out_file = os.path.join(PACKETS_DIR, 'l2tp-downloader.py')
    # with open(__file__, 'r') as inf, open(out_file, 'w') as outf:  # python>=2.7 only
    with open(__file__, 'r') as inf:
        with open(out_file, 'w') as outf:
            outf.write(inf.read())


def pack_to_archive(distro, arch):
    archive_name = os.path.abspath("{0}_{1[0]}{1[1]}_{2}_{3}.tar".format(
        PACKETS_DIR, distro, arch, time.strftime("%Y-%m-%d")))
    logger.info("Write archive '%s'", archive_name)
    tar = tarfile.open(archive_name, "w")
    tar.add(PACKETS_DIR)
    tar.close()


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.info("l2tp-downloader, v%s", __version__)
    distro = get_distro()
    arch = get_arch()
    if not os.path.isdir(PACKETS_DIR):
        os.mkdir(PACKETS_DIR)
    download_packets(
        'http://mirror.yandex.ru/ubuntu/', 'universe',
        distro, arch, ['xl2tpd', 'openswan'])
    download_packets(
        'http://mirror.yandex.ru/ubuntu/', 'main',
        distro, arch, ['ppp'])
    download_packets(
        'http://ppa.launchpad.net/seriy-pr/network-manager-l2tp/', 'main',
        distro, arch, ['network-manager-l2tp', 'network-manager-l2tp-gnome'])
    write_readme()
    write_self()
    pack_to_archive(distro, arch)
    raw_input("Press any key")


if __name__ == "__main__":
    main()
