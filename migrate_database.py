#!/usr/bin/env python3
"""
数据库迁移脚本
用于将旧数据库结构迁移到新结构（移除用户密码功能）
"""

import sqlite3
import os
import shutil
from datetime import datetime

def migrate_database():
    """迁移数据库"""
    db_file = 'clash_manager.db'
    
    # 检查数据库是否存在
    if not os.path.exists(db_file):
        print("✅ 数据库文件不存在，无需迁移")
        print("   首次运行时会自动创建新数据库")
        return
    
    # 备份原数据库
    backup_file = f'clash_manager.db.backup.{datetime.now().strftime("%Y%m%d%H%M%S")}'
    print(f"📦 备份原数据库到: {backup_file}")
    shutil.copy2(db_file, backup_file)
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 检查是否需要迁移
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'password_hash' not in columns:
            print("✅ 数据库已经是最新结构，无需迁移")
            conn.close()
            return
        
        print("🔄 开始迁移数据库...")
        
        # 1. 创建新的 users 表
        print("  创建新表结构...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users_new (
                id INTEGER PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                subscription_token VARCHAR(64) UNIQUE NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                remark VARCHAR(255),
                created_at DATETIME
            )
        ''')
        
        # 2. 复制数据（不包含 password_hash）
        print("  复制用户数据...")
        cursor.execute('''
            INSERT INTO users_new (id, username, subscription_token, enabled, created_at)
            SELECT id, username, subscription_token, enabled, created_at
            FROM users
        ''')
        
        # 3. 删除旧表
        print("  删除旧表...")
        cursor.execute('DROP TABLE users')
        
        # 4. 重命名新表
        print("  重命名新表...")
        cursor.execute('ALTER TABLE users_new RENAME TO users')
        
        # 5. 重新创建关联表（如果需要）
        print("  重建关联表...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_nodes_new (
                user_id INTEGER NOT NULL,
                node_id INTEGER NOT NULL,
                PRIMARY KEY (user_id, node_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (node_id) REFERENCES nodes(id)
            )
        ''')
        
        # 复制关联数据
        cursor.execute('''
            INSERT OR IGNORE INTO user_nodes_new (user_id, node_id)
            SELECT user_id, node_id FROM user_nodes
        ''')
        
        cursor.execute('DROP TABLE user_nodes')
        cursor.execute('ALTER TABLE user_nodes_new RENAME TO user_nodes')
        
        conn.commit()
        conn.close()
        
        print("\n✅ 数据库迁移完成！")
        print(f"   原数据库已备份到: {backup_file}")
        print("   用户表已更新：")
        print("   - 移除了 password_hash 字段")
        print("   - 添加了 remark 字段")
        print("\n💡 提示：")
        print("   - 用户现在是分组/标签功能，无需密码")
        print("   - 可以直接使用订阅令牌访问")
        print("   - 如有问题，可以从备份恢复")
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        print(f"   可以从备份恢复: {backup_file}")
        conn.rollback()
        conn.close()
        raise

if __name__ == '__main__':
    print("="*60)
    print("🔧 Clash Meta 订阅管理系统 - 数据库迁移工具")
    print("="*60)
    print("\n本工具将数据库从旧版本迁移到新版本")
    print("主要变更：用户管理改为分组功能，移除密码")
    print("\n按 Enter 继续，Ctrl+C 取消...")
    
    try:
        input()
        migrate_database()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("请检查错误信息并重试")

