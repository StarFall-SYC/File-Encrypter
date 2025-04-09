#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主题管理器模块 - 提供界面主题支持
"""

import os
from typing import Dict, List, Optional, Tuple
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from ..utils.logger import logger

class ThemeManager:
    """主题管理器类，用于管理界面主题"""
    
    def __init__(self):
        """初始化主题管理器"""
        self.themes = {}  # 主题字典
        self.current_theme = None  # 当前主题名称
        self.default_theme = "light"  # 默认主题
        
        # 初始化内置主题
        self._initialize_themes()
    
    def _initialize_themes(self):
        """初始化内置主题"""
        # 浅色主题
        self.themes["light"] = {
            'name': 'light',
            'primary': '#0078d7',
            'secondary': '#5c6bc0',
            'background': '#f5f5f5',
            'surface': '#ffffff',
            'error': '#d32f2f',
            'text_primary': '#212121',
            'text_secondary': '#757575',
            'dark': False,
            'stylesheet': self._get_light_stylesheet()
        }
        
        # 深色主题
        self.themes["dark"] = {
            'name': 'dark',
            'primary': '#1976d2',
            'secondary': '#7986cb',
            'background': '#303030',
            'surface': '#424242',
            'error': '#ef5350',
            'text_primary': '#ffffff',
            'text_secondary': '#b0bec5',
            'dark': True,
            'stylesheet': self._get_dark_stylesheet()
        }
        
        # 蓝色主题
        self.themes["blue"] = {
            'name': 'blue',
            'primary': '#1565c0',
            'secondary': '#1e88e5',
            'background': '#eceff1',
            'surface': '#ffffff',
            'error': '#d50000',
            'text_primary': '#263238',
            'text_secondary': '#546e7a',
            'dark': False,
            'stylesheet': self._get_blue_stylesheet()
        }
        
        # 绿色主题
        self.themes["green"] = {
            'name': 'green',
            'primary': '#2e7d32',
            'secondary': '#43a047',
            'background': '#f1f8e9',
            'surface': '#ffffff',
            'error': '#c62828',
            'text_primary': '#212121',
            'text_secondary': '#757575',
            'dark': False,
            'stylesheet': self._get_green_stylesheet()
        }
        
        # 紫色主题
        self.themes["purple"] = {
            'name': 'purple',
            'primary': '#6a1b9a',
            'secondary': '#8e24aa',
            'background': '#f3e5f5',
            'surface': '#ffffff',
            'error': '#d50000',
            'text_primary': '#212121',
            'text_secondary': '#757575',
            'dark': False,
            'stylesheet': self._get_purple_stylesheet()
        }
        
        logger.info(f"初始化了 {len(self.themes)} 个主题")
    
    def get_available_themes(self) -> List[str]:
        """
        获取所有可用主题
        
        Returns:
            List[str]: 主题名称列表
        """
        return list(self.themes.keys())
    
    def apply_theme(self, theme_name: str, app: QApplication = None) -> bool:
        """
        应用主题
        
        Args:
            theme_name: 主题名称
            app: QApplication实例，如果为None则使用QApplication.instance()
            
        Returns:
            bool: 应用是否成功
        """
        if theme_name not in self.themes:
            logger.warning(f"主题不存在: {theme_name}")
            return False
        
        theme = self.themes[theme_name]
        
        try:
            # 获取应用实例
            if app is None:
                app = QApplication.instance()
                if app is None:
                    logger.error("未找到QApplication实例")
                    return False
            
            # 强制清除所有现有样式，避免混合主题问题
            app.setStyleSheet("")
            
            # 确保所有控件先重置样式
            for widget in app.allWidgets():
                widget.setStyleSheet("")
                widget.style().unpolish(widget)
            
            # 设置应用调色板
            self._set_palette(app, theme)
            
            # 设置应用样式表
            app.setStyleSheet(theme.get('stylesheet', ''))
            
            # 更新当前主题
            self.current_theme = theme_name
            logger.info(f"应用主题: {theme_name}")
            
            # 强制更新所有控件
            for widget in app.allWidgets():
                widget.style().polish(widget)
                widget.update()
            
            return True
        except Exception as e:
            logger.error(f"应用主题失败: {str(e)}")
            return False
    
    def _set_palette(self, app: QApplication, theme: Dict):
        """
        设置应用调色板
        
        Args:
            app: QApplication实例
            theme: 主题字典
        """
        palette = QPalette()
        
        # 设置颜色
        if theme.get('dark', False):
            # 深色模式
            palette.setColor(QPalette.Window, QColor(theme.get('background', '#303030')))
            palette.setColor(QPalette.WindowText, QColor(theme.get('text_primary', '#ffffff')))
            palette.setColor(QPalette.Base, QColor(theme.get('surface', '#424242')))
            palette.setColor(QPalette.AlternateBase, QColor(theme.get('background', '#303030')))
            palette.setColor(QPalette.ToolTipBase, QColor(theme.get('surface', '#424242')))
            palette.setColor(QPalette.ToolTipText, QColor(theme.get('text_primary', '#ffffff')))
            palette.setColor(QPalette.Text, QColor(theme.get('text_primary', '#ffffff')))
            palette.setColor(QPalette.Button, QColor(theme.get('surface', '#424242')))
            palette.setColor(QPalette.ButtonText, QColor(theme.get('text_primary', '#ffffff')))
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(theme.get('primary', '#1976d2')))
            palette.setColor(QPalette.Highlight, QColor(theme.get('primary', '#1976d2')))
            palette.setColor(QPalette.HighlightedText, QColor(theme.get('text_primary', '#ffffff')))
        else:
            # 浅色模式
            palette.setColor(QPalette.Window, QColor(theme.get('background', '#f5f5f5')))
            palette.setColor(QPalette.WindowText, QColor(theme.get('text_primary', '#212121')))
            palette.setColor(QPalette.Base, QColor(theme.get('surface', '#ffffff')))
            palette.setColor(QPalette.AlternateBase, QColor(theme.get('background', '#f5f5f5')))
            palette.setColor(QPalette.ToolTipBase, QColor(theme.get('surface', '#ffffff')))
            palette.setColor(QPalette.ToolTipText, QColor(theme.get('text_primary', '#212121')))
            palette.setColor(QPalette.Text, QColor(theme.get('text_primary', '#212121')))
            palette.setColor(QPalette.Button, QColor(theme.get('surface', '#ffffff')))
            palette.setColor(QPalette.ButtonText, QColor(theme.get('text_primary', '#212121')))
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(theme.get('primary', '#0078d7')))
            palette.setColor(QPalette.Highlight, QColor(theme.get('primary', '#0078d7')))
            palette.setColor(QPalette.HighlightedText, Qt.white)
        
        # 设置应用调色板
        app.setPalette(palette)
    
    def _get_light_stylesheet(self) -> str:
        """
        获取浅色主题样式表
        
        Returns:
            str: 样式表字符串
        """
        return """
        /* 全局样式重置，避免与其他主题混合 */
        * {
            font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
        }
        
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        QTabWidget::pane {
            border: 1px solid #e0e0e0;
            background-color: #ffffff;
        }
        
        QTabBar::tab {
            background-color: #f0f0f0;
            padding: 8px 12px;
            border: 1px solid #e0e0e0;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff;
            border-bottom-color: #ffffff;
        }
        
        QPushButton {
            background-color: #0078d7;
            color: white;
            border-radius: 4px;
            border: none;
            padding: 6px 12px;
            outline: none;
        }
        
        QPushButton:hover {
            background-color: #106ebe;
        }
        
        QPushButton:pressed {
            background-color: #005a9e;
        }
        
        QPushButton:disabled {
            background-color: #cccccc;
            color: #999999;
        }
        
        QComboBox {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 4px 8px;
            color: #212121;
        }
        
        QComboBox:focus {
            border: 1px solid #0078d7;
        }
        
        QComboBox:hover {
            border: 1px solid #0078d7;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: none;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }
        
        QComboBox::down-arrow {
            image: url(none);
            width: 14px;
            height: 14px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #212121;
            selection-background-color: #e3f2fd;
            selection-color: #212121;
            border: 1px solid #e0e0e0;
            outline: 0;
        }
        
        QComboBox QAbstractItemView::item {
            background-color: transparent;
            color: #212121;
            border: none;
            padding: 4px 8px;
            min-height: 24px;
        }
        
        QComboBox QAbstractItemView::item:selected {
            background-color: #e3f2fd;
            color: #0078d7;
        }
        
        QComboBox QAbstractItemView::item:hover {
            background-color: #e0e0e0;
            color: #212121 !important;
            border: none;
            outline: none;
        }
        
        QLineEdit {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 4px 8px;
        }
        
        QLineEdit:focus {
            border: 1px solid #0078d7;
        }
        
        QGroupBox {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            margin-top: 20px;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: #212121;
        }
        
        QCheckBox {
            color: #212121;
        }
        
        QCheckBox::indicator:checked {
            background-color: #0078d7;
            border: 1px solid #0078d7;
        }
        
        QTreeView {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
        }
        
        QTreeView::item:selected {
            background-color: #e3f2fd;
            color: #212121;
        }
        
        QProgressBar {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: #ffffff;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #0078d7;
            width: 10px;
        }
        
        QScrollBar:vertical {
            border: 1px solid #e0e0e0;
            background: #f5f5f5;
            width: 15px;
            margin: 15px 0 15px 0;
        }
        
        QScrollBar::handle:vertical {
            background: #c0c0c0;
            min-height: 30px;
            border-radius: 3px;
        }
        
        QStatusBar {
            background-color: #f5f5f5;
            color: #757575;
            border-top: 1px solid #e0e0e0;
            font-size: 12px;
            min-height: 22px;
            padding: 2px;
        }
        
        QStatusBar::item {
            border: none;
            background: transparent;
        }
        """
    
    def _get_dark_stylesheet(self) -> str:
        """
        获取深色主题样式表
        
        Returns:
            str: 样式表字符串
        """
        return """
        /* 全局样式重置，避免与其他主题混合 */
        * {
            font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
        }
        
        QMainWindow {
            background-color: #303030;
            color: #ffffff;
        }
        
        QWidget {
            color: #ffffff;
        }
        
        QTabWidget::pane {
            border: 1px solid #212121;
            background-color: #424242;
        }
        
        QTabBar::tab {
            background-color: #303030;
            padding: 8px 12px;
            border: 1px solid #212121;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            color: #b0bec5;
        }
        
        QTabBar::tab:selected {
            background-color: #424242;
            border-bottom-color: #424242;
            color: #ffffff;
        }
        
        QPushButton {
            background-color: #1976d2;
            color: white;
            border-radius: 4px;
            border: none;
            padding: 6px 12px;
            outline: none;
        }
        
        QPushButton:hover {
            background-color: #2196f3;
        }
        
        QPushButton:pressed {
            background-color: #0d47a1;
        }
        
        QPushButton:disabled {
            background-color: #424242;
            color: #757575;
        }
        
        QComboBox {
            background-color: #424242;
            border: 1px solid #212121;
            border-radius: 4px;
            padding: 4px 8px;
            color: #ffffff;
        }
        
        QComboBox:hover {
            border: 1px solid #1976d2;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: none;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }
        
        QComboBox::down-arrow {
            image: url(none);
            width: 14px;
            height: 14px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #424242;
            color: #ffffff;
            selection-background-color: #1976d2;
            selection-color: #ffffff;
            border: 1px solid #212121;
            outline: 0;
        }
        
        QComboBox QAbstractItemView::item {
            background-color: transparent;
            color: #ffffff;
            border: none;
            padding: 4px 8px;
            min-height: 24px;
        }
        
        QComboBox QAbstractItemView::item:selected {
            background-color: #1976d2;
            color: #ffffff;
        }
        
        QComboBox QAbstractItemView::item:hover {
            background-color: #455a64;
            color: #eceff1 !important;
            border: none;
            outline: none;
        }
        
        QComboBox:focus {
            border: 1px solid #1976d2;
        }
        
        QLineEdit {
            background-color: #424242;
            border: 1px solid #212121;
            border-radius: 4px;
            padding: 4px 8px;
            color: #ffffff;
        }
        
        QLineEdit:focus {
            border: 1px solid #1976d2;
        }
        
        QGroupBox {
            border: 1px solid #212121;
            border-radius: 4px;
            margin-top: 20px;
            padding-top: 10px;
            color: #ffffff;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: #b0bec5;
        }
        
        QCheckBox {
            color: #ffffff;
        }
        
        QCheckBox::indicator:checked {
            background-color: #1976d2;
            border: 1px solid #1976d2;
        }
        
        QTreeView {
            background-color: #424242;
            color: #ffffff;
            border: 1px solid #212121;
        }
        
        QTreeView::item:selected {
            background-color: #1976d2;
            color: #ffffff;
        }
        
        QProgressBar {
            border: 1px solid #212121;
            border-radius: 4px;
            background-color: #303030;
            text-align: center;
            color: #ffffff;
        }
        
        QProgressBar::chunk {
            background-color: #1976d2;
            width: 10px;
        }
        
        QScrollBar:vertical {
            border: 1px solid #212121;
            background: #303030;
            width: 15px;
            margin: 15px 0 15px 0;
        }
        
        QScrollBar::handle:vertical {
            background: #424242;
            min-height: 30px;
            border-radius: 3px;
        }
        
        QStatusBar {
            background-color: #1c2529;
            color: #b0bec5;
            border-top: 1px solid #37474f;
            font-size: 12px;
            min-height: 22px;
            padding: 2px;
        }
        
        QStatusBar::item {
            border: none;
            background: transparent;
        }
        
        QLabel {
            color: #ffffff;
        }
        
        QMenu {
            background-color: #424242;
            color: #ffffff;
            border: 1px solid #212121;
        }
        
        QMenu::item:selected {
            background-color: #1976d2;
        }
        
        QMenuBar {
            background-color: #212121;
            color: #ffffff;
        }
        
        QMenuBar::item:selected {
            background-color: #424242;
        }
        """
    
    def _get_blue_stylesheet(self) -> str:
        """
        获取蓝色主题样式表
        
        Returns:
            str: 样式表字符串
        """
        return """
        /* 全局样式重置，避免与其他主题混合 */
        * {
            font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
        }
        
        QMainWindow {
            background-color: #eceff1;
        }
        
        QTabWidget::pane {
            border: 1px solid #b0bec5;
            background-color: #ffffff;
        }
        
        QTabBar::tab {
            background-color: #cfd8dc;
            padding: 8px 12px;
            border: 1px solid #b0bec5;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff;
            border-bottom-color: #ffffff;
        }
        
        QPushButton {
            background-color: #1565c0;
            color: white;
            border-radius: 4px;
            border: none;
            padding: 6px 12px;
            outline: none;
        }
        
        QPushButton:hover {
            background-color: #1976d2;
        }
        
        QPushButton:pressed {
            background-color: #0d47a1;
        }
        
        QPushButton:disabled {
            background-color: #b0bec5;
            color: #90a4ae;
        }
        
        QComboBox {
            background-color: #ffffff;
            border: 1px solid #b0bec5;
            border-radius: 4px;
            padding: 4px 8px;
            color: #263238;
        }
        
        QComboBox:hover {
            border: 1px solid #1565c0;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: none;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }
        
        QComboBox::down-arrow {
            image: url(none);
            width: 14px;
            height: 14px;
        }
        
        QComboBox:focus {
            border: 1px solid #1565c0;
        }
        
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #263238;
            selection-background-color: #bbdefb;
            selection-color: #1565c0;
            border: 1px solid #b0bec5;
            outline: 0;
        }
        
        QComboBox QAbstractItemView::item {
            background-color: transparent;
            color: #263238;
            border: none;
            padding: 4px 8px;
            min-height: 24px;
        }
        
        QComboBox QAbstractItemView::item:selected {
            background-color: #bbdefb;
            color: #1565c0;
        }
        
        QComboBox QAbstractItemView::item:hover {
            background-color: #bbdefb;
            color: #1565c0 !important;
            border: none;
            outline: none;
        }
        
        QLineEdit {
            background-color: #ffffff;
            border: 1px solid #b0bec5;
            border-radius: 4px;
            padding: 4px 8px;
            color: #263238;
        }
        
        QLineEdit:focus {
            border: 1px solid #1565c0;
        }
        
        QGroupBox {
            border: 1px solid #b0bec5;
            border-radius: 4px;
            margin-top: 20px;
            padding-top: 10px;
            color: #263238;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: #263238;
        }
        
        QCheckBox {
            color: #263238;
        }
        
        QCheckBox::indicator:checked {
            background-color: #1565c0;
            border: 1px solid #1565c0;
        }
        
        QTreeView {
            background-color: #ffffff;
            border: 1px solid #b0bec5;
            color: #263238;
        }
        
        QTreeView::item {
            color: #263238;
        }
        
        QTreeView::item:selected {
            background-color: #bbdefb;
            color: #263238;
        }
        
        QHeaderView::section {
            background-color: #eceff1;
            color: #263238;
            padding: 4px;
            border: 1px solid #b0bec5;
        }
        
        QProgressBar {
            border: 1px solid #b0bec5;
            border-radius: 4px;
            background-color: #ffffff;
            text-align: center;
            color: #263238;
        }
        
        QProgressBar::chunk {
            background-color: #1565c0;
            width: 10px;
        }
        
        QScrollBar:vertical {
            border: 1px solid #b0bec5;
            background: #eceff1;
            width: 15px;
            margin: 15px 0 15px 0;
        }
        
        QScrollBar::handle:vertical {
            background: #90a4ae;
            min-height: 30px;
            border-radius: 3px;
        }
        
        QStatusBar {
            background-color: #eceff1;
            color: #546e7a;
            border-top: 1px solid #cfd8dc;
            font-size: 12px;
            min-height: 22px;
            padding: 2px;
        }
        
        QStatusBar::item {
            border: none;
            background: transparent;
        }
        
        QLabel {
            color: #263238;
        }
        
        QMenu {
            background-color: #ffffff;
            color: #263238;
            border: 1px solid #b0bec5;
        }
        
        QMenu::item:selected {
            background-color: #bbdefb;
            color: #1565c0;
        }
        
        QMenuBar {
            background-color: #eceff1;
            color: #263238;
            border-bottom: 1px solid #b0bec5;
        }
        
        QMenuBar::item:selected {
            background-color: #bbdefb;
            color: #1565c0;
        }
        """
    
    def _get_green_stylesheet(self) -> str:
        """
        获取绿色主题样式表
        
        Returns:
            str: 样式表字符串
        """
        return """
        /* 全局样式重置，避免与其他主题混合 */
        * {
            font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
        }
        
        QMainWindow {
            background-color: #e8f5e9;
        }
        
        QTabWidget::pane {
            border: 1px solid #c5e1a5;
            background-color: #ffffff;
        }
        
        QTabBar::tab {
            background-color: #dcedc8;
            padding: 8px 12px;
            border: 1px solid #c5e1a5;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff;
            border-bottom-color: #ffffff;
        }
        
        QPushButton {
            background-color: #2e7d32;
            color: white;
            border-radius: 4px;
            border: none;
            padding: 6px 12px;
            outline: none;
        }
        
        QPushButton:hover {
            background-color: #388e3c;
        }
        
        QPushButton:pressed {
            background-color: #1b5e20;
        }
        
        QPushButton:disabled {
            background-color: #c5e1a5;
            color: #9e9e9e;
        }
        
        QComboBox {
            background-color: #ffffff;
            border: 1px solid #c5e1a5;
            border-radius: 4px;
            padding: 4px 8px;
            color: #33691e;
        }
        
        QComboBox:hover {
            border: 1px solid #2e7d32;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: none;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }
        
        QComboBox::down-arrow {
            image: url(none);
            width: 14px;
            height: 14px;
        }
        
        QComboBox:focus {
            border: 1px solid #2e7d32;
        }
        
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #33691e;
            selection-background-color: #c8e6c9;
            selection-color: #2e7d32;
            border: 1px solid #c5e1a5;
            outline: 0;
        }
        
        QComboBox QAbstractItemView::item {
            background-color: transparent;
            color: #33691e;
            border: none;
            padding: 4px 8px;
            min-height: 24px;
        }
        
        QComboBox QAbstractItemView::item:selected {
            background-color: #c8e6c9;
            color: #2e7d32;
        }
        
        QComboBox QAbstractItemView::item:hover {
            background-color: #a5d6a7;
            color: #2e7d32 !important;
            border: none;
            outline: none;
        }
        
        QLineEdit {
            background-color: #ffffff;
            border: 1px solid #c5e1a5;
            border-radius: 4px;
            padding: 4px 8px;
        }
        
        QLineEdit:focus {
            border: 1px solid #2e7d32;
        }
        
        QGroupBox {
            border: 1px solid #c5e1a5;
            border-radius: 4px;
            margin-top: 20px;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: #33691e;
        }
        
        QCheckBox::indicator:checked {
            background-color: #2e7d32;
            border: 1px solid #2e7d32;
        }
        
        QTreeView {
            background-color: #ffffff;
            border: 1px solid #c5e1a5;
        }
        
        QTreeView::item:selected {
            background-color: #c8e6c9;
            color: #33691e;
        }
        
        QProgressBar {
            border: 1px solid #c5e1a5;
            border-radius: 4px;
            background-color: #ffffff;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #2e7d32;
            width: 10px;
        }
        
        QScrollBar:vertical {
            border: 1px solid #c5e1a5;
            background: #e8f5e9;
            width: 15px;
            margin: 15px 0 15px 0;
        }
        
        QScrollBar::handle:vertical {
            background: #aed581;
            min-height: 30px;
            border-radius: 3px;
        }
        
        QStatusBar {
            background-color: #e8f5e9;
            color: #2e7d32;
            border-top: 1px solid #c8e6c9;
            font-size: 12px;
            min-height: 22px;
            padding: 2px;
        }
        
        QStatusBar::item {
            border: none;
            background: transparent;
        }
        """
    
    def _get_purple_stylesheet(self) -> str:
        """
        获取紫色主题样式表
        
        Returns:
            str: 样式表字符串
        """
        return """
        /* 全局样式重置，避免与其他主题混合 */
        * {
            font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
        }
        
        QMainWindow {
            background-color: #f3e5f5;
        }
        
        QTabWidget::pane {
            border: 1px solid #e1bee7;
            background-color: #ffffff;
        }
        
        QTabBar::tab {
            background-color: #e1bee7;
            padding: 8px 12px;
            border: 1px solid #ce93d8;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff;
            border-bottom-color: #ffffff;
        }
        
        QPushButton {
            background-color: #6a1b9a;
            color: white;
            border-radius: 4px;
            border: none;
            padding: 6px 12px;
            outline: none;
        }
        
        QPushButton:hover {
            background-color: #8e24aa;
        }
        
        QPushButton:pressed {
            background-color: #4a148c;
        }
        
        QPushButton:disabled {
            background-color: #e1bee7;
            color: #9e9e9e;
        }
        
        QComboBox {
            background-color: #ffffff;
            border: 1px solid #e1bee7;
            border-radius: 4px;
            padding: 4px 8px;
            color: #4a148c;
        }
        
        QComboBox:hover {
            border: 1px solid #8e24aa;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: none;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }
        
        QComboBox::down-arrow {
            image: url(none);
            width: 14px;
            height: 14px;
        }
        
        QComboBox:focus {
            border: 1px solid #8e24aa;
        }
        
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #4a148c;
            selection-background-color: #f3e5f5;
            selection-color: #8e24aa;
            border: 1px solid #e1bee7;
            outline: 0;
        }
        
        QComboBox QAbstractItemView::item {
            background-color: transparent;
            color: #4a148c;
            border: none;
            padding: 4px 8px;
            min-height: 24px;
        }
        
        QComboBox QAbstractItemView::item:selected {
            background-color: #f3e5f5;
            color: #8e24aa;
        }
        
        QComboBox QAbstractItemView::item:hover {
            background-color: #ce93d8;
            color: #4a148c !important;
            border: none;
            outline: none;
        }
        
        QLineEdit {
            background-color: #ffffff;
            border: 1px solid #e1bee7;
            border-radius: 4px;
            padding: 4px 8px;
        }
        
        QLineEdit:focus {
            border: 1px solid #8e24aa;
        }
        
        QGroupBox {
            border: 1px solid #e1bee7;
            border-radius: 4px;
            margin-top: 20px;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: #4a148c;
        }
        
        QCheckBox::indicator:checked {
            background-color: #8e24aa;
            border: 1px solid #8e24aa;
        }
        
        QTreeView {
            background-color: #ffffff;
            border: 1px solid #e1bee7;
        }
        
        QTreeView::item:selected {
            background-color: #f3e5f5;
            color: #4a148c;
        }
        
        QProgressBar {
            border: 1px solid #e1bee7;
            border-radius: 4px;
            background-color: #ffffff;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #8e24aa;
            width: 10px;
        }
        
        QScrollBar:vertical {
            border: 1px solid #e1bee7;
            background: #f3e5f5;
            width: 15px;
            margin: 15px 0 15px 0;
        }
        
        QScrollBar::handle:vertical {
            background: #ce93d8;
            min-height: 30px;
            border-radius: 3px;
        }
        
        QStatusBar {
            background-color: #f3e5f5;
            color: #6a1b9a;
            border-top: 1px solid #e1bee7;
            font-size: 12px;
            min-height: 22px;
            padding: 2px;
        }
        
        QStatusBar::item {
            border: none;
            background: transparent;
        }
        """
    
    def get_current_theme(self) -> Optional[Dict]:
        """
        获取当前主题信息
        
        Returns:
            Optional[Dict]: 主题字典
        """
        if self.current_theme is None:
            return self.themes.get(self.default_theme)
        return self.themes.get(self.current_theme)

# 创建全局主题管理器实例
theme_manager = ThemeManager() 