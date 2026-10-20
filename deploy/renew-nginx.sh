#!/bin/sh
# Certbot deploy hook for the active BaoTa Nginx (not /usr/sbin/nginx).
set -eu
/www/server/nginx/sbin/nginx -t
/www/server/nginx/sbin/nginx -s reload
