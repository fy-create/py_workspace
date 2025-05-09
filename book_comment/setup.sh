#!/bin/bash

rm -rf myvenv

# 创建虚拟环境
python3.11 -m venv myvenv

# 激活虚拟环境
source myvenv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

