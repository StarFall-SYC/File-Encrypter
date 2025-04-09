#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
应用热更新管理器 - 负责协调语言和主题的实时更新
"""

import os
from typing import List, Dict, Any, Optional, Callable
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow

from .logger import logger
from .translator import translator
from .theme_manager import theme_manager

class AppUpdater:
    """应用热更新管理器类，用于协调应用程序的语言和主题更新"""
    
    def __init__(self):
        """初始化应用热更新管理器"""
        self.callback_widgets = []  # 需要更新的窗口部件列表
        self.app_instance = None    # 应用程序实例
    
    def register_app(self, app: QApplication):
        """
        注册应用程序实例
        
        Args:
            app: QApplication实例
        """
        self.app_instance = app
        logger.info("应用更新管理器已注册应用程序实例")
    
    def register_widget(self, widget: QWidget):
        """
        注册需要更新的窗口部件
        
        Args:
            widget: 需要更新的QWidget或其子类实例
        """
        if widget not in self.callback_widgets:
            self.callback_widgets.append(widget)
            logger.debug(f"注册窗口部件到更新器: {widget.__class__.__name__}")
    
    def update_language(self, lang_code: str):
        """
        更新应用程序语言
        
        Args:
            lang_code: 语言代码
        
        Returns:
            bool: 是否更新成功
        """
        try:
            # 切换语言
            if not translator.switch_language(lang_code):
                logger.warning(f"切换语言失败: {lang_code}")
                return False
            
            # 通知所有注册的窗口部件更新文本
            self._update_all_widgets()
            
            logger.info(f"应用语言已更新为: {lang_code}")
            return True
        except Exception as e:
            logger.error(f"更新语言时出错: {str(e)}")
            return False
    
    def update_theme(self, theme_name: str):
        """
        更新应用程序主题
        
        Args:
            theme_name: 主题名称
        
        Returns:
            bool: 是否更新成功
        """
        try:
            # 验证主题是否存在
            if theme_name not in theme_manager.get_available_themes():
                logger.warning(f"主题不存在: {theme_name}")
                return False
            
            # 应用主题
            if self.app_instance:
                theme_manager.apply_theme(theme_name, self.app_instance)
            else:
                theme_manager.apply_theme(theme_name)
            
            # 通知所有注册的窗口部件更新文本和样式
            self._update_all_widgets()
            
            logger.info(f"应用主题已更新为: {theme_name}")
            return True
        except Exception as e:
            logger.error(f"更新主题时出错: {str(e)}")
            return False
    
    def _update_all_widgets(self):
        """更新所有注册的窗口部件"""
        if not self.callback_widgets:
            logger.warning("没有注册的窗口部件需要更新")
            return
        
        for widget in self.callback_widgets:
            try:
                if hasattr(widget, 'update_ui_texts'):
                    widget.update_ui_texts()
                    logger.debug(f"已更新窗口部件文本: {widget.__class__.__name__}")
                
                if hasattr(widget, 'update_ui_style'):
                    widget.update_ui_style()
                    logger.debug(f"已更新窗口部件样式: {widget.__class__.__name__}")
                    
            except Exception as e:
                logger.error(f"更新窗口部件时出错: {str(e)}")
    
    def clear_widgets(self):
        """清除所有注册的窗口部件"""
        self.callback_widgets.clear()
        logger.debug("已清除所有注册的窗口部件")

# 创建全局应用更新器实例
app_updater = AppUpdater() 