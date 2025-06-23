if [ -z "$1" ]; then
  echo "Erro: Você precisa fornecer o nome do arquivo de exemplo." >&2
  echo "Uso: $0 <nome_do_arquivo>" >&2
  exit 1
fi

FILENAME=$1

if [ -f "$FILENAME" ]; then
    python3 src/main.py $FILENAME --static --json-log static_log.jsonl #> /usr/dev/null > 2>&1
    python3 src/main.py $FILENAME --dynamic --json-log dynamic_log.jsonl #> /usr/dev/null > 2>&1
    python3 visualization.py --static-log static_log.jsonl --dynamic-log dynamic_log.jsonl --delay 1.2
else
  echo "O arquivo '$FILENAME' não foi encontrado."
fi
