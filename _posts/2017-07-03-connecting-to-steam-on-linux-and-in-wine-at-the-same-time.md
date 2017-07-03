---
layout: post
title: Connecting to Steam on Linux and in Wine at the same time
date: 2017-07-03 04:44:00 +0200
---

There's the know problem that if you run native and Wine Steam on the same PC, only one of them can be connected to the Steam network. Some time ago users [Ruedii] and [ardje] on the [steam-for-linux bugtracker] suggested using virtual network devices and namespace to work around this limitation, so I gave it a try and it worked out great. To make it easier for others to take advantage of this amazing technology, I'm writing down all the steps it took to implement this as a permanent solution. The instructions are tested on Debian, but should work on any Distribution with minimal changes. The goal is to have two virtual ethernet devices, one (veth0) for the regular system and another (veth1) inside a namespace to run Wine Steam in.

### Enable the macvlan kernel module
The macvlan module allows us to create virtual ethernet devices. It can be enabled by adding the line `macvlan` at the end of `/etc/modules`. Arch users should be able to load it by placing a file with the same line in `/etc/modules-load.d/`.

    echo 'macvlan' | sudo tee --append /etc/modules

### Disable NetworkManager
Using it would make everything much more complicated and the benefits on a gaming system are usually small. With systemd the command is:

    sudo systemctl disable network-manager.service

There may be a GUI tool in the tray that needs to be deactivated in the autostart settings of your desktop environment.

### Configure the default network interfaces
These are defined in `/etc/network/interfaces` and can be edited with any text editor.

    sudo nano /etc/network/interfaces

The first lines are probably some comments and a `source` entry. Ignore them and move on to the loopback interface. It should look something like this:

    # Loopback interface
    auto lo
    iface lo inet loopback

Next is the cable interface, probably called eno1. It will no longer get an IP address, as veth0 is going to take that job.

    # Cable interface
    auto eno1
    iface eno1 inet manual
        ip ip link set eno1 up
        down ip link set eno1 down

### Configure the first virtual interface

I'm using a static IP configuration to make things easier. The MAC address is randomly generated, but make sure it's part of the locally administered ranges to prevent conflicts.

    # Virtual interface 1
    auto veth0
    iface veth0 inet static
        address 192.168.1.10
        netmask 255.255.255.0
        gateway 192.168.1.1
        pre-up ip link add name veth0 address 6E:33:EB:FB:B6:C2 link eno1 type macvlan
        post-down ip link delete dev veth0

### Configure the second virtual interface

This part is a bit more complicated because the interface gets added to a namespace before it is enabled. The namespace also gets its own loopback device to allow communication between processes inside of it.

    auto veth1
    iface veth1 inet manual
        # Create the virtual interface
        pre-up  ip link add name veth1 address 36:F5:C1:A7:D1:AB link eno1 type macvlan
        # Create the namespace
        pre-up  ip netns add vns1
        # Put veth1 inside the namespace
        pre-up  ip link set veth1 netns vns1
        # Activate veth1 and lo
        up      ip netns exec vns1 ip link set dev veth1 up
        up      ip netns exec vns1 ip link set dev lo up
        # Set the address and route configuration
        post-up ip netns exec vns1 ip addr add 192.168.1.11/24 dev veth1
        post-up ip netns exec vns1 ip route add default via 192.168.1.1
        # Deactivate veth1 and lo
        down    ip netns exec vns1 ip link set dev veth1 down
        down    ip netns exec vns1 ip link set dev lo down
        # Delete namespace including interface
        post-down ip netns del vns1

### Building a wrapper around the namespace command

At this point we could already run Steam in Wine using the regular `ip netns` command and some sudo magic.

    sudo ip netns exec vns1 sudo -u "$USER" -i wine /path/to/steam.exe

This is not really convenient for everyday use though, because you'd have to type your password every time launching steam. So I decided to build a small wrapper script which allows users in the `netns` group to run commands in a namespace without giving them full root access. It's placed at `/usr/local/bin/netns`.

    #!/bin/bash

    if [[ $EUID == 0 ]]; then
        if [[ -n $SUDO_USER ]]; then
            NS_USER="$SUDO_USER"
        else
            NS_USER="root"
        fi
    else
        echo "Error: Script does not have root privileges"
        exit 1
    fi

    if (( $# < 2 )); then
        echo "Usage: nsexec <namespace> <command> [args]"
        exit 1
    fi

    NAMESPACE="$1"; shift
    ip netns exec "$NAMESPACE" sudo -u "$SUDO_USER" -i -- "$@"

Add this line to the sudoers file using `sudo visudo` to allow running the command without a password.

    # Allow network namespaces
    %netns	ALL=NOPASSWD: /usr/local/bin/nsexec

Create the `netns` group and add yourself to it.

    sudo addgroup --system netns
    sudo adduser "$USER" netns

At this point it's probably a good idea to reboot and apply all the changes. Everything is set up now and you can launch Steam using the wrapper.

    sudo nsexec wine /path/to/steam.exe

It still requires sudo, but shouldn't ask for a password anymore. Depending on how you launch Steam, you can add it to the existing starter in `/usr/share/applications/` or put it in a script.

[Ruedii]: https://github.com/Ruedii
[ardje]: https://github.com/ardje
[steam-for-linux bugtracker]: https://github.com/ValveSoftware/steam-for-linux/issues/4412#issuecomment-304745400
