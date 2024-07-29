---
layout: post
title: The HomeWizard P1 Meter does not support custom firmware
date: 2024-07-29 14:04:00 +0200
---

This is just a quick summary of my attempt for people who have the same idea of installing ESPHome or Tasmota on the P1 Dongle. The board has easily accessible debug pins to which a pin header can be soldered, as has been done in the following images, but secure boot and flash encryption is enabled for the ESP-C3-MINI-1 module so it **can not be reflashed**. The label on my specific board is `P1 Dongle EU V1.0 - 2023-10-26`. The case is push fit and can be opened by prying it apart at the USB port.

## Pictures

Case with board
![Photo of case with board]({{ site.baseurl }}/img/p1_meter/case_assembly.jpeg)

Board front view
![Front view of the board]({{ site.baseurl }}/img/p1_meter/board_front.jpeg)

Board back view
![Back view of the board]({{ site.baseurl }}/img/p1_meter/board_back.jpeg)

## Boot log

    021
    rst:0x1 (POWERON),boot:0xd (SPI_FAST_FLASH_BOOT)
    SPIWP:0xee
    mode:DIO, clock div:1
    Valid secure boot key blocks: 0 1 2
    secure boot verification succeeded
    load:0x3fcd5988,len:0x2d0c
    load:0x403cc710,len:0x770
    load:0x403ce710,len:0x595c
    entry 0x403cc710
    I (335) cpu_start: Unicore app
    I (335) cpu_start: Pro cpu up.
    I (344) cpu_start: Pro cpu start user code
    I (344) cpu_start: cpu freq: 160000000 Hz
    I (344) cpu_start: Application information:
    I (347) cpu_start: Project name:     p1dongle
    I (352) cpu_start: App version:      5.04
    I (357) cpu_start: Secure version:   0
    I (361) cpu_start: Compile time:      
    I (365) cpu_start: ELF file SHA256:  d9c7359fb29904fe...
    I (371) cpu_start: ESP-IDF:          v5.1.2
    I (376) cpu_start: Min chip rev:     v0.3
    I (381) cpu_start: Max chip rev:     v0.99 
    I (386) cpu_start: Chip rev:         v0.4
    I (391) heap_init: Initializing. RAM available for dynamic allocation:
    I (398) heap_init: At 3FC9D6C0 len 00022940 (138 KiB): DRAM
    I (404) heap_init: At 3FCC0000 len 0001C710 (113 KiB): DRAM/RETENTION
    I (411) heap_init: At 3FCDC710 len 00002950 (10 KiB): DRAM/RETENTION/STACK
    I (419) heap_init: At 50000028 len 00001FC0 (7 KiB): RTCRAM
    I (426) spi_flash: detected chip: generic
    I (430) spi_flash: flash io: dio
    I (434) flash_encrypt: Flash encryption mode is RELEASE
    I (440) sleep: Configure to isolate all GPIO pins in sleep state
    I (446) sleep: Enable automatic switching of GPIO sleep configuration
    I (453) app_start: Starting scheduler on CPU0
    I (458) main_task: Started on CPU0
    I (462) main_task: Calling app_main()
    I (473) gpio: GPIO[10]| InputEn: 1| OutputEn: 0| OpenDrain: 0| Pullup: 1| Pulldown: 0| Intr:3 
    I (475) gpio: GPIO[1]| InputEn: 1| OutputEn: 0| OpenDrain: 0| Pullup: 0| Pulldown: 1| Intr:3 
    I (485) gpio: GPIO[19]| InputEn: 0| OutputEn: 1| OpenDrain: 0| Pullup: 0| Pulldown: 0| Intr:0 
    E (494) FLASH: _flash_read_from_partition(419): failed ESP_ERR_NVS_NOT_FOUND
    E (502) FLASH: _flash_read_from_partition(419): failed ESP_ERR_NVS_NOT_FOUND
    E (509) FLASH: _flash_read_from_partition(419): failed ESP_ERR_NVS_NOT_FOUND
