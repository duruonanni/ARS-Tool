#!/bin/bash
cd "$(dirname "$0")"

# 启动 Python 服务（后台）
python3 lenovo_spec_server.py &
PY_PID=$!

# 等服务就绪
sleep 1.5

# 自动在浏览器打开工具页面
open "http://localhost:9527/"

# 等待服务进程（前台保持，Ctrl+C 可关闭）
wait $PY_PID
