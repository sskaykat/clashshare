#!/usr/bin/env python3
"""
数据库迁移脚本：将用户-订阅关系从一对多迁移到多对多
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'instance/clash_manager.db'


def migrate():
    """执行数据库迁移"""
    if not os.path.exists(DB_PATH):
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        print("请先运行应用创建数据库")
        return False
    
    print("="*60)
    print("开始迁移数据库：用户-订阅关系 (一对多 -> 多对多)")
    print("="*60)
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查是否已经迁移过
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='user_subscription'
        """)
        if cursor.fetchone():
            print("✅ 数据库已经是多对多关系，无需迁移")
            return True
        
        # 1. 创建新的关联表
        print("\n1. 创建 user_subscription 关联表...")
        cursor.execute("""
            CREATE TABLE user_subscription (
                user_id INTEGER NOT NULL,
                subscription_id INTEGER NOT NULL,
                created_at DATETIME,
                PRIMARY KEY (user_id, subscription_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
            )
        """)
        print("   ✅ 关联表创建成功")
        
        # 2. 迁移现有数据
        print("\n2. 迁移现有的用户-订阅关系...")
        cursor.execute("""
            SELECT id, user_id FROM subscriptions 
            WHERE user_id IS NOT NULL
        """)
        relations = cursor.fetchall()
        
        if relations:
            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            for sub_id, user_id in relations:
                cursor.execute("""
                    INSERT INTO user_subscription (user_id, subscription_id, created_at)
                    VALUES (?, ?, ?)
                """, (user_id, sub_id, current_time))
            print(f"   ✅ 已迁移 {len(relations)} 个关系记录")
        else:
            print("   ℹ️  没有需要迁移的关系记录")
        
        # 3. 创建临时表（不包含user_id列）
        print("\n3. 重建 subscriptions 表...")
        cursor.execute("""
            CREATE TABLE subscriptions_new (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                subscription_token VARCHAR(64) UNIQUE NOT NULL,
                template_id INTEGER,
                created_at DATETIME,
                FOREIGN KEY (template_id) REFERENCES templates(id)
            )
        """)
        
        # 4. 复制数据到新表
        cursor.execute("""
            INSERT INTO subscriptions_new (id, name, subscription_token, template_id, created_at)
            SELECT id, name, subscription_token, template_id, created_at
            FROM subscriptions
        """)
        print("   ✅ 数据已复制到新表")
        
        # 5. 删除旧表
        cursor.execute("DROP TABLE subscriptions")
        
        # 6. 重命名新表
        cursor.execute("ALTER TABLE subscriptions_new RENAME TO subscriptions")
        print("   ✅ subscriptions 表重建完成")
        
        # 提交事务
        conn.commit()
        
        print("\n" + "="*60)
        print("✅ 数据库迁移完成！")
        print("="*60)
        print("\n现在用户和订阅是多对多关系：")
        print("- 多个用户可以共用同一个订阅")
        print("- 一个用户也可以使用多个订阅")
        print("- 不会出现订阅被挤占的问题")
        print("\n可以安全地启动应用了！")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def backup_database():
    """备份数据库"""
    if not os.path.exists(DB_PATH):
        return
    
    backup_path = DB_PATH + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    import shutil
    shutil.copy2(DB_PATH, backup_path)
    print(f"✅ 数据库已备份至: {backup_path}")


if __name__ == '__main__':
    print("\n⚠️  重要提示：此脚本将修改数据库结构！")
    print("\n即将执行以下操作：")
    print("1. 创建 user_subscription 关联表（多对多）")
    print("2. 迁移现有的用户-订阅关系数据")
    print("3. 移除 subscriptions 表中的 user_id 列")
    print("\n是否继续？(y/n): ", end='')
    
    choice = input().lower()
    if choice == 'y':
        # 先备份
        print("\n正在备份数据库...")
        backup_database()
        
        # 执行迁移
        if migrate():
            print("\n✅ 所有操作完成！")
        else:
            print("\n❌ 迁移失败，请检查错误信息")
    else:
        print("\n取消迁移")

