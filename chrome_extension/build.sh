#!/bin/bash
set -e

rm -rf dist

if [ "$1" = "prod" ]; then
    NODE_ENV=production node build.js
    zip -r dist.zip dist
    echo "Build complete → dist/ and dist.zip"
else
    node build.js
fi