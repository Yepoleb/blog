---
layout: post
title: How to get GOG GALAXY to accept a MITM certificate
date: 2022-05-09 13:06:00 +0200
---

Just a quick post on how to set up MITM with GOG GALAXY so other people can take over my job. First make sure to update the application, because half of these changes get reverted with every update.

## The part you need to do after every update

This makes the graphical interface work.

1. Get the MITM certificate from mitm.it in PEM format.
2. Open `C:\ProgramData\GOG.com\Galaxy\redists\rootCA.pem` in a text editor. `ProgramData` is not the same as `Program Files`!
3. Paste the downloaded certificate's content at the end.
4. Save.

## The part you only need to do once

This makes the background service work.

1. Get the MITM certificate from mitm.it in P12 format.
2. Import it into "Trusted Root Certification Authorities" using the Windows utility

The upstream mitmproxy does not have support for adding revocation information to certificates at the time of writing this (2022-05-09). libcurl with the Windows Schannel backend, which is used for the background services, refuses certificates without revocation information. You need to use my fork at https://github.com/Yepoleb/mitmproxy-crl/tree/crl. Make sure to run the `crl` branch. It's probably a good idea to create a venv for this version.

For more information on how I set up mitmproxy for transparently proxying a VM read my previous article [Transparent proxying setup for mitmproxy with only one VM](/blog/2022/05/07/transparent-proxying-setup-for-mitmproxy-with-only-one-vm/)
