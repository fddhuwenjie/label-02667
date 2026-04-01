# SQL 数据库管理器 PyQt6 架构深度分析报告

## 1. 数据库连接管理实现分析

### 当前实现方式

**代码位置**: `frontend-admin/app/database.py:7-143`

当前采用的是 **单连接长连接复用模式**，具体实现：

```python
class DatabaseService:
    def __init__(self):
        self.conn: Optional[pymysql.Connection] = None
        self.current_db: Optional[str] = None
```

**核心特征**：
- **不是连接池**：只维护单个 `pymysql.Connection` 对象
- **不是每次操作新建连接**：登录时建立一次连接，之后所有操作复用该连接
- **保活机制**：每次操作前调用 `ensure_connection()`，通过 `conn.ping(reconnect=True)` 检测连接状态，断开时自动重连

### 高频操作场景下的性能问题

在高频操作（如每秒数十次查询、批量导入导出）场景下，当前实现存在以下问题：

| 问题类型 | 具体表现 | 根本原因 |
|---------|----------|----------|
| **线程安全问题** | 并发操作时数据错乱、连接异常 | `pymysql.Connection` 不是线程安全的，PyQt6 信号槽可能跨线程调用 |
| **阻塞串行执行** | 界面假死、操作排队 | 所有数据库操作在主线程串行执行，没有异步/线程池隔离 |
| **重连风暴** | 网络波动后批量超时 | `ping(reconnect=True)` 在网络异常时会触发同步重连，阻塞后续所有操作 |
| **资源泄漏风险** | MySQL 服务端连接耗尽 | 异常退出时连接未正常关闭，依赖 MySQL 超时回收 |

---

## 2. SQL 查询结果表格渲染性能分析

### 使用的 Qt 模型

**代码位置**: `frontend-admin/app/main.py:238-243, 369-377`

当前使用的是 **`QTableWidget`**，这是 Qt 的便捷表格组件，**不使用标准 Model/View 架构**。

渲染流程：
```python
rows, count = self.db.execute_query(sql, self.current_db)
if rows:
    cols = list(rows[0].keys())
    self.result_table.setColumnCount(len(cols))
    self.result_table.setHorizontalHeaderLabels(cols)
    self.result_table.setRowCount(len(rows))
    for i, row in enumerate(rows):
        for j, c in enumerate(cols):
            self.result_table.setItem(i, j, QTableWidgetItem(str(row[c] or "")))
```

### 10 万行数据时的性能问题

**结论：一定会导致严重的界面卡顿，甚至程序崩溃**

**卡顿原因分析**：

#### 1. **内存一次性加载**
```python
# database.py:109
rows = cursor.fetchall()  # 10 万行 Dict 全部加载到 Python 内存
```
- 内存占用：10 万行 × 平均 10 列 ≈ 100 万个 Python 对象
- 预估内存：50MB ~ 200MB（取决于数据内容）

#### 2. **主线程阻塞渲染**
```python
for i, row in enumerate(rows):          # 10 万次外层循环
    for j, c in enumerate(cols):        # N 次内层循环
        self.result_table.setItem(...)  # 创建 QTableWidgetItem
```
- 循环次数：10 万 × 10 = **100 万次**
- 每个 `setItem` 触发重新计算布局、绘制
- **主线程完全阻塞 5-30 秒，界面无响应**

#### 3. **QTableWidget 固有局限**
- ❌ 无虚拟滚动（Virtual Scrolling）
- ❌ 无分页加载机制
- ❌ 所有单元格 Item 必须预先创建，不管是否可见
- ❌ 不支持懒加载数据

---

## 3. 多 MySQL 实例 Tab 切换架构改造方案

### 核心架构改动总览

| 改动层级 | 改动内容 | 影响范围 |
|---------|----------|----------|
| 数据层 | DatabaseService → ConnectionManager + ConnectionPool | database.py |
| UI层 | 单 ManagerWidget → TabWidget + 每个 Tab 独立实例 | main.py |
| 配置层 | 单连接配置 → 多连接配置管理 | config.py |
| 会话层 | 全局单 db_service → Tab 隔离各自的 db_service | main.py |

### 需要修改的核心类和方法

---

#### 🔴 **第一类：新增核心类**

##### 1. `DatabaseConnection` 类 - 封装单个数据库连接
**文件**: `database.py`
```python
class DatabaseConnection:
    """单个数据库连接实例，每个 Tab 对应一个实例"""
    def __init__(self, conn_id: str, config: dict):
        self.conn_id = conn_id
        self.config = config  # {host, port, user, password, label}
        self.conn = None
        self.current_db = None
        # 原有 DatabaseService 的所有方法迁移至此
        def connect(): ...
        def disconnect(): ...
        def execute_query(): ...
```

##### 2. `ConnectionManager` 单例类 - 管理所有连接
**文件**: `database.py`
```python
class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, DatabaseConnection] = {}
        self.active_conn_id: Optional[str] = None
    
    def add_connection(self, config: dict) -> str:
        """新建连接，返回 conn_id"""
    def remove_connection(self, conn_id: str):
    def get_connection(self, conn_id: str) -> DatabaseConnection:
    def switch_active(self, conn_id: str):
```

---

#### 🟡 **第二类：修改现有核心类**

##### 3. `MainWindow` 类 - `main.py:429-448`
**需要修改的方法**：

| 方法名 | 改动内容 |
|--------|----------|
| `__init__` | 初始化 ConnectionManager、TabWidget |
| `show_login` | 改为弹出对话框，不再是 centralWidget |
| `on_connect` | 创建新 Tab 而非替换 centralWidget |
| **新增方法** | `create_new_connection_tab()` |
| **新增方法** | `close_connection_tab(conn_id)` |

**关键改动示例**：
```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.conn_manager = ConnectionManager()
        self.tab_widget = QTabWidget()  # 作为 centralWidget
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self._add_welcome_tab()  # 欢迎页，带"新建连接"按钮
```

##### 4. `LoginWidget` 类 - `main.py:26-114`
**需要修改的方法**：

| 方法名 | 改动内容 |
|--------|----------|
| `init_ui` | 增加"连接名称"输入框、保存连接配置复选框 |
| 新增 | `load_saved_connections()` 下拉选择已保存连接 |
| `connect` | 创建 DatabaseConnection 实例，添加到 ConnectionManager |

##### 5. `ManagerWidget` 类 - `main.py:117-426`
**需要修改的方法**：

| 方法名 | 改动内容 |
|--------|----------|
| `__init__` | 参数改为 `conn_id`，通过 ConnectionManager 获取对应 db_connection |
| **所有方法** | 将 `self.db.xxx()` 改为 `self.db_connection.xxx()` |
| `disconnect` | 改为关闭当前 Tab，通知 MainWindow |

---

#### 🟢 **第三类：新增/修改的配置存储**

##### 6. `config.py` 配置格式升级
```yaml
# 原有格式（单连接）
host: localhost
port: 3306
user: root

# 新格式（多连接）
connections:
  - id: conn_001
    label: 生产环境-主库
    host: 192.168.1.100
    port: 3306
    user: root
    password: ****
  - id: conn_002
    label: 测试环境
    host: localhost
    port: 3306
    user: root
last_active: conn_001
```

---

### 改造后的架构图

```
┌─────────────────────────────────────────────────────────┐
│                    MainWindow                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │  + [+]   [生产-主库] x  [测试环境] x               │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │                                                   │  │
│  │    ManagerWidget (Tab 1)     ManagerWidget (Tab 2)│  │
│  │  ┌─────────────────┐       ┌─────────────────┐    │  │
│  │  │ db_connection   │       │ db_connection   │    │  │
│  │  │ (conn_001)      │       │ (conn_002)      │    │  │
│  │  └─────────────────┘       └─────────────────┘    │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                              ↓
            ┌──────────────────────────────────┐
            │      ConnectionManager           │
            │  {conn_001, conn_002, ...}       │
            └──────────────────────────────────┘
```

### 关键注意事项

1. **Tab 切换的数据隔离**：每个 Tab 的 `current_db`、`current_table`、SQL 输入框内容必须各自独立
2. **连接状态同步**：某个 Tab 连接断开时，只影响该 Tab，不影响其他连接
3. **资源释放**：关闭 Tab 时必须调用对应 `disconnect()` 释放数据库连接
4. **配置迁移**：兼容旧版单连接配置，自动迁移到多连接格式
