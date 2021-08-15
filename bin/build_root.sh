#!/bin/bash
#sudo apt install debootstrap
cd "$(dirname "$0")"

shell_root=/home/$SUDO_USER/.poodillion_root
if [ -d "$shell_root" ]; then
    echo "$shell_root found!"
    read -p "Would you like to rebuild $shell_root? " -n 1 -r
    echo    # (optional) move to a new line
    if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
        echo "Exiting"
        exit 1
    else
        echo "Cleaning up old root..."
        rm -r $shell_root
    fi
fi


if [ "aarch64" == $(uname -m) ]
then
    echo "Running on aarch64"
    debootstrap --arch arm64 bullseye $shell_root http://ftp.us.debian.org/debian
    
else
    echo "Running on amd64"
    debootstrap --arch amd64 bullseye $shell_root http://ftp.us.debian.org/debian
fi

echo "Running setup script"
cp ./init_world.sh $shell_root
chroot $shell_root /init_world.sh

