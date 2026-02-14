"""输入验证模块"""
import re


def validate_host(host: str) -> tuple[bool, str]:
    """验证主机地址"""
    if not host or not host.strip():
        return False, "主机地址不能为空"
    host = host.strip()
    # 简单验证：允许IP、域名、localhost
    if not re.match(r'^[\w\.\-]+$', host):
        return False, "主机地址格式无效"
    return True, ""


def validate_port(port: str) -> tuple[bool, str]:
    """验证端口"""
    if not port or not port.strip():
        return False, "端口不能为空"
    try:
        p = int(port)
        if p < 1 or p > 65535:
            return False, "端口范围: 1-65535"
        return True, ""
    except ValueError:
        return False, "端口必须是数字"


def validate_user(user: str) -> tuple[bool, str]:
    """验证用户名"""
    if not user or not user.strip():
        return False, "用户名不能为空"
    return True, ""


def validate_sql(sql: str) -> tuple[bool, str]:
    """验证SQL语句，危险操作返回警告信息供二次确认"""
    if not sql or not sql.strip():
        return False, "SQL语句不能为空"
    sql_upper = sql.strip().upper()
    # 危险操作列表 - 返回警告而非直接拦截
    dangerous_ops = {
        "DROP DATABASE": "删除整个数据库",
        "DROP SCHEMA": "删除整个数据库",
        "TRUNCATE": "清空表数据",
        "DROP TABLE": "删除表",
        "DELETE FROM": "删除数据（无WHERE条件时会删除所有数据）"
    }
    for op, desc in dangerous_ops.items():
        if op in sql_upper:
            # 返回特殊标记，让调用方决定是否二次确认
            return True, f"CONFIRM:{op}|{desc}"
    return True, ""


def is_dangerous_sql(msg: str) -> tuple[bool, str, str]:
    """检查是否是需要确认的危险SQL"""
    if msg.startswith("CONFIRM:"):
        parts = msg[8:].split("|")
        return True, parts[0], parts[1] if len(parts) > 1 else ""
    return False, "", ""


def validate_json(json_str: str) -> tuple[bool, str]:
    """验证JSON格式"""
    if not json_str or not json_str.strip():
        return False, "JSON数据不能为空"
    import json
    try:
        data = json.loads(json_str)
        if not isinstance(data, list):
            return False, "JSON必须是数组格式"
        if not data:
            return False, "JSON数组不能为空"
        if not all(isinstance(item, dict) for item in data):
            return False, "数组元素必须是对象"
        return True, ""
    except json.JSONDecodeError as e:
        return False, f"JSON格式错误: {e}"
