---
layout: post
title: How I set up Wordpress on Debian 10
date: 2021-07-02 00:12:00 +0200
---

I'm documenting here how I decided to set up Wordpress on my server. It was supposed to be used by a friend, which influenced which decisions I took in terms of configuration. First priority was deciding on how to isolate the application from the rest of the system. These are the options I considered:

* Virtual machine - too much work to set up and maintain.
* Container - still needs quite a lot of work to maintain the base system.
* chroot - possible, but needs a lot of testing to verify everything necessary is available
* AppArmor - similar issues to chroot, I might have considered it if I was more experienced with it
* Separate user - medium level of isolation, can access general system files but does not share permissions with other applications
* www-data user - low level of isolation, everything is shared between web applications

I decided to use the separate user approach because it seemed like a good compromise of usability and security. Most guides use the www-data method, but I despise running code as the web user or even as part of the web server. The whole process was heavily inspired by how the Debian maintainers usually package things.

### Installing packages

The required packages for this installation are `wordpress php-fpm mariadb-server`, which I installed using apt. Apache is assumed to be already installed.

    sudo apt install wordpress php-fpm mariadb-server

### Creating users
    
Username for the new user is `wordpress`. I decided to create it as a regular user in `/home` so it can be used for general administrative purposes of the instance.

    sudo adduser wordpress

This user also has to be created in MariaDB along with a database of the same name. Socket authentication has many benefits over password authentication because there is no password to be forgotten or stolen. A MariaDB shell can be opened by running the `mariadb` command as root.

    CREATE DATABASE wordpress CHARACTER SET 'utf8mb4';
    GRANT ALL ON `wordpress`.* TO 'wordpress'@'localhost' IDENTIFIED VIA unix_socket;
    FLUSH PRIVILEGES;

### Configuring PHP-FPM

PHP-FPM is the process that's going to be running the PHP code. Wordpress is the only PHP application on this server, so I'm just going to rename the default pool configuration.

    cd /etc/php/7.3/fpm/pool.d/
    sudo mv www.conf wordpress.conf

The new config needs the username, group and socket set. The example below is not the full config, just the lines that need to be changed.
    
    [wordpress]
    user = wordpress
    group = wordpress
    listen = /run/php/wordpress.sock

At last FPM needs to be restarted.

    sudo systemctl restart php7.3-fpm

### Configuring Apache2

Apache2 is the webserver that will serve all the static content and act as a reverse proxy for the application. The config is placed in `/etc/apache2/sites-available` as `wordpress.conf`

    <VirtualHost *:443>
            ServerName wordpress.yepoleb.at
            CustomLog ${APACHE_LOG_DIR}/wordpress.log combined

            SSLEngine On

            DocumentRoot /usr/share/wordpress
            Alias /wp-content /home/wordpress/wp-content

            <Directory /usr/share/wordpress>
                    Options FollowSymLinks
                    AllowOverride Limit Options FileInfo
                    DirectoryIndex index.php
                    Require all granted
            </Directory>
            <Directory /home/wordpress/wp-content>
                    Options FollowSymLinks
                    Require all granted
            </Directory>

            SetEnvIfNoCase ^Authorization$ "(.+)" HTTP_AUTHORIZATION=$1
            <FilesMatch ".+\.php$">
                    SetHandler "proxy:unix:/run/php/wordpress.sock|fcgi://localhost"
            </FilesMatch>
    </VirtualHost>

This is the main part of the config. `SSLEngine On` is a shorthand for a full SSL configuration which I have placed in `/etc/apache2/conf-available` so it applies to all sites. `DocumentRoot` sets the root path of the application, which is the same for all installations. Only the `wp-content` directory contains userdata. The directory entries are mostly access control because the default configuration does not allow serving files from those paths. The `SetEnvIfNoCase` line is necessary to pass the authorization header to FPM. The `FilesMatch` section sets the handler socket for PHP files.
    
    <VirtualHost *:80>
            ServerName wordpress.yepoleb.at
            CustomLog ${APACHE_LOG_DIR}/wordpress.log combined

            RewriteEngine On
            RewriteCond %{REQUEST_URI} !/.well-known/acme-challenge
            RewriteRule ^/?(.*) https://wordpress.yepoleb.at/$1 [END,R=permanent]
    </VirtualHost>

This part is just a more complicated HTTP to HTTPS redirect with an exception for certbot webroot challenges. There are a few modules that also need to be enabled:

    sudo a2enmod rewrite setenvif proxy_fcgi ssl

Enable the site and restart Apache.

    sudo a2ensite wordpress
    sudo systemctl restart apache2

### Configuring Wordpress

The template configuration can be copied from the Wordpress installation directory.

    sudo cp /usr/share/wordpress/wp-config-sample.php /etc/wordpress/config-wordpress.yepoleb.at.php

I set the following values:
    
    define('DB_NAME', 'wordpress');
    define('DB_USER', 'wordpress');
    define('DB_PASSWORD', '');
    define('DB_HOST', 'localhost:/var/run/mysqld/mysqld.sock');
    define('DB_CHARSET', 'utf8mb4');
    define('DB_COLLATE', '');
    define('WP_CONTENT_DIR', '/home/wordpress/wp-content');

The `WP_CONTENT_DIR` line is the most significant value because it changes where userdata is stored. There are also a few entries for salt values which I set using Python's `secrets.token_hex(32)` because I'm too paranoid to use a web generator.

### Installing theme

This setup already works pretty well, but Wordpress will complain about a missing theme. This needs to be installed and linked in the appropriate directory.

    sudo apt install wordpress-theme-twentynineteen
    sudo -u wordpress ln -s /usr/share/wordpress/wp-content/themes/twentynineteen /home/wordpress/wp-content/themes/twentynineteen
    
### Software versions

* Debian 10 Buster
* Wordpress 5.0.12
* PHP-FPM 7.3
* Apache2 2.4.38
