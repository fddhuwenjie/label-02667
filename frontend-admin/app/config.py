"""配置管理模块 - 使用加密存储敏感信息"""
import os
import json
import base64
from pathlib import Path
from cryptography.fernet import Fernet

CONFIG_FILE = Path.home() / ".sql_manager_config.json"
KEY_FILE = Path.home() / ".sql_manager_key"

DEFAULT_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "last_database": ""
}


def _get_or_create_key() -> bytes:
    """获取或创建加密密钥"""
    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()
    # 生成新的Fernet密钥
    key = Fernet.generate_key()
    KEY_FILE.write_bytes(key)
    KEY_FILE.chmod(0o600)
    return key


def _get_cipher() -> Fernet:
    """获取加密器"""
    key = _get_or_create_key()
    return Fernet(key)


def _encrypt(text: str) -> str:
    """加密文本"""
    if not text:
        return ""
    return _get_cipher().encrypt(text.encode()).decode()


def _decrypt(text: str) -> str:
    """解密文本"""
    if not text:
        return ""
    try:
        return _get_cipher().decrypt(text.encode()).decode()
    except Exception:
        return ""


def load_config() -> dict:
    """加载配置"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                # 解密密码
                if "password" in config and config["password"]:
                    config["password"] = _decrypt(config["password"])
                return {**DEFAULT_CONFIG, **config}
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    """保存配置（密码加密存储）"""
    try:
        save_data = config.copy()
        # 加密密码
        if "password" in save_data and save_data["password"]:
            save_data["password"] = _encrypt(save_data["password"])
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        CONFIG_FILE.chmod(0o600)
    except Exception:
        pass
