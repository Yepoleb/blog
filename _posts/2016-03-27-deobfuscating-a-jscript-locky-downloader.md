---
layout: post
title: Deobfuscating a JScript Locky Downloader
date: 2016-03-27 22:06:42 +0200
---

Ransomware is the new trend in malware development and it doesn't seem to be dying out soon. I recently received another email with a locky downloader script attached and decided to take a look. It's written in JScript, an ECMAScript implementation by Microsoft and uses methods of the Windows Script Host.

## The source code

#### invoice.js
{% highlight javascript %}
{% include code/invoice.js %}
{% endhighlight %}

## Seperating constants and code

The first step in making the code readable is inlining all the constants. To make that easier split the file into two new ones called `code.js` and `vars.js`.

## Unescape the urlencoded code

There's some urlencoded stuff in `code.js`, just put it through an online tool or paste the unescape command in a Node.js shell. Use [jsbeautifier](http://jsbeautifier.org) to make it pretty.

## Removing prototype functions

The prototype functions can just be replaced with a static value. Use the regex replace feature of your text editor to remove everything that matches this:

* vars.js: `\(function .+?\.prototype\..+?\(\) { return `
* vars.js: `; }, .+?\)`
* code.js: `\.\w+\(\)`

## Inlining the constants

The two files should look like this now:

#### vars.js
{% highlight javascript %}
{% include code/vars.js %}
{% endhighlight %}

#### code.js
{% highlight javascript %}
{% include code/code.js %}
{% endhighlight %}

I wrote a Python script to do the remaining work for me

#### unscramble.py
{% highlight python %}
{% include code/unscramble.py %}
{% endhighlight %}

After running it you should get a file called `code_new.js` with the final result.

#### code_new.js
{% highlight javascript %}
{% include code/code_new.js %}
{% endhighlight %}

The code is now mostly readable and you can find the payload url. By the time I read the email the file was already taken down, but with some search engine magic I could find it on [http://dasmalwerk.eu/](dasmalwerk.eu/). Unfortunately it didn't work in my virtual machine.

