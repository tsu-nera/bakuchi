#!/bin/bash
tmux new-session -d -s trading
tmux split-window -v "tail -f /home/tsu-nera/repo/bakuchi/logs/cron/asset.log"
tmux split-window -v "tail -f logs/margin.log"
tmux split-window -v "tail -f logs/ccxt.log"
tmux attach -t trading
