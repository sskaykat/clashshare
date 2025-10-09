#!/usr/bin/env python3
"""
重置数据库脚本
警告：这会删除所有数据！
"""

import os
import shutil
from datetime import datetime

def reset_database():
    """重置数据库"""
    db_file = 'clash_manager.db'
    
    if not os.path.exists(db_file):
        print("✅ 数据库不存在，无需重置")
        print("   运行 python app.py 会自动创建新数据库")
        return
    
    # 备份原数据库
    backup_file = f'clash_manager.db.backup.{datetime.now().strftime("%Y%m%d%H%M%S")}'
    print(f"📦 备份原数据库到: {backup_file}")
    shutil.copy2(db_file, backup_file)
    
    # 删除数据库
    os.remove(db_file)
    print(f"🗑️  已删除数据库文件: {db_file}")
    
    print("\n✅ 数据库已重置！")
    print(f"   原数据库已备份到: {backup_file}")
    print("\n💡 下一步：")
    print("   1. 运行: python app.py")
    print("   2. 会自动创建新的数据库结构")
    print("   3. 使用默认账号登录: admin / admin123")
    
    print("\n⚠️  注意：")
    print("   - 所有订阅、节点、用户数据已清空")
    print("   - 需要重新添加订阅和创建用户")
    print(f"   - 如需恢复，可从备份文件恢复: {backup_file}")

if __name__ == '__main__':
    print("="*60)
    print("⚠️  数据库重置工具")
    print("="*60)
    print("\n警告：这将删除所有数据（订阅、节点、用户）！")
    print("数据库会自动备份，但建议手动备份重要数据。")
    print("\n确定要继续吗？")
    print("输入 'yes' 确认，其他任意键取消: ")
    
    confirm = input().strip().lower()
    
    if confirm == 'yes':
        reset_database()
    else:
        print("\n❌ 操作已取消")

