# SQL 数据库管理器 PyQt6 架构深度分析报告

---

## 一、数据库连接管理实现分析

### 1.1 当前实现方式

**代码位置：** `frontend-admin/app/database.py:7-143`

#### 连接管理机制
当前采用**单连接长连接模式**，既不是连接池，也不是每次操作新建连接：

```python
class DatabaseService:
    def __init__(self):
        self.conn: Optional[pymysql.Connection] = None
        self.current_db: Optional[str] = None
```

**核心特点：**
- 整个应用生命周期内只维护一个数据库连接
- 调用 `connect()` 方法时建立连接，连接保存在实例变量中
- 每次执行操作前通过 `ensure_connection()` 检查连接有效性
- 使用 `ping(reconnect=True)` 自动重连断开的连接

#### 关键方法分析

| 方法 | 职责 | 代码位置 |
|------|------|----------|
| `connect()` | 建立单一数据库连接 | `database.py:14-33` |
| `disconnect()` | 关闭当前连接 | `database.py:35-44` |
| `ensure_connection()` | 连接心跳检查与自动重连 | `database.py:46-55` |

---

### 1.2 高频操作场景下的性能问题

虽然不是每次操作新建连接，但单连接模式在高频场景下仍存在严重性能问题：

#### 问题1：串行执行瓶颈
- **问题本质**：所有数据库操作共享同一个连接，无法并行执行
- **影响**：即使在多线程环境下，pymysql 连接本身不是线程安全的，必须加锁保护，导致所有查询串行执行
- **表现**：QPS 超过 50 时响应时间呈指数级上升

#### 问题2：连接重建开销
- **问题本质**：连接断开时 `ping(reconnect=True)` 会阻塞重建
- **影响**：网络波动时会造成批量请求同时阻塞等待重连
- **表现**：出现周期性的界面卡顿

#### 问题3：缺少连接复用机制
- **问题本质**：没有连接池管理，无法利用连接复用优化
- **影响**：
  - 无法根据负载动态调整连接数
  - 无法实现故障转移
  - 无法设置连接空闲超时回收

---

## 二、SQL 查询结果表格渲染分析

### 2.1 当前使用的 Qt 模型

**代码位置：** `frontend-admin/app/main.py:238-243, 369-377`

#### 使用的渲染方式
当前使用 **`QTableWidget`** 作为表格组件，这是 Qt 的便利类（Convenience Class），内部采用隐式的 `QTableWidgetItem` 模型，**不是 MVC 架构的分离模型**。

```python
# 初始化
self.result_table = QTableWidget()

# 渲染逻辑
self.result_table.setRowCount(len(rows))
self.result_table.setColumnCount(len(cols))
for i, row in enumerate(rows):
    for j, c in enumerate(cols):
        self.result_table.setItem(i, j, QTableWidgetItem(str(row[c] or "")))
```

#### 与 Qt 标准模型的对比

| 方案 | 类 | 架构 | 适用场景 |
|------|----|------|----------|
| 当前方案 | `QTableWidget` | 视图与模型耦合 | 小数据量（<1000行） |
| 标准方案 | `QTableView` + `QAbstractTableModel` | MVC 分离 | 大数据量、虚拟滚动 |

---

### 2.2 10万行数据时的性能问题

**结论：一定会导致严重的界面卡顿，原因如下：**

#### 原因1：全量内存加载
- **问题**：`cursor.fetchall()` 一次性将 10 万行全部加载到 Python 内存
- **影响**：
  - 内存占用：每行平均 1KB 的话，10万行 ≈ 100MB+
  - GC 压力大，频繁触发垃圾回收
- **代码位置**：`database.py:109`

#### 原因2：同步阻塞渲染
- **问题**：在主线程中循环创建 10 万个 `QTableWidgetItem` 对象
- **影响**：
  - 每个 `setItem()` 都会触发重绘信号
  - 10万次循环，即使每次 0.01ms，总共需要 1 秒以上
  - 渲染期间整个界面完全无响应

#### 原因3：缺少虚拟滚动机制
- **问题**：即使视口只显示 50 行，也会创建全部 10 万行的 Qt 对象
- **影响**：
  - 内存膨胀：每个 `QTableWidgetItem` 约 64 字节，10万个 ≈ 6.4MB
  - 滚动时卡顿严重，平滑滚动失效

#### 原因4：没有批处理优化
- **问题**：渲染期间没有关闭更新信号
- **优化点**：应该添加：
  ```python
  self.result_table.setUpdatesEnabled(False)
  # 渲染逻辑...
  self.result_table.setUpdatesEnabled(True)
  ```

---

## 三、多实例连接架构改造方案

### 3.1 整体架构变更

#### 当前架构（单实例）
```
MainWindow
  └── ManagerWidget
        └── 单个 DatabaseService 实例
              └── 单个数据库连接
```

#### 目标架构（多实例 Tab）
```
MainWindow
  └── ConnectionTabWidget
        ├── Tab 1: ManagerWidget (实例A)
        │     └── DatabaseService (连接A)
        ├── Tab 2: ManagerWidget (实例B)
        │     └── DatabaseService (连接B)
        └── + 新建连接 Tab
```

---

### 3.2 需要修改的核心类和方法

#### 第一类：数据层改造

##### 1. `DatabaseService` 类增强
**文件：** `frontend-admin/app/database.py`

**新增属性：**
```python
class DatabaseService:
    # 新增
    instance_id: str
    connection_name: str
    host: str
    port: int
    user: str
```

**修改点：**
- 移除全局状态依赖，每个实例完全独立
- 添加连接元数据标识
- 支持连接状态事件回调

---

#### 第二类：UI 层改造

##### 2. 新增 `ConnectionManager` 类
**新建文件：** `frontend-admin/app/connection_manager.py`

**核心职责：**
- 管理所有活跃的 DatabaseService 实例
- 维护 Tab 页与连接实例的映射关系
- 处理连接生命周期事件

**核心方法：**
```python
class ConnectionManager:
    def add_connection(self, config: ConnectionConfig) -> str
    def remove_connection(self, instance_id: str)
    def get_active_connection(self) -> Optional[DatabaseService]
    def switch_connection(self, instance_id: str)
```

---

##### 3. `MainWindow` 类重构
**文件：** `frontend-admin/app/main.py:429-448`

**修改方法：**
- `__init__()`：初始化 `QTabWidget` 作为中央部件，而非单个 Widget
- `show_login()`：改为在新 Tab 中打开登录界面
- `on_connect()`：创建新的 ManagerWidget Tab，而非替换中央部件

**新增方法：**
```python
def create_new_connection_tab(self)
def close_connection_tab(self, index: int)
def on_tab_changed(self, index: int)
```

---

##### 4. `ManagerWidget` 类改造
**文件：** `frontend-admin/app/main.py:117-426`

**移除全局依赖：**
- 移除对主窗口状态的依赖
- 每个实例持有自己的 `current_db`、`current_table` 状态
- 每个实例持有独立的 `db_service` 引用

**新增属性：**
```python
class ManagerWidget(QWidget):
    instance_id: str
    connection_config: ConnectionConfig
```

---

##### 5. `LoginWidget` 类改造
**文件：** `frontend-admin/app/main.py:26-114`

**修改点：**
- 支持"新建连接"模式，不覆盖已有配置
- 支持保存多个连接配置到配置文件
- 支持从历史连接列表快速选择

---

#### 第三类：配置层改造

##### 6. 配置系统扩展
**文件：** `frontend-admin/app/config.py`

**配置结构升级：**
```python
# 旧结构
{
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": ""
}

# 新结构
{
    "connections": [
        {
            "id": "uuid-1",
            "name": "生产环境",
            "host": "192.168.1.100",
            "port": 3306,
            "user": "root",
            "password": "",
            "last_used": "2026-04-01T10:00:00"
        }
    ],
    "last_active": "uuid-1"
}
```

---

### 3.3 改造优先级建议

| 阶段 | 内容 | 预估工作量 |
|------|------|------------|
| P0 | 重构 ManagerWidget 去全局化 | 2人天 |
| P0 | 实现 Tab 页管理框架 | 1人天 |
| P1 | 多连接配置存储 | 0.5人天 |
| P1 | 连接管理器实现 | 0.5人天 |
| P2 | 历史连接快速选择 | 1人天 |
| P2 | Tab 页重命名、颜色标记 | 0.5人天 |

---

## 四、总结与建议

### 关键发现
1. **连接管理**：单连接模式简单但扩展性差，高频场景性能瓶颈明显
2. **表格渲染**：`QTableWidget` 只适合小数据量，10万行必然卡顿
3. **多实例支持**：当前架构耦合严重，需要解耦后才能支持多 Tab

### 优化建议
1. 引入 `DBUtils` 连接池替换单连接
2. 改用 `QTableView` + `QAbstractTableModel` 实现虚拟滚动
3. 所有数据库操作移到后台线程，避免阻塞 UI
