#!/bin/bash

DOMAIN="spendsplif.com"
CERT="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"

while [ ! -f "$CERT" ]; do
    echo "Ожидание генерации сертификата для $DOMAIN..."
    sleep 5
done

echo "Сертификат для $DOMAIN найден, запускаем Nginx..."
nginx -g "daemon off;"