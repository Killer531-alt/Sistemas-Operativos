#!/usr/bin/env bash
set -euo pipefail

BASE="/home/ubuntu/parcial-so/archivos"
ORIGEN="$BASE/entrada"

for carpeta in documentos imagenes trabajo comprimidos otros; do
    mkdir -p "$BASE/$carpeta"
done

find "$ORIGEN" -maxdepth 1 -type f -print0 |
while IFS= read -r -d '' archivo; do
    nombre="${archivo##*/}"
    extension="${nombre##*.}"
    extension="${extension,,}"

    case "$extension" in
        pdf|txt|doc|docx|odt|rtf)
            destino="documentos"
            ;;
        jpg|jpeg|png|gif|bmp|webp)
            destino="imagenes"
            ;;
        sh|py|js|html|css|conf|json|yaml|yml|ini|csv)
            destino="trabajo"
            ;;
        zip|tar|gz|bz2|xz|7z)
            destino="comprimidos"
            ;;
        *)
            destino="otros"
            ;;
    esac

    if [[ -e "$BASE/$destino/$nombre" ]]; then
        echo "OMITIDO: $nombre ya existe en $destino"
        continue
    fi

    mv -- "$archivo" "$BASE/$destino/$nombre"
    echo "CLASIFICADO: $nombre -> $destino/"
done

echo
echo "Resumen de archivos clasificados:"
for carpeta in entrada documentos imagenes trabajo comprimidos otros; do
    cantidad=$(find "$BASE/$carpeta" -maxdepth 1 -type f | wc -l)
    printf "%-12s %s archivo(s)\n" "$carpeta" "$cantidad"
done

echo
echo "Proceso finalizado."