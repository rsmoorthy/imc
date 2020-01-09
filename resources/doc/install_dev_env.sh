#!/bin/bash

# Execute all of them as root

# Run these commands on a PC
apt-get install coreutils quilt parted qemu-user-static debootstrap zerofree zip \
	dosfstools bsdtar libcap2-bin grep rsync xz-utils file git curl

ROOT_DIR=/root/root
mkdir -p $ROOT_DIR
#debootstrap --arch armhf --components main,contrib,non-free --keyring /home/rsm/rpi4/raspberrypi.gpg buster $ROOT_DIR http://raspbian.raspberrypi.org/raspbian
# The above command takes a lot of time
debootstrap --arch armhf buster $ROOT_DIR http://raspbian.raspberrypi.org/raspbian

mount -t proc proc $ROOT_DIR/proc/
mount -t sysfs sys $ROOT_DIR/sys/
mount -o bind /dev $ROOT_DIR/dev/
mount -o bind /dev/pts $ROOT_DIR/dev/pts

chroot $ROOT_DIR

# The following commands are specified in the chrooted env
apt install --no-install-recommends python3-venv libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev pkg-config libgl1-mesa-dev libgles2-mesa-dev python-setuptools libgstreamer1.0-dev libmediainfo0v5 python3-pip python3-setuptools build-essential python3-dev libpangoft2-1.0-0 git curl

pip3 install pipenv

# Not needed here apt install --no-install-recommends xserver-xorg-legacy

git clone -b window-manager https://github.com/rsmoorthy/pi-player.git
cd pi-player
pipenv install
#pipenv install --skip-lock

pipenv shell
pyinstaller main.py
du -sch dist/
bash -x deploy.sh

ls -l /tmp/imc.tgz # file to be extracted in /opt/imc in Raspberry Pi
