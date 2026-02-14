# SQL数据库管理器

Python桌面GUI应用，用于连接和管理MySQL数据库。

## How to Run

### 环境要求

| 依赖 | 最低版本 | 推荐版本 | 说明 |
|------|----------|----------|------|
| Python | 3.9+ | 3.11 | 需要支持PyQt6 |
| pip | 21.0+ | 最新 | Python包管理器 |
| Docker | 20.10+ | 最新 | 容器运行环境 |
| Docker Compose | 2.0+ | 最新 | 容器编排工具 |

### 系统支持

| 操作系统 | 架构 | 状态 |
|----------|------|------|
| macOS | ARM64 (M1/M2) | ✅ 支持 |
| macOS | x86_64 | ✅ 支持 |
| Windows | x86_64 | ✅ 支持 |
| Linux | x86_64 | ✅ 支持 |
| Linux | ARM64 | ✅ 支持 |

### 快速启动

```bash
# 一键启动（推荐）
./start.sh
```

### 手动启动

```bash
# 1. 启动MySQL数据库
docker-compose up -d mysql

# 2. 等待MySQL就绪（约10-30秒）
docker exec $(docker ps -qf "name=mysql") mysqladmin ping -h localhost -u root -proot123

# 3. 安装Python依赖
cd frontend-admin
pip3 install -r requirements.txt

# 4. 运行GUI应用
python3 -m app.main
```

## Services

| 服务 | 端口 | 说明 |
|------|------|------|
| mysql | 3306 | MySQL 8.0 数据库 |
| frontend-admin | 本地GUI | PyQt6 桌面应用 |

## 测试账号

| 项目 | 值 |
|------|------|
| MySQL主机 | localhost |
| 端口 | 3306 |
| 用户名 | root |
| 密码 | root123 |
| 测试数据库 | testdb |

### 测试数据

`testdb` 数据库包含以下表：

| 表名 | 说明 | 数据量 |
|------|------|--------|
| users | 用户表 | 3条 |
| products | 商品表 | 3条 |

### 示例查询语句

```sql
-- 查询所有用户
SELECT * FROM users;

-- 查询所有商品
SELECT * FROM products;

-- 查询库存大于50的商品
SELECT * FROM products WHERE stock > 50;

-- 按价格降序查询商品
SELECT name, price FROM products ORDER BY price DESC;

-- 统计商品总数和平均价格
SELECT COUNT(*) AS total, AVG(price) AS avg_price FROM products;
```

### 导入数据示例

在"导入"标签页中粘贴以下JSON格式数据：

```json
[
  {"username": "user1", "email": "user1@test.com"},
  {"username": "user2", "email": "user2@test.com"}
]
```

## 题目内容

利用Python编写一个可视化窗口，目的是连接SQL数据库，包含：
- 数据库登录界面
- 查看数据库内框架和表
- 导入数据
- 查询数据
- 导出数据功能

## 技术栈

- GUI框架：PyQt6
- 数据库驱动：PyMySQL + cryptography（加密存储密码）
- 数据库：MySQL 8.0
- 容器化：Docker

## 项目结构

```
├── docker-compose.yml      # Docker编排配置
├── init.sql                # 数据库初始化脚本
├── start.sh                # 一键启动脚本
├── README.md               # 项目文档
└── frontend-admin/         # 前端管理应用
    ├── Dockerfile          # Docker构建文件
    ├── requirements.txt    # Python依赖
    ├── app/
    │   ├── main.py         # 主程序入口
    │   ├── database.py     # 数据库服务层
    │   ├── config.py       # 配置管理（加密存储）
    │   ├── validators.py   # 输入验证
    │   ├── dialogs.py      # 自定义弹窗
    │   ├── styles.py       # 界面样式
    │   └── logger.py       # 日志模块
    └── tests/              # 单元测试
        ├── test_config.py
        ├── test_validators.py
        └── test_database.py
```

## 安全特性

- 密码加密存储：使用 cryptography 库对数据库密码进行加密
- 配置文件权限：配置文件设置为仅用户可读（chmod 600）
- 危险操作确认：DROP/TRUNCATE 等操作需要二次确认

## 运行测试

```bash
cd frontend-admin
python3 -m unittest discover tests/ -v
```
