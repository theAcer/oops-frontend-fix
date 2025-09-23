#!/bin/bash
# wait-for-it.sh

set -ex # Added -x for shell debugging

host="$1"
port="$2"
shift 2
cmd="$@"

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

exec $cmd 