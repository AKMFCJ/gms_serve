#!/bin/bash
read name
sed -i /$name\",no-port-forwarding,no-X11-forwarding,no-agent-forwarding,no-pty/d /home/git/.ssh/authorized_keys