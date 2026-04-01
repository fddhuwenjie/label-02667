# SQL 数据库管理器 PyQt6 架构分析与改进建议

## 问题 1：数据库连接管理分析

### 当前实现方式

当前系统使用**单个数据库连接**的方式，而非连接池或每次操作新建连接。

**关键代码位置**：
- `frontend-admin/app/database.py:10-13` - `DatabaseService` 类持有单个连接对象 `self.conn`
- `frontend-admin/app/database.py:14-33` - `connect()` 方法创建单个连接
- `frontend-admin/app/database.py:46-55` - `ensure_connection()` 方法通过 `ping()` 保持连接活跃

### 高频操作场景的性能问题

在高频操作场景下，当前实现会面临以下性能问题：

1. **连接阻塞**：所有操作串行执行，无法并发处理多个查询
2. **无连接复用机制**：虽然保持单个连接，但每次操作仍需等待前一个操作完成
3. **连接断开风险**：长时间保持单个连接，可能因网络波动或服务器超时导致断开
4. **无备用连接**：一旦连接断开，需要重新建立连接，影响用户体验

---

## 问题 2：SQL 查询结果表格渲染分析

### 使用的 Qt 模型

当前系统使用的是 **`QTableWidget`**，而不是基于 `QAbstractTableModel` 的自定义模型。

**关键代码位置**：
- `frontend-admin/app/main.py:208` - 表结构展示使用 `QTableWidget`
- `frontend-admin/app/main.py:238` - 查询结果展示使用 `QTableWidget`
- `frontend-admin/app/main.py:370-377` - 数据填充方式：遍历所有行和列，逐个创建 `QTableWidgetItem`

### 10 万行数据时的界面卡顿问题

当查询返回 10 万行数据时，当前实现**必然会导致界面卡顿**，原因如下：

1. **一次性加载全部数据**：`cursor.fetchall()` 会将所有数据一次性加载到内存中（`database.py:109`）
2. **逐个创建 Item 对象**：需要创建 10 万 × 列数 个 `QTableWidgetItem` 对象，消耗大量内存和 CPU
3. **无虚拟滚动/分页机制**：`QTableWidget` 不支持数据虚拟化，所有数据都必须在内存中准备好
4. **主线程阻塞**：所有数据加载和渲染都在主线程中执行，会导致界面完全冻结

---

## 问题 3：支持多 MySQL 实例连接的架构改动

### 需要修改的核心类和方法

#### 1. 新建 `ConnectionManager` 类
**文件**：`frontend-admin/app/database.py`
- 管理多个 `DatabaseService` 实例
- 维护连接 ID 到连接实例的映射
- 提供连接的创建、删除、切换功能

#### 2. 重构 `DatabaseService` 类
**文件**：`frontend-admin/app/database.py`
- 添加 `connection_id` 属性标识每个连接
- 添加 `connection_name` 属性用于显示
- 保持现有数据库操作方法不变

#### 3. 新建 `ConnectionTabWidget` 类
**文件**：`frontend-admin/app/main.py`
- 继承 `QTabWidget`
- 每个 Tab 页包含独立的 `ManagerWidget` 实例
- 处理 Tab 页的添加、关闭、切换

#### 4. 重构 `MainWindow` 类
**文件**：`frontend-admin/app/main.py:429-448`
- 移除 `show_login()` 和 `on_connect()` 的单连接逻辑
- 添加「新建连接」按钮和对话框
- 管理多个连接 Tab 页

#### 5. 重构/新建连接对话框
**文件**：新建 `frontend-admin/app/dialogs.py` 中的 `ConnectionDialog` 类
- 支持连接名称输入
- 支持保存多个连接配置
- 从配置中加载历史连接

#### 6. 修改 `config.py`
**文件**：`frontend-admin/app/config.py`
- 支持存储多个连接配置（列表形式）
- 每个连接配置包含：名称、主机、端口、用户名、密码

#### 7. 重构 `ManagerWidget` 类
**文件**：`frontend-admin/app/main.py:117-426`
- 不再直接从 `MainWindow` 接收 `db_service`
- 每个实例拥有自己的 `db_service`
- 移除与主窗口耦合的断开连接逻辑

---

## 总结

| 问题 | 现状 | 改进方向 |
|------|------|----------|
| 连接管理 | 单连接 | 连接池或多连接管理 |
| 表格渲染 | QTableWidget | QAbstractTableModel + 分页/虚拟滚动 |
| 多连接支持 | 不支持 | Tab 页架构 + 连接管理器 |

这些改进将显著提升系统在数据量较大和多连接场景下的性能和用户体验。
