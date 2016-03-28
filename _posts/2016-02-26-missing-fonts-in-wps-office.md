---
layout: post
title: Missing Fonts in WPS Office for Linux
date: 2016-02-26 20:11:31 +0100
---

Even after installing the `wps-office-fonts` package, WPS Office still complained about missing fonts: Wingdings, Wingdings 2, Wingdings 3 and MT Extra. I found them on the [Microsoft typography site](https://www.microsoft.com/typography/fonts/family.aspx?FID=16), which lists the products that contain them. Seems like everything except the first Wingdings is all office packages from 97 to 2007. Luckily my dad has an Office 2003 CD laying around, so I copied the installer files to a folder. The program resources are all in cabinet archives, which can be extracted by using the cabextract tool:

{% highlight bash %}
cabextract -d extract/ *.CAB
{% endhighlight %}

Part of the extracted files are three of the required fonts: `WINGDNG2.TTF`, `WINGDNG3.TTF` and `MTEXTRA.TTF_1031`. Now only Wingdings is missing, it can be found in pretty much all Windows installs. I figured out 3 ways to get the file:

1. Copy it from an existing windows installation
2. Copy it from one of the IE VMs, which Microsoft provides for free at <https://dev.windows.com/en-us/microsoft-edge/tools/vms/linux/>
3. Extract it from the DVD image

Number 1 and 2 are boring, so I started by copying the `/sources/install.wim` image from the DVD to an empty directory. It can be unpacked with 7z and because we only need the fonts, I added a filter for `*.ttf`.

{% highlight bash %}
7z x install.wim '*.ttf' -r
{% endhighlight %}

Inside the `1/Windows/Fonts` folder should be the `wingding.tff` file. This is the last file I needed, so there's not much left to do. I renamed the fonts to lowercase names, copied them to `/usr/share/fonts/truetype/microsoft/` and that's it. WPS Office stopped complaining and now properly displays some PowerPoint presentations that didn't work before.

