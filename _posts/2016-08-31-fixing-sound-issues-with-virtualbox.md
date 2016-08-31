---
layout: post
title: Fixing sound issues with Virtualbox
date: 2016-08-31 17:33:35 +0200
---

Here are a few ways to fix sound issues with virtual Windows guests running in Virtualbox.

## VM Settings

* Toggle System -> Motherboard -> Extended Features: Enable I/O APIC
* Disable System -> Acceleration -> Hardware Virtualization: Enable VT-x/AMD-V
* Change Audio -> Host Audio Driver

## Windows XP Guests and below

* Set Control Panel -> Sounds and Audio Devices -> Audio -> Sound playback -> Advanced -> Performance -> Hardware acceleration to None
