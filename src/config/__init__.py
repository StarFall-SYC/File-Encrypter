#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置模块初始化
"""

from .config import Config, config
from .app_settings import AppSettings, settings

__all__ = ['Config', 'config', 'AppSettings', 'settings'] 