#!/bin/bash
tmux new-session -d -s trading
tmux split-window -v "tail -f logs/trades/profit.log"
tmux split-window -v "tail -f logs/trades/margin.log"
tmux split-window -v "tail -f logs/trades/ccxt.log"
tmux attach -t trading
