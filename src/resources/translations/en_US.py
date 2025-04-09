#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
English (US) language resource file
"""

translations = {
    # Main Window
    "app_title": "File Encrypter",
    "ready": "Ready",
    
    # Menu
    "menu_file": "File",
    "menu_encrypt": "Encrypt Files",
    "menu_decrypt": "Decrypt Files",
    "menu_exit": "Exit",
    "menu_tools": "Tools",
    "menu_keys": "Key Management",
    "menu_settings": "Settings",
    "menu_help": "Help",
    "menu_about": "About",
    
    # Tabs
    "tab_encrypt": "Encrypt",
    "tab_decrypt": "Decrypt",
    "tab_keys": "Keys",
    "tab_monitor": "File Monitor",
    "tab_settings": "Settings",
    
    # Encrypt/Decrypt Tab
    "encrypt_title": "File Encryption",
    "encrypt_desc": "Encrypt your files and folders to ensure data security",
    "decrypt_title": "File Decryption",
    "decrypt_desc": "Decrypt previously encrypted files to restore original data",
    "algo_group": "Encryption Algorithm",
    "algo_symmetric": "Symmetric",
    "algo_asymmetric": "Asymmetric",
    "key_group": "Key Selection",
    "key_select": "Select Key:",
    "key_create": "Create New Key",
    "file_group": "File Selection",
    "file_select": "Select File",
    "folder_select": "Select Folder",
    "output_group": "Output Options",
    "output_dir": "Output Directory:",
    "output_select": "Select Directory",
    "delete_original": "Delete original files after processing",
    "verify_encryption": "Verify encryption result",
    "btn_encrypt": "Start Encryption",
    "btn_decrypt": "Start Decryption",
    
    # Key Management Tab
    "keys_title": "Key Management",
    "keys_desc": "Manage your encryption keys",
    "keys_filter": "Filter:",
    "keys_create": "Create Key",
    "keys_import": "Import Key",
    "keys_export": "Export Key",
    "keys_delete": "Delete Key",
    "keys_name": "Key Name",
    "keys_type": "Key Type",
    "keys_algo": "Algorithm",
    "keys_protected": "Protected",
    "key_type_symmetric": "Symmetric",
    "key_type_asymmetric": "Asymmetric",
    
    # File Monitor Tab
    "monitor_title": "File Monitor",
    "monitor_desc": "Monitor file changes in directories and automatically encrypt or decrypt new files",
    "monitor_tasks": "Monitor Tasks",
    "monitor_add": "Add Monitor",
    "monitor_edit": "Edit",
    "monitor_delete": "Delete",
    "monitor_refresh": "Refresh",
    "monitor_id": "Task ID",
    "monitor_dir": "Directory",
    "monitor_auto": "Auto Process",
    "monitor_status": "Status",
    "monitor_details": "Task Details",
    "monitor_select": "Select a monitoring task to view details",

    # Settings Tab
    "settings_title": "Application Settings",
    "settings_desc": "Customize application behavior and appearance",
    "settings_general": "General Settings",
    "settings_language": "Interface Language:",
    "settings_theme": "Interface Theme:",
    "settings_dark_mode": "Dark Mode",
    "settings_auto_start": "Start on system boot",
    "settings_adv": "Advanced Settings",
    "settings_buffer": "Buffer Size:",
    "settings_threads": "Max Threads:",
    "settings_save": "Save Settings",
    "settings_reset": "Reset to Default",
    "settings_encryption": "Encryption Settings",
    "settings_default_algorithm": "Default Algorithm:",
    "settings_saved": "Settings saved successfully",
    "settings_reset_confirm": "Are you sure you want to reset all settings to their default values?",
    "settings_reset_success": "Settings have been reset to defaults",
    "preview": "Preview",
    
    # Dialogs
    "dialog_error": "Error",
    "dialog_warning": "Warning",
    "dialog_info": "Information",
    "dialog_confirm": "Confirm",
    "dialog_cancel": "Cancel",
    "dialog_ok": "OK",
    "dialog_yes": "Yes",
    "dialog_no": "No",
    "yes": "Yes",
    "no": "No",
    
    # Password Dialog
    "password_title": "Password Entry",
    "password_prompt": "Enter password:",
    "password_confirm": "Confirm password:",
    "password_show": "Show password",
    "password_hint": "Password hint: Use a combination of letters, numbers and special characters for better security",
    
    # Key Generation Dialog
    "keygen_title": "Generate New Key",
    "keygen_desc": "Please enter key information to create a new key.\nThe key name should help you identify its purpose.",
    "keygen_name": "Key Name:",
    "keygen_random": "Random",
    "keygen_sym_info": "Symmetric encryption uses the same key for encryption and decryption, suitable for large files",
    "keygen_asym_info": "Asymmetric encryption uses public key for encryption and private key for decryption, ideal for secure key exchange",
    "keygen_length_info": "Note: Longer keys are more secure but slower for encryption/decryption",
    "keygen_security": "Security Options",
    "keygen_password": "Protect key with password",
    "keygen_password_info": "Password protection prevents unauthorized access to your key",
    "keygen_generate": "Generate Key",

    # Monitor Config Dialog
    "monitor_config_title": "File Monitoring Configuration",
    "monitor_config_dir": "Monitor Directory",
    "monitor_config_dir_select": "Select Directory",
    "monitor_config_settings": "Monitor Settings",
    "monitor_config_recursive": "Monitor subdirectories recursively",
    "monitor_config_auto": "Automatically process new files",
    "monitor_config_filter": "File Filtering",
    "monitor_config_filter_note": "File patterns support wildcards, separate multiple patterns with semicolons (;)",
    "monitor_config_include": "Include patterns:",
    "monitor_config_exclude": "Exclude patterns:",
    "monitor_config_include_placeholder": "Example: *.txt;*.doc;*.pdf",
    "monitor_config_exclude_placeholder": "Example: *.tmp;~*;.git*",
    "monitor_config_process": "Auto-Process Settings",
    "monitor_config_type": "Process type:",
    "monitor_config_key": "Use key:",
    "monitor_config_output": "Output directory:",
    "monitor_config_output_select": "Select",
    "monitor_config_delete": "Delete original files after processing",

    # Progress Dialog
    "progress_title": "Processing Progress",
    "progress_encrypt": "Encryption Progress",
    "progress_decrypt": "Decryption Progress",
    "progress_message": "Please wait...",
    "progress_init": "Initializing...",
    "progress_cancel": "Cancel Operation",
    "progress_cancel_confirm": "Are you sure you want to cancel the current operation?",
    "progress_cancelling": "Cancelling operation...",

    # Success/Error Messages
    "encrypt_success": "File encryption completed!",
    "decrypt_success": "File decryption completed!",
    "key_gen_success": "Key generation successful!",
    "key_import_success": "Key '{0}' imported successfully!",
    "key_export_success": "Key '{0}' exported to {1} successfully!",
    "key_delete_success": "Key '{0}' has been deleted!",
    "encrypt_error": "Encryption Error",
    "decrypt_error": "Decryption Error",
    "key_error": "Key Error",
    "key_not_found": "Could not find key named {0}.",
    "no_keys": "No encryption keys available. Please generate or import a key first.",
    "password_empty": "Password cannot be empty",
    "password_mismatch": "Passwords do not match",
    
    # Themes
    "theme_light": "Light",
    "theme_dark": "Dark",
    "theme_system": "System",
    "theme_blue": "Blue",
    "theme_green": "Green",
    "theme_purple": "Purple",
    
    # Languages
    "lang_zh_CN": "Chinese (Simplified)",
    "lang_en_US": "English (US)",
} 