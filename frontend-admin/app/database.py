"""数据库服务层 - 封装所有数据库操作"""
import pymysql
from typing import Optional, List, Dict, Any
from app.logger import log_info, log_error


class DatabaseService:
    """数据库服务类，封装所有数据库操作"""
    
    def __init__(self):
        self.conn: Optional[pymysql.Connection] = None
        self.current_db: Optional[str] = None
    
    def connect(self, host: str, port: int, user: str, password: str) -> bool:
        """连接数据库"""
        try:
            log_info(f"连接: {host}:{port}")
            self.conn = pymysql.connect(
                host=host.strip(),
                port=port,
                user=user.strip(),
                password=password,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=10,
                read_timeout=30,
                write_timeout=30
            )
            log_info("连接成功")
            return True
        except Exception as e:
            log_error(f"连接失败: {e}")
            raise
    
    def disconnect(self):
        """断开连接"""
        if self.conn:
            try:
                self.conn.close()
                log_info("已断开连接")
            except Exception:
                pass
            self.conn = None
            self.current_db = None
    
    def ensure_connection(self) -> bool:
        """确保连接有效"""
        if not self.conn:
            return False
        try:
            self.conn.ping(reconnect=True)
            return True
        except Exception as e:
            log_error(f"连接检查失败: {e}")
            return False
    
    def select_database(self, db_name: str):
        """选择数据库"""
        if self.ensure_connection():
            self.conn.select_db(db_name)
            self.current_db = db_name
    
    def get_databases(self) -> List[str]:
        """获取所有数据库列表"""
        if not self.ensure_connection():
            raise ConnectionError("数据库连接已断开")
        with self.conn.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            return [row["Database"] for row in cursor.fetchall()]
    
    def get_tables(self, db_name: str) -> List[str]:
        """获取指定数据库的表列表"""
        if not self.ensure_connection():
            raise ConnectionError("数据库连接已断开")
        self.select_database(db_name)
        with self.conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            return [list(row.values())[0] for row in cursor.fetchall()]
    
    def get_table_structure(self, db_name: str, table_name: str) -> List[Dict[str, Any]]:
        """获取表结构"""
        if not self.ensure_connection():
            raise ConnectionError("数据库连接已断开")
        self.select_database(db_name)
        with self.conn.cursor() as cursor:
            cursor.execute(f"DESCRIBE `{table_name}`")
            return cursor.fetchall()
    
    def execute_query(self, sql: str, db_name: Optional[str] = None) -> tuple[List[Dict], int]:
        """
        执行SQL查询
        返回: (结果列表, 影响行数)
        """
        if not self.ensure_connection():
            raise ConnectionError("数据库连接已断开")
        
        if db_name:
            self.select_database(db_name)
        elif self.current_db:
            self.select_database(self.current_db)
        
        log_info(f"执行SQL: {sql[:80]}")
        
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            sql_upper = sql.strip().upper()
            
            if sql_upper.startswith(("SELECT", "SHOW", "DESC")):
                rows = cursor.fetchall()
                return rows, len(rows)
            else:
                self.conn.commit()
                return [], cursor.rowcount
    
    def import_data(self, db_name: str, table_name: str, data: List[Dict]) -> int:
        """导入数据到指定表"""
        if not self.ensure_connection():
            raise ConnectionError("数据库连接已断开")
        if not data:
            return 0
        
        self.select_database(db_name)
        cols = list(data[0].keys())
        placeholders = ','.join(['%s'] * len(cols))
        col_names = ','.join(f'`{c}`' for c in cols)
        sql = f"INSERT INTO `{table_name}` ({col_names}) VALUES ({placeholders})"
        
        count = 0
        with self.conn.cursor() as cursor:
            for row in data:
                cursor.execute(sql, [row.get(c) for c in cols])
                count += 1
        self.conn.commit()
        return count
    
    def export_data(self, db_name: str, table_name: str) -> List[Dict]:
        """导出表数据"""
        if not self.ensure_connection():
            raise ConnectionError("数据库连接已断开")
        self.select_database(db_name)
        with self.conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `{table_name}`")
            return cursor.fetchall()
