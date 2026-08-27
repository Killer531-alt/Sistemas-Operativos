#!/bin/bash
# Proceso de sumas para g2 - suma hasta que pasen 40 segundos

contador=0
suma_total=0
tiempo_fin=$(( $(date +%s) + 40 ))

echo "Iniciando sumas... el proceso durará 40 segundos"

while [ $(date +%s) -lt $tiempo_fin ]; do
    suma_total=$((suma_total + contador))
    echo "[$contador] Suma acumulada: $suma_total - $(date +%T)"
    contador=$((contador + 1))
    sleep 1
done

echo "Finalizado. Total sumado: $suma_total"