#!/bin/bash
#run inside the new chroot
user=poodillion
touch /it_worked
useradd $user
#clear passwd
sed -i "s/$user:\!:/$user::/g" /etc/shadow

#Setup shell
usermod --shell /bin/bash $user

#Disable login
mkdir /etc/systemd/system/console-getty.service.d/
echo -e "\n[Service]\nExecStart=\nExecStart=-/sbin/agetty --noclear --autologin $user --keep-baud console 115200,38400,9600 \$TERM\n" > /etc/systemd/system/console-getty.service.d/override.conf
#systemctl enable console-getty


#setup home
echo "Setting up home"
mkdir /home/$user
chown $user:$user /home/$user

#setup game foder
mkdir /game
chown $user:$user /game

#Setup bashrc
echo 'PROMPT_COMMAND="echo \$PWD > /game/PWD"' > /home/$user/.bashrc
echo 'PROMPT_COMMAND="echo \$PWD > /game/PWD"' >> /etc/bash.bashrc
#Set init PWD
echo "/home/$user" > /tmp/PWD
chown $user:$user /home/$user/.bashrc
chmod 755 /home/$user/.bashrc
