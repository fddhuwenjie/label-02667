"""数据库服务层测试"""
import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import DatabaseService


class TestDatabaseService(unittest.TestCase):
    """数据库服务测试"""

    def setUp(self):
        self.db = DatabaseService()

    def test_initial_state(self):
        """测试初始状态"""
        self.assertIsNone(self.db.conn)
        self.assertIsNone(self.db.current_db)

    @patch('app.database.pymysql.connect')
    def test_connect_success(self, mock_connect):
        """测试连接成功"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        result = self.db.connect("localhost", 3306, "root", "password")
        
        self.assertTrue(result)
        self.assertEqual(self.db.conn, mock_conn)
        mock_connect.assert_called_once()

    @patch('app.database.pymysql.connect')
    def test_connect_failure(self, mock_connect):
        """测试连接失败"""
        mock_connect.side_effect = Exception("Connection refused")
        
        with self.assertRaises(Exception):
            self.db.connect("localhost", 3306, "root", "wrong")

    def test_disconnect(self):
        """测试断开连接"""
        self.db.conn = MagicMock()
        self.db.current_db = "testdb"
        
        self.db.disconnect()
        
        self.assertIsNone(self.db.conn)
        self.assertIsNone(self.db.current_db)

    def test_ensure_connection_no_conn(self):
        """测试无连接时检查"""
        self.assertFalse(self.db.ensure_connection())

    def test_ensure_connection_with_conn(self):
        """测试有连接时检查"""
        self.db.conn = MagicMock()
        self.db.conn.ping = MagicMock()
        
        self.assertTrue(self.db.ensure_connection())
        self.db.conn.ping.assert_called_once_with(reconnect=True)

    def test_get_databases(self):
        """测试获取数据库列表"""
        self.db.conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"Database": "testdb"},
            {"Database": "mysql"}
        ]
        self.db.conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        result = self.db.get_databases()
        
        self.assertEqual(result, ["testdb", "mysql"])

    def test_get_databases_no_connection(self):
        """测试无连接时获取数据库列表"""
        with self.assertRaises(ConnectionError):
            self.db.get_databases()

    def test_get_tables(self):
        """测试获取表列表"""
        self.db.conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"Tables_in_testdb": "users"},
            {"Tables_in_testdb": "products"}
        ]
        self.db.conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        result = self.db.get_tables("testdb")
        
        self.assertEqual(result, ["users", "products"])

    def test_get_table_structure(self):
        """测试获取表结构"""
        self.db.conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"Field": "id", "Type": "int", "Null": "NO", "Key": "PRI", "Default": None}
        ]
        self.db.conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        result = self.db.get_table_structure("testdb", "users")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Field"], "id")

    def test_execute_query_select(self):
        """测试执行SELECT查询"""
        self.db.conn = MagicMock()
        self.db.current_db = "testdb"
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"id": 1, "name": "test"}]
        self.db.conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        rows, count = self.db.execute_query("SELECT * FROM users")
        
        self.assertEqual(len(rows), 1)
        self.assertEqual(count, 1)

    def test_execute_query_insert(self):
        """测试执行INSERT"""
        self.db.conn = MagicMock()
        self.db.current_db = "testdb"
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        self.db.conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        rows, count = self.db.execute_query("INSERT INTO users VALUES (1, 'test')")
        
        self.assertEqual(rows, [])
        self.assertEqual(count, 1)
        self.db.conn.commit.assert_called_once()

    def test_import_data(self):
        """测试导入数据"""
        self.db.conn = MagicMock()
        mock_cursor = MagicMock()
        self.db.conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        data = [{"name": "test1"}, {"name": "test2"}]
        count = self.db.import_data("testdb", "users", data)
        
        self.assertEqual(count, 2)
        self.db.conn.commit.assert_called_once()

    def test_import_data_empty(self):
        """测试导入空数据"""
        self.db.conn = MagicMock()
        count = self.db.import_data("testdb", "users", [])
        self.assertEqual(count, 0)

    def test_export_data(self):
        """测试导出数据"""
        self.db.conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"id": 1}, {"id": 2}]
        self.db.conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        result = self.db.export_data("testdb", "users")
        
        self.assertEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main()
