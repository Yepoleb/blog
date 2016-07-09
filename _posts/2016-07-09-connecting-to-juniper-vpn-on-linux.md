---
layout: post
title: Connecting to Juniper VPN on Linux
date: 2016-07-09 16:31:41 +0200
---

I recently tried to connect to a "Junos Pulse Secure Access Service" and found two ways to do that on Linux. Instructions are written for Debian/Ubuntu, but you should be able to find the required packages for any distribution.

## Use OpenConnect

OpenConnect supports Juniper VPN as of version 7.05. At least Debian stretch or Ubuntu wily are required to install it from the package sources.

1. Install the openconnect package  
   `sudo apt-get install openconnect`

2. Connect to the server  
   `sudo openconnect --juniper https://vpn.example.com`  
   If OpenConnect responds with `openconnect: unrecognized option '--juniper'`, your version is too old and you should update. 


## Use the offical client

The offical client can be installed from the VPN's web interface. It has the downside of requiring 32-bit Java 7 libraries. If your distribution doesn't have openjdk-7 packages anymore, you should probably use the OpenConnect method described above.

1. Add the i386 architecture, if you're using a 64-bit OS and haven't done that already.  
   `sudo dpkg --add-architecture i386`  
   `sudo apt-get update`

2. Install the Java plugin and 32-bit JRE.  
   `sudo apt-get install icedtea-7-plugin openjdk-7-jre:i386`

3. Set the 32-bit JRE as default.  
   `sudo update-alternatives --config java`

4. Install the client by clicking the "Start" button in the web interface and allow the browser to run "IcedTea-Web".  
   ![vpn_connect_start]({{ site.baseurl }}/img/vpn_connect_start.png)

After completing the installation a window should pop up with connection information.

![vpn_connected]({{ site.baseurl }}/img/vpn_connected.png)

