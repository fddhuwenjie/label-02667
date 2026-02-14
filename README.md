# SQL数据库管理器

Python桌面GUI应用，用于连接和管理MySQL数据库。

## How to Run

```bash
# 一键启动
./start.sh
```

或手动执行：

```bash
# 1. 启动MySQL数据库
docker-compose up -d

# 2. 安装Python依赖
cd frontend-admin
pip3 install -r requirements.txt

# 3. 运行GUI应用
python3 -m app.main
```

## Services

| 服务 | 端口 | 说明 |
|------|------|------|
| mysql | 3306 | MySQL数据库 |
| frontend-admin | 本地GUI | Python桌面应用 |

## 测试账号

| 项目 | 值 |
|------|------|
| MySQL主机 | localhost |
| 端口 | 3306 |
| 用户名 | root |
| 密码 | root123 |
| 测试数据库 | testdb |

> ⚠️ **重要提示**：测试时请选择 `testdb` 数据库，不要选择 `mysql`、`sys` 等系统数据库！

### 测试数据

`testdb` 数据库包含以下表：

| 表名 | 说明 | 数据量 |
|------|------|--------|
| users | 用户表 | 3条 |
| products | 商品表 | 5条 |

### 示例查询语句

> 执行查询前，请先在左侧点击展开 `testdb` 数据库

```sql
-- 1. 查询所有用户
SELECT * FROM users;

-- 2. 查询所有商品
SELECT * FROM products;

-- 3. 查询库存大于50的商品
SELECT * FROM products WHERE stock > 50;

-- 4. 按价格降序查询商品
SELECT name, price FROM products ORDER BY price DESC;

-- 5. 统计商品总数和平均价格
SELECT COUNT(*) AS total, AVG(price) AS avg_price FROM products;
```

### 导入数据示例

> 导入前请先选择 `testdb` 数据库下的 `users` 表

在"导入"标签页中粘贴以下JSON格式数据：

```json
[
  {"username": "user1", "email": "user1@test.com"},
  {"username": "user2", "email": "user2@test.com"}
]
```

### 导出数据

选择表后点击"导出CSV"按钮，选择保存路径即可导出。

## 题目内容
利用python编写一个可视化窗口，目的是链接sql数据库，包含数据库登录界面，查看数据库内框架和表，导入数据，查询数据以及导出数据功能

利用Python编写一个可视化窗口，目的是连接SQL数据库，包含：
- 数据库登录界面
- 查看数据库内框架和表
- 导入数据
- 查询数据
- 导出数据功能

## 技术栈

- GUI框架：PyQt6
- 数据库驱动：PyMySQL
- 数据库：MySQL 8.0
- 容器化：Docker (仅数据库)

## 项目特性

- 日志记录：操作日志保存在 `~/.sql_manager_logs/`
- 配置管理：连接信息自动保存在 `~/.sql_manager_config.json`
- 输入验证：主机、端口、SQL语句、JSON数据格式验证
- 危险操作警告：DROP DATABASE 等操作会提示确认

## 运行测试

```bash
cd frontend-admin
python3 -m unittest discover tests/ -v
```
