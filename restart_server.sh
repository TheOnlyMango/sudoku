#!/bin/bash
# Helper script to restart the chat server on main-win

echo "Connecting to main-win..."
expect << 'EOFMAIN'
set timeout 30
spawn ssh shelb@main-win
expect {
    "password:" {
        send "o3s2-O2ll-!@#$\r"
    }
}
expect ">"
send "cd claude\\sudoku\r"
expect ">"
send "taskkill /F /IM python.exe 2>nul\r"
expect ">"
send "timeout /t 2 >nul\r"
expect ">"
send "start /B python chat_server.py\r"
expect ">"
send "timeout /t 2\r"
expect ">"
send "exit\r"
expect eof
EOFMAIN

echo "Server restarted!"
