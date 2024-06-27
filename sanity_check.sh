#!/bin/bash

# Check if /home/root/bird/dev/dev.json exists
if [ ! -f "/home/root/bird/dev/dev.json" ]; then
    echo "/home/root/bird/dev/dev.json does not exist."
    echo "mount bird at /home/root so that bird/dev/dev/json is at /home/root/bird/dev/dev.json"
    exit
fi

# Check if /home/root/bird/test/test.json exists
if [ ! -f "/home/root/bird/test/test.json" ]; then
    echo "/home/root/bird/test/test.json does not exist."
    echo "mount bird at /home/root so that bird/test/test/json is at /home/root/bird/test/test.json"
    exit
fi

echo "all good"