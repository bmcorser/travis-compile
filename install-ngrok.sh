#!/bin/bash
if [ -f ngrok ]; then
    echo "ngrok is present"
else
    echo "installing ngrok"
    platform=$(uname -s)
    if [ $platform == "Darwin" ]; then
        wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-darwin-amd64.zip -O ngrok.zip
    elif [ $platform == "Linux" ]; then
        wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip -O ngrok.zip
    else
        exit 'Unsupported platform'
    fi
    unzip ngrok.zip
    rm -v ngrok.zip
fi
