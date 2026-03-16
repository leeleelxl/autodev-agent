#!/bin/sh
set -e
# 修复：强制私钥 600 权限
chmod 600 /tmp/jwtRS256.key
exec "$@"