#!/bin/bash
# Proceso disparado para g1 - abre Wikipedia cada 40 segundos

while true; do
    # Abre una página aleatoria de Wikipedia
    xdg-open "https://es.wikipedia.org/wiki/Special:Random" &
    echo "[$(date)] Abriendo Wikipedia - PID del navegador: $!"
    sleep 40
done