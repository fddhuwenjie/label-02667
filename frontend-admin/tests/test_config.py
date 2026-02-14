"""配置管理测试"""
import unittest
import sys
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import config


class TestConfig(unittest.TestCase):

    def test_default_config(self):
        """测试默认配置"""
        self.assertIn("host", config.DEFAULT_CONFIG)
        self.assertIn("port", config.DEFAULT_CONFIG)
        self.assertIn("user", config.DEFAULT_CONFIG)

    def test_load_config_no_file(self):
        """测试无配置文件时加载默认配置"""
        with patch.object(config, 'CONFIG_FILE', Path("/nonexistent/path.json")):
            cfg = config.load_config()
            self.assertEqual(cfg["host"], "localhost")
            self.assertEqual(cfg["port"], 3306)

    def test_save_and_load_config(self):
        """测试保存和加载配置"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)

        try:
            with patch.object(config, 'CONFIG_FILE', temp_path):
                test_config = {"host": "testhost", "port": 3307, "user": "testuser"}
                config.save_config(test_config)

                loaded = config.load_config()
                self.assertEqual(loaded["host"], "testhost")
                self.assertEqual(loaded["port"], 3307)
        finally:
            temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
