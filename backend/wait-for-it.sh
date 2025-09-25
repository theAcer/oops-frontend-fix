#!/bin/bash
# wait-for-it.sh

set -ex # Added -x for shell debugging

host="$1"
port="$2"
shift 2
# Capture the remaining arguments as a single command string to preserve operators like '&&'
cmd="$*"

until PGPASSWORD=$POSTGRES_PASSWORD pg_isready -h "$host" -p "$port" -U postgres
do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

# Wait for Redis
until redis-cli -h redis ping;
do
  >&2 echo "Redis is unavailable - sleeping"
  sleep 1
done

>&2 echo "Redis is up - executing command"

# Execute the command string via a login shell to interpret operators properly
exec /bin/bash -lc "$cmd" 