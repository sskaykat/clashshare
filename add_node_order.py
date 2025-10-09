#!/usr/bin/env python3
"""
数据库迁移脚本：为节点表添加排序字段
"""

import sqlite3
import os

DB_PATH = 'instance/clash_manager.db'


def add_order_field():
    """为nodes表添加order字段"""
    if not os.path.exists(DB_PATH):
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        print("请先运行应用创建数据库")
        return False
    
    print("="*60)
    print("开始迁移数据库：为节点表添加排序字段")
    print("="*60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查是否已经有order字段
        cursor.execute("PRAGMA table_info(nodes)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'order' in columns:
            print("✅ order字段已存在，无需迁移")
            return True
        
        print("\n1. 添加 order 字段到 nodes 表...")
        cursor.execute("ALTER TABLE nodes ADD COLUMN 'order' INTEGER DEFAULT 0")
        
        print("   ✅ order 字段添加成功")
        
        # 为现有节点设置默认排序（按ID顺序）
        print("\n2. 为现有节点设置默认排序...")
        cursor.execute("SELECT id FROM nodes ORDER BY id")
        node_ids = [row[0] for row in cursor.fetchall()]
        
        for index, node_id in enumerate(node_ids):
            cursor.execute("UPDATE nodes SET 'order' = ? WHERE id = ?", (index * 10, node_id))
        
        print(f"   ✅ 已为 {len(node_ids)} 个节点设置默认排序")
        
        conn.commit()
        
        print("\n" + "="*60)
        print("✅ 数据库迁移完成！")
        print("="*60)
        print("\n功能说明：")
        print("- 节点现在支持自定义排序")
        print("- 排序值越小，节点越靠前")
        print("- 默认按每个节点间隔10（0, 10, 20, ...）")
        print("- 订阅导出时会按照排序输出节点")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    print("\n⚠️  重要提示：此脚本将修改数据库结构！")
    print("\n即将执行以下操作：")
    print("1. 在 nodes 表中添加 order 字段")
    print("2. 为现有节点设置默认排序值")
    print("\n是否继续？(y/n): ", end='')
    
    choice = input().lower()
    if choice == 'y':
        if add_order_field():
            print("\n✅ 所有操作完成！")
            print("现在可以重启应用，在节点管理页面修改节点排序。")
        else:
            print("\n❌ 迁移失败，请检查错误信息")
    else:
        print("\n取消迁移")

