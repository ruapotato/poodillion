#!/bin/bash
#sudo apt install debootstrap
cd "$(dirname "$0")"

if test -z "$SUDO_USER"
then
    USER=$(getent passwd $PKEXEC_UID | cut -d: -f1)
    echo "Skip interface (Running with pkexec)"
    run_setup="0"
else
    USER=$SUDO_USER
    run_setup="1"
fi
shell_root=/home/$USER/.poodillion_root

#Only run setup interface if run with sudo not pkexec
if [ "$run_setup" -eq "1" ]
then
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
else
    #clean up if an old install is around (Run with pkexec)
    rm -r "$shell_root"
fi

if [ "aarch64" == $(uname -m) ]
then
    echo "Running on aarch64"
    debootstrap --include python3 --arch arm64 bullseye $shell_root http://ftp.us.debian.org/debian
    
else
    echo "Running on amd64"
    debootstrap --include python3 --arch amd64 bullseye $shell_root http://ftp.us.debian.org/debian
fi

#install rm
mv $shell_root/usr/bin/rm $shell_root/root/rm
cp ./fake_rm.py $shell_root/usr/bin/rm
cp ../player_sys.py $shell_root/usr/lib/python3.9/

#install touch
mv $shell_root/usr/bin/touch $shell_root/root/touch
cp ./fake_touch.py $shell_root/usr/bin/touch

#setup defualt .spawners
echo "#   when:          img:             name:    %                     action:damage:life:    % drops"> $shell_root/home/poodillion/.spawner
echo "on_enter:  fun_guy.png:              bob: 100% msg Use cd to change rooms:     1:   3: 100% -50HP">> $shell_root/home/poodillion/.spawner

#setup ~/m
mkdir $shell_root/home/poodillion/mushroom
echo "#   when:         img:  name:    %  action:damage:life:    % drops" > $shell_root/home/poodillion/mushroom/.spawner
echo "on_enter: fun_guy.png:  bob2: 100% msg rm will kill enemies.:     1:   3: 100% msg be careful who you kill!" >> $shell_root/home/poodillion/mushroom/.spawner

echo "Running setup script"
cp ./init_world.sh $shell_root
chroot $shell_root /init_world.sh

