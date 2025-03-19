#!/bin/bash

SERVER_IP="server"
SERVER_PORT=12345

MSG="Hola mundo"

SERVER_RESPONSE=$(echo "$MSG" | docker run -i --rm --network tp0_testing_net gophernet/netcat "$SERVER_IP" "$SERVER_PORT")

if [ "$MSG" = "$SERVER_RESPONSE" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi