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

    def test_validate_sql_dangerous_confirm(self):
        """测试危险操作返回确认标记"""
        # DROP DATABASE 需要确认
        ok, msg = validate_sql("DROP DATABASE test")
        self.assertTrue(ok)  # 返回True但带确认标记
        self.assertTrue(msg.startswith("CONFIRM:"))
        
        # TRUNCATE 需要确认
        ok, msg = validate_sql("TRUNCATE TABLE users")
        self.assertTrue(ok)
        self.assertIn("CONFIRM:", msg)
        
        # DROP TABLE 需要确认
        ok, msg = validate_sql("DROP TABLE users")
        self.assertTrue(ok)
        self.assertIn("CONFIRM:", msg)

    def test_is_dangerous_sql(self):
        """测试危险SQL检测"""
        from app.validators import is_dangerous_sql
        
        # 普通消息
        is_danger, op, desc = is_dangerous_sql("")
        self.assertFalse(is_danger)
        
        # 确认消息
        is_danger, op, desc = is_dangerous_sql("CONFIRM:DROP DATABASE|删除整个数据库")
        self.assertTrue(is_danger)
        self.assertEqual(op, "DROP DATABASE")
        self.assertEqual(desc, "删除整个数据库")

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
