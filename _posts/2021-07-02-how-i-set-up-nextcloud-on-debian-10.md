---
layout: post
title: How I set up Nextcloud on Debian 10
date: 2021-07-02 18:25:00 +0200
---

This is a sequel to my post about setting up Wordpress on Debian. It has a quick introduction about why I set up things the way I do, which I will not repeat here. Instead I'll go straight to the installation steps.

### Installing packages

Nextcloud itself unfortunately doesn't have a package in Debian, but PHP and a MariaDB can be installed from apt. Apache is assumed to be already installed.

    sudo apt install php-fpm mariadb-server

Nextcloud is downloaded from the official website as a tar.bz2 archive.

    sudo wget https://download.nextcloud.com/server/releases/nextcloud-xx.0.0.tar.bz2
    tar -xf nextcloud-xx.0.0.tar.bz2

The content is copied to `/usr/local/share`.

    sudo cp -r nextcloud /usr/local/share

This directory will stay owned by root and application data will be placed in another directory created later.

### Creating users
    
I decided to create a system user, because there's no need for a real user to ever authenticate as nextcloud.

    sudo adduser --system --home /var/lib/nextcloud --shell /bin/sh --no-create-home --group --disabled-login --gecos 'Nextcloud' nextcloud

Nextcloud also needs a database and a user, authenticated by socket for added security. A MariaDB shell can be opened by running the `mariadb` command as root.

    CREATE DATABASE nextcloud CHARACTER SET 'utf8mb4';
    GRANT ALL ON `nextcloud`.* TO 'nextcloud'@'localhost' IDENTIFIED VIA unix_socket;
    FLUSH PRIVILEGES;

Now data and config directories can be created and ownership transfered to nextcloud.

    sudo mkdir -p /var/lib/nextcloud/data
    sudo mkdir -p /var/lib/nextcloud/config
    sudo chown -R nextcloud:nextcloud /var/lib/nextcloud

### Configuring PHP-FPM

PHP-FPM is the process that's going to be running the PHP code. Nextcloud is the only PHP application on this server, so I'm just going to rename the default pool configuration.

    cd /etc/php/7.3/fpm/pool.d/
    sudo mv www.conf nextcloud.conf

The new config needs the username, group and socket set. The example below is not the full config, just the lines that need to be changed. `clear_env = no` is apparently needed to preserve the `PATH` variable and the following line changes the config directory to something outside the application root. This variable is unfortunately not documented, I found it reading source code.
    
    [nextcloud]
    user = nextcloud
    group = nextcloud
    listen = /run/php/nextcloud.sock
    clear_env = no
    env[NEXTCLOUD_CONFIG_DIR] = /var/lib/nextcloud/config

At last FPM needs to be restarted.

    sudo systemctl restart php7.3-fpm

### Apache configuration

Apache2 is the webserver that will serve all the static content and act as a reverse proxy for the application. The config is placed in `/etc/apache2/sites-available` as `nextcloud.conf`

    <VirtualHost *:443>
            ServerName nextcloud.yepoleb.at
            CustomLog ${APACHE_LOG_DIR}/nextcloud.log combined

            SSLEngine On

            DocumentRoot /usr/local/share/nextcloud
            <Directory /usr/local/share/nextcloud>
                    Require all granted
                    AllowOverride All
                    Options FollowSymLinks MultiViews
            </Directory>

            <FilesMatch ".+\.php$">
                    SetHandler "proxy:unix:/run/php/nextcloud.sock|fcgi://localhost"
            </FilesMatch>
    </VirtualHost>

This is the main part of the config. `SSLEngine On` is a shorthand for a full SSL configuration which I have placed in `/etc/apache2/conf-available` so it applies to all sites. The directory section allows serving files from the application directory and overrides some access control options. The `FilesMatch` section sets the handler socket for PHP files.
    
    <VirtualHost *:80>
            ServerName nextcloud.yepoleb.at
            CustomLog ${APACHE_LOG_DIR}/nextcloud.log combined

            RewriteEngine On
            RewriteCond %{REQUEST_URI} !/.well-known/acme-challenge
            RewriteRule ^/?(.*) https://nextcloud.yepoleb.at/$1 [END,R=permanent]
    </VirtualHost>

This part is just a more complicated HTTP to HTTPS redirect with an exception for certbot webroot challenges. There are a few modules that also need to be enabled:

    sudo a2enmod rewrite setenvif proxy_fcgi ssl

Enable the site and restart Apache.

    sudo a2ensite nextcloud
    sudo systemctl restart apache2

### Configuring Nextcloud

Now the webinterface of Nextcloud is reachable. It will complain that the app store needs write permission or needs to be disabled. I don't care about any apps, so I disabled it in the now created configuration file `/var/lib/nextcloud/config/config.php` by adding the following line.

    'appstoreenabled' => false

After the change the webinterface should no longer complain. The important values in the setup wizard are the data directory `/var/lib/nextcloud/data` and the database address `localhost:/var/run/mysqld/mysqld.sock`. The database password can stay empty because of socket auth.

### Tweaking PHP

Nextcloud complains in the settings if the following options are not set in `/etc/php/7.3/fpm/php.ini`

    upload_max_filesize = 1G
    post_max_size = 1G
    memory_limit = 512M

### Software versions

* Debian 10 Buster
* Nextcloud 22.0.0
* PHP-FPM 7.3
* Apache2 2.4.38
