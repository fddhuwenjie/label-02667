"""验证器测试"""
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.validators import (
    validate_host, validate_port, validate_user,
    validate_sql, validate_json
)


class TestValidators(unittest.TestCase):

    def test_validate_host_valid(self):
        self.assertTrue(validate_host("localhost")[0])
        self.assertTrue(validate_host("127.0.0.1")[0])
        self.assertTrue(validate_host("mysql")[0])
        self.assertTrue(validate_host("db.example.com")[0])

    def test_validate_host_invalid(self):
        self.assertFalse(validate_host("")[0])
        self.assertFalse(validate_host("   ")[0])
        self.assertFalse(validate_host("host;drop")[0])

    def test_validate_port_valid(self):
        self.assertTrue(validate_port("3306")[0])
        self.assertTrue(validate_port("1")[0])
        self.assertTrue(validate_port("65535")[0])

    def test_validate_port_invalid(self):
        self.assertFalse(validate_port("")[0])
        self.assertFalse(validate_port("abc")[0])
        self.assertFalse(validate_port("0")[0])
        self.assertFalse(validate_port("65536")[0])
        self.assertFalse(validate_port("-1")[0])

    def test_validate_user_valid(self):
        self.assertTrue(validate_user("root")[0])
        self.assertTrue(validate_user("admin")[0])

    def test_validate_user_invalid(self):
        self.assertFalse(validate_user("")[0])
        self.assertFalse(validate_user("   ")[0])

    def test_validate_sql_valid(self):
        self.assertTrue(validate_sql("SELECT * FROM users")[0])
        self.assertTrue(validate_sql("INSERT INTO t VALUES (1)")[0])

    def test_validate_sql_invalid(self):
        self.assertFalse(validate_sql("")[0])
        # 危险操作警告
        ok, msg = validate_sql("DROP DATABASE test")
        self.assertFalse(ok)
        self.assertIn("危险", msg)

    def test_validate_json_valid(self):
        self.assertTrue(validate_json('[{"a": 1}]')[0])
        self.assertTrue(validate_json('[{"name": "test"}, {"name": "test2"}]')[0])

    def test_validate_json_invalid(self):
        self.assertFalse(validate_json("")[0])
        self.assertFalse(validate_json("not json")[0])
        self.assertFalse(validate_json('{"a": 1}')[0])  # 不是数组
        self.assertFalse(validate_json('[]')[0])  # 空数组
        self.assertFalse(validate_json('[1, 2, 3]')[0])  # 元素不是对象


if __name__ == "__main__":
    unittest.main()
