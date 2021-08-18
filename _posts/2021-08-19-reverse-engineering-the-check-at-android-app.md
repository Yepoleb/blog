---
layout: post
title: Reverse Engineering the CHECK-AT Android App
date: 2021-08-19 00:48:31 +0200
---

This article describes how I modified the CHECK-AT app to reverse engineer the web API and encryption.

## Decompiling the App

The app is structured as a split APK. I used [Package Manager](https://f-droid.org/en/packages/com.smartpack.packagemanager/) from F-Droid to extract the APKs and [SAI](https://f-droid.org/en/packages/com.aefyr.sai.fdroid/) to install modified versions. Both apps can do both tasks, but I found SAI to have the better interface. For transfering the files KDE connect worked well, but you can probably use adb to make the process of installing updates even faster.

For extracing and repackaging apps [apktool](https://ibotpeaches.github.io/Apktool/) is the obvious choice. This only produces smali code instead of readable Java, so I used two separate tools to decompile. [enjarify](https://github.com/Storyyeller/enjarify) converts Dalvik bytecode to Java bytecode so it can be decompiled using regular Java decompilers. From my experience it has better compatibility than the older dex2jar. At first I used [JD-GUI](https://java-decompiler.github.io/) for the actual decompilation process, but after it failed on some important methods I switched to [Luyten](https://github.com/deathmarine/Luyten) which was more successful.

Using these tools I was able to extract a lot of information already, like the structure of the QR code and that there was an HTTP API for fetching certificates.

## Man in the Middle

Not wanting to try and piece together how the API works from decompiled code I decided to once again set up [mitmproxy](https://mitmproxy.org/). Maybe this setup could have been easier by just using the Android proxy settings, but I'm so used to set up transparent proxying that I didn't even consider it.

### Setting up the VPN

First step was setting up a VPN to route all the traffic from my phone over my PC. OpenVPN does the job quite well.

```sh
sudo sysctl -w net.ipv4.ip_forward=1
sudo ip tuntap add name tun0 mode tun
openvpn --genkey --secret static.key
sudo openvpn --dev tun0 --ifconfig 10.0.0.1 10.0.0.2 --secret static.key
```

The VPN also needs an iptables masquerade rule to enable the network address translation. 

```sh
sudo iptables -t nat -A POSTROUTING -o eth0 -s 10.0.0.0/24 -j MASQUERADE
```

If regular internet access works over the VPN redirecting HTTP can be enabled.

```sh
mitmproxy --mode transparent --showhost
sudo iptables -t nat -A PREROUTING -i tun0 -p tcp --dport 80 -j REDIRECT --to-port 8080
sudo iptables -t nat -A PREROUTING -i tun0 -p tcp --dport 443 -j REDIRECT --to-port 8080
```

### Injecting the CA

For a while now Android no longer trusts user CAs for apps that don't explicitly opt-in. At first I tried to add that opt-in switch by modifying the manifest file as described in the official documentation [here](https://developer.android.com/training/articles/security-config). This did not work as the app ships its own certificate store. Surprisingly this consists of two Let's Encrypt roots: DST X3 and ISRG X1. As the DST root is no longer actively used and will expire soon, I decided it's easiest to just replace it with my own. The mitmproxy cert is located at `~/.mitmproxy/mitmproxy-ca-cert.pem` and it will replace `res/raw/letsencrypt_dst_x3.pem` inside the app package.

### Reassembling the App

The initial attempt at reassembling the apk failed. It required the `--use-aapt2` commandline switch to work and a few resource files to be renamed because they contained invalid characters. The final APK needs a signature, else it won't install. Most guides suggest using jarsigner, but this is apparently not enough for more recent SDK versions. I had to use apksigner instead. Before any signing a key needs to be generated.

```sh
keytool -genkey -v -keystore my-keystore.keystore -alias myalias -keyalg RSA -keysize 2048 -validity 10000
```

Then each of the split APKs needs to be signed

```sh
zipalign -v 4 base.apk aligned.apk
apksigner sign --ks my-keystore.keystore --ks-pass pass:12345678 aligned.apk
```

I ziped up the files and sent them to my phone to install using SAI. I was finally able to snoop the API URLs.

_After writing this section I remembered that there was also some certificate pinning code that I disabled by adding an early return statement to the function. But without the CA it would not work and I never went back to verify if it was really necessary._

## Injecting Custom Code

Cryptography is notoriously hard to reverse engineer. I figured I had the best chances if I had as much data as possible to compare my own results to. Debugging using Android Studio and [smalidea](https://github.com/JesusFreke/smalidea) just didn't want to work, so I opted for the next best thing which was logging. Injecting custom code using apktool means modifying the disassembled smali files because recompiling Java is too unreliable. I started out by writing out the code I wanted to inject in a separate Android Studio project.

```java
final byte[] data = new byte[] {(byte)0x04, (byte)0xE4, (byte)0x16, (byte)0xBE};
String data_str = Arrays.toString(data);
Log.i("loggingtag", data_str);
```

Then I compiled and decompiled it again to get back the smali code. This code can then be copied at the right places into the code of the original app. The register numbers need to be increased to not collide with those already in use and the first register needs to point to the actual data.

```smali
invoke-static {p1}, Ljava/util/Arrays;->toString([B)Ljava/lang/String;
move-result-object v7
const-string v6, "logtag"
invoke-static {v6, v7}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
```

This allowed me to dump the values that were fed to the signature algorithm and utimately figure out the encryption.

## Final Notes

All my findings are documented in this repository: https://github.com/Yepoleb/idcard-qr

If this post was useful to you and you're doing something similar, feel free to contact me for help if you're stuck.
