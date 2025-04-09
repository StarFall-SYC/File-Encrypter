#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
应用程序设置模块，管理UI相关设置
"""

import os
import json
from typing import Dict, Any, Optional
from .config import config
from ..utils.logger import logger

class AppSettings:
    """应用程序设置管理类"""
    
    def __init__(self):
        """初始化应用程序设置"""
        # 加载设置
        self.settings = {}
        self._load_defaults()
        self._load_from_config()
        
        logger.info("应用程序设置初始化完成")
    
    def _load_defaults(self):
        """加载默认设置"""
        self.settings = {
            "ui": {
                "language": "zh_CN",
                "theme": "light",
                "show_toolbar": True,
                "show_statusbar": True,
                "dark_mode": False
            },
            "encryption": {
                "default_algorithm": "AES-256-CBC",
                "chunk_size": 4096,
                "verify_after_encryption": True,
                "secure_delete_original": False
            },
            "paths": {
                "last_directory": os.path.expanduser("~"),
                "temp_directory": os.path.join(os.path.expanduser("~"), ".file_encrypter", "temp")
            }
        }
    
    def _load_from_config(self):
        """从配置加载设置"""
        # UI设置
        self.settings["ui"]["language"] = config.get("app", "language", "zh_CN")
        self.settings["ui"]["theme"] = config.get("app", "theme", "light")
        self.settings["ui"]["show_toolbar"] = config.get("app", "show_toolbar", True)
        self.settings["ui"]["show_statusbar"] = config.get("app", "show_statusbar", True)
        self.settings["ui"]["dark_mode"] = config.get("app", "dark_mode", False)
        
        # 加密设置
        self.settings["encryption"]["default_algorithm"] = config.get("encryption", 
                                                                  "default_algorithm", 
                                                                  "AES-256-CBC")
        self.settings["encryption"]["chunk_size"] = config.get("encryption", "chunk_size", 4096)
        self.settings["encryption"]["verify_after_encryption"] = config.get("encryption", 
                                                                       "verify_after_encryption", 
                                                                       True)
        self.settings["encryption"]["secure_delete_original"] = config.get("encryption", 
                                                                      "secure_delete_original", 
                                                                      False)
        
        # 路径设置
        self.settings["paths"]["last_directory"] = config.get("paths", "last_open_dir", 
                                                            os.path.expanduser("~"))
        self.settings["paths"]["temp_directory"] = config.get("paths", "temp_dir", 
                                                           os.path.join(os.path.expanduser("~"), 
                                                                      ".file_encrypter", "temp"))
    
    def get(self, section: str, key: str, default=None) -> Any:
        """
        获取设置值
        
        Args:
            section: 设置部分
            key: 设置键
            default: 默认值
            
        Returns:
            Any: 设置值
        """
        if section in self.settings and key in self.settings[section]:
            return self.settings[section][key]
        return default
    
    def set(self, section: str, key: str, value: Any) -> bool:
        """
        设置值
        
        Args:
            section: 设置部分
            key: 设置键
            value: 设置值
            
        Returns:
            bool: 是否成功
        """
        if section not in self.settings:
            self.settings[section] = {}
        
        self.settings[section][key] = value
        
        # 同步到全局配置
        return config.set(section, key, value)
    
    def save_all(self) -> bool:
        """
        保存所有设置到配置
        
        Returns:
            bool: 是否成功
        """
        try:
            # UI设置
            for key, value in self.settings["ui"].items():
                config.set("app", key, value)
            
            # 加密设置
            for key, value in self.settings["encryption"].items():
                config.set("encryption", key, value)
            
            # 路径设置
            config.set("paths", "last_open_dir", self.settings["paths"]["last_directory"])
            config.set("paths", "temp_dir", self.settings["paths"]["temp_directory"])
            
            return True
        except Exception as e:
            logger.error(f"保存设置失败: {str(e)}")
            return False
    
    def reset(self, section: Optional[str] = None) -> bool:
        """
        重置设置
        
        Args:
            section: 要重置的部分，None表示重置所有
            
        Returns:
            bool: 是否成功
        """
        self._load_defaults()
        if section:
            return config.reset(section)
        else:
            return config.reset()

# 全局设置实例
settings = AppSettings() 