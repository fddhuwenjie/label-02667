"""配置管理测试"""
import unittest
import sys
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import config


class TestConfig(unittest.TestCase):

    def test_default_config(self):
        """测试默认配置"""
        self.assertIn("host", config.DEFAULT_CONFIG)
        self.assertIn("port", config.DEFAULT_CONFIG)
        self.assertIn("user", config.DEFAULT_CONFIG)
        self.assertIn("password", config.DEFAULT_CONFIG)

    def test_load_config_no_file(self):
        """测试无配置文件时加载默认配置"""
        with patch.object(config, 'CONFIG_FILE', Path("/nonexistent/path.json")):
            cfg = config.load_config()
            self.assertEqual(cfg["host"], "localhost")
            self.assertEqual(cfg["port"], 3306)

    def test_encrypt_decrypt(self):
        """测试加密解密"""
        with tempfile.NamedTemporaryFile(suffix='.key', delete=False) as f:
            temp_key = Path(f.name)
        # 删除临时文件让测试重新创建密钥
        temp_key.unlink(missing_ok=True)
        
        try:
            with patch.object(config, 'KEY_FILE', temp_key):
                # 测试加密
                encrypted = config._encrypt("test_password")
                self.assertNotEqual(encrypted, "test_password")
                self.assertTrue(len(encrypted) > 0)
                
                # 测试解密
                decrypted = config._decrypt(encrypted)
                self.assertEqual(decrypted, "test_password")
        finally:
            temp_key.unlink(missing_ok=True)

    def test_encrypt_empty(self):
        """测试空字符串加密"""
        result = config._encrypt("")
        self.assertEqual(result, "")

    def test_decrypt_empty(self):
        """测试空字符串解密"""
        result = config._decrypt("")
        self.assertEqual(result, "")

    def test_save_and_load_config_with_password(self):
        """测试保存和加载带密码的配置"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_config = Path(f.name)
        with tempfile.NamedTemporaryFile(suffix='.key', delete=False) as f:
            temp_key = Path(f.name)
        # 删除临时文件让测试重新创建
        temp_config.unlink(missing_ok=True)
        temp_key.unlink(missing_ok=True)

        try:
            with patch.object(config, 'CONFIG_FILE', temp_config), \
                 patch.object(config, 'KEY_FILE', temp_key):
                test_config = {
                    "host": "testhost",
                    "port": 3307,
                    "user": "testuser",
                    "password": "secret123"
                }
                config.save_config(test_config)

                # 验证密码已加密存储
                with open(temp_config, 'r') as f:
                    saved = json.load(f)
                    self.assertNotEqual(saved["password"], "secret123")

                # 验证加载后密码已解密
                loaded = config.load_config()
                self.assertEqual(loaded["host"], "testhost")
                self.assertEqual(loaded["port"], 3307)
                self.assertEqual(loaded["password"], "secret123")
        finally:
            temp_config.unlink(missing_ok=True)
            temp_key.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
