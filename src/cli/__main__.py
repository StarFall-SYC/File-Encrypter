#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""CLI入口模块"""

import sys
import os

# 确保父目录在Python路径中，以支持相对导入
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from src.cli import main
except ImportError:
    # 如果导入失败
    print("cli导入失败")

if __name__ == "__main__":
    sys.exit(main()) 