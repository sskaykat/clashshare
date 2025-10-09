# YAML 模板功能 - 安装说明

## 📅 2025-10-08

---

## ⚠️ 重要提示

由于添加了新的Template表和字段，需要重置数据库。

---

## 🔧 安装步骤

### 方法1：自动重置（推荐）

1. **停止正在运行的服务**（如果有）
   - 按 `Ctrl+C` 停止

2. **删除旧数据库**
   ```bash
   # Windows
   del instance\clash_manager.db
   rd /s /q __pycache__
   
   # Linux/Mac
   rm -f instance/clash_manager.db
   rm -rf __pycache__
   ```

3. **重新启动服务**
   ```bash
   python app.py
   ```

系统会自动：
- 创建新数据库结构
- 创建默认管理员（admin/admin123）
- 创建默认配置模板

---

## 🗃️ 新增数据库结构

### Template 表
```sql
CREATE TABLE templates (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    content TEXT NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Subscription 表新增字段
```sql
ALTER TABLE subscriptions ADD COLUMN template_id INTEGER REFERENCES templates(id);
```

### User 表新增字段
```sql
ALTER TABLE users ADD COLUMN template_id INTEGER REFERENCES templates(id);
```

---

## ✅ 验证安装

### 1. 检查数据库表
启动服务后，应该看到：
```
✅ 默认管理员已创建
   用户名: admin
   密码: admin123
   ⚠️  请登录后立即修改密码！
✅ 默认配置模板已创建
```

### 2. 登录后台
访问 http://127.0.0.1:5000
- 用户名：admin
- 密码：admin123

### 3. 检查功能
- 侧边栏应该显示 **"📝 模板管理"**
- 概览页面应该显示4个统计卡片（包含"配置模板"）
- 点击模板管理，应该看到"默认模板"

---

## 🎯 下一步

1. **修改默认密码**
   - 系统设置 → 修改密码

2. **创建第一个订阅分组**
   - 订阅管理 → 创建分组

3. **添加节点**
   - 节点管理 → 添加节点/批量导入

4. **（可选）自定义模板**
   - 模板管理 → 创建模板

---

## ❓ 常见问题

### Q: 启动时提示数据库错误
A: 确保已完全删除旧数据库和 `__pycache__` 目录

### Q: 模板管理页面不显示
A: 清空浏览器缓存或强制刷新（Ctrl+F5）

### Q: 默认模板没有创建
A: 检查终端输出，如果没有看到"✅ 默认配置模板已创建"，手动在模板管理中创建

---

## 📚 使用文档

详见 `功能-YAML模板管理.md`

---

**安装完成后即可开始使用模板功能！** 🎉

