# ps5-host-luckfox
PS5 Jailbreak with Luckfox Pico

# Wiki and documentation
[Luckfox Downloads](https://wiki.luckfox.com/Luckfox-Pico/Download)

## Prepare the board
### Install the driver - DriverAssitant-RK
### Flash Buildroot in SPI FLASH - Luckfox_Pico_Max_Flash_XXXXXX.zip
### Create Ubuntu SDCard - Ubuntu_Luckfox_Pico_Max_MicroSD_XXXXXX.zip

## SSH Login
```
Login: pico
Password: luckfox
Static IP: 172.32.0.70
```

## Internet Share
- Select your adapter witch has Internet acces
- Right-click: Propieties: Share: Select your Ethernet adapter

## Download the files in the board
```
cd
sudo apt update
sudo apt install dnsmasq -y
wget https://github.com/srgi79/ps5-host-luckfox/raw/refs/heads/main/main.py
wget https://github.com/srgi79/ps5-host-luckfox/raw/refs/heads/main/main_ssl.py
wget https://github.com/srgi79/ps5-host-luckfox/raw/refs/heads/main/dnsmasq.hosts
wget https://github.com/srgi79/ps5-host-luckfox/raw/refs/heads/main/dnsmasq.conf
```

## Download your prefered idlesauce exploit
### IPv6 (3.XX - 4.XX)
```
git clone https://github.com/idlesauce/PS5-Exploit-Host.git ps5_host/
```
### UMTX2 (1.00 - 5.50)
```
git clone https://github.com/idlesauce/umtx2.git ps5_host/
```

## Disable internet share

## Set Static IP

Create the service file.
```
sudo nano /etc/systemd/system/static-ip.service
```

Add the service content.
```
[Unit]
Description=Set Static IP Address
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/set-static-ip.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Create the script file.
```
sudo nano /usr/local/bin/set-static-ip.sh
```

Add the script content.
```
#!/bin/bash

ifconfig eth0 10.1.1.1 netmask 255.255.255.0
ip link set eth0 up
route add default gw 10.1.1.1
ifconfig eth0 up 
```

Set executable permissions.
```
sudo chmod +x /usr/local/bin/set-static-ip.sh
```

Reload systemd.
```
sudo systemctl daemon-reload
```

Enable the service.
```
sudo systemctl enable static-ip.service
```

Test the service.
```
sudo systemctl start static-ip.service
```

Check the status.
```
sudo systemctl status static-ip.service
```

## Configure DNS Server
```
cd
sudo cp dnsmasq.conf /etc/dnsmasq.conf
sudo cp dnsmasq.hosts /etc/dnsmasq.hosts
cp main.py ps5_host/
cp main_ssl.py ps5_host/
cp ps5_host/ ps5_host_ssl/ -r
```

## Enable PS5 host - Using PKG
Create the service file.
```
sudo nano /etc/systemd/system/ps5-host.service
```
Add the service content.
```
[Unit]
Description=PS5 Host

[Service]
ExecStart=/bin/bash -c 'cd /home/pico/ps5_host && python3 main.py'
User=root

[Install]
WantedBy=multi-user.target
```

Reload systemd.
```
sudo systemctl daemon-reload
```

Enable the service.
```
sudo systemctl enable ps5-host.service
```

Test the service.
```
sudo systemctl start ps5-host.service
```

Check the status.
```
sudo systemctl status ps5-host.service
```
## Enable PS5 host - Using PS5 Manual
Create the service file.
```
sudo nano /etc/systemd/system/ps5-host-ssl.service
```
Add the service content.
```
[Unit]
Description=PS5 Host SSL

[Service]
ExecStart=/bin/bash -c 'cd /home/pico/ps5_host_ssl && python3 main_ssl.py'
User=root

[Install]
WantedBy=multi-user.target
```

Reload systemd.
```
sudo systemctl daemon-reload
```

Enable the service.
```
sudo systemctl enable ps5-host-ssl.service
```

Test the service.
```
sudo systemctl start ps5-host-ssl.service
```

Check the status.
```
sudo systemctl status ps5-host-ssl.service
```

## Reboot
```
sudo reboot
```
