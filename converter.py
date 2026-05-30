#!/usr/bin/env python3
"""
Clash Meta 订阅转换器
支持 SS/SSR/VMess/VLESS/Hysteria2 等协议
"""

import argparse
import sys
import requests
from typing import List
from parsers import ProxyParser
from generator import ClashConfigGenerator


for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, 'reconfigure'):
        stream.reconfigure(errors='replace')


def fetch_subscription(url: str) -> str:
    """
    从 URL 获取订阅内容
    
    Args:
        url: 订阅链接
    
    Returns:
        订阅内容
    """
    try:
        print(f"📡 正在获取订阅: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"❌ 获取订阅失败: {e}")
        sys.exit(1)


def read_subscription_file(file_path: str) -> str:
    """
    从本地文件读取订阅内容
    
    Args:
        file_path: 文件路径
    
    Returns:
        订阅内容
    """
    try:
        print(f"📄 正在读取文件: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Clash Meta 订阅转换器 - 支持多种代理协议',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 从订阅链接转换
  python converter.py --url "https://your-subscription-url" --output config.yaml
  
  # 从本地文件转换
  python converter.py --file subscription.txt --output config.yaml
  
  # 添加单个节点
  python converter.py --url "https://sub-url" --nodes "vmess://xxx" --output config.yaml
  
  # 只转换单节点（不使用订阅）
  python converter.py --nodes "ss://xxx" "vmess://yyy" --output config.yaml

支持的协议: SS, SSR, VMess, VLESS (Reality), Hysteria2, Trojan, HTTP/HTTPS, SOCKS
        """
    )
    
    # 输入源选项
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        '--url',
        help='订阅链接 URL'
    )
    input_group.add_argument(
        '--file',
        help='本地订阅文件路径'
    )
    
    # 其他选项
    parser.add_argument(
        '--nodes',
        nargs='+',
        help='单个节点分享链接（可以多个）'
    )
    parser.add_argument(
        '--output',
        default='clash_config.yaml',
        help='输出的 YAML 配置文件路径（默认: clash_config.yaml）'
    )
    parser.add_argument(
        '--proxy-group',
        default='🚀 节点选择',
        help='代理组名称（默认: 🚀 节点选择）'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='测试模式：显示解析的节点但不生成配置文件'
    )
    
    args = parser.parse_args()
    
    # 检查至少有一个输入源
    if not args.url and not args.file and not args.nodes:
        parser.print_help()
        print("\n❌ 错误: 请至少指定一个输入源 (--url, --file 或 --nodes)")
        sys.exit(1)
    
    # 收集所有节点
    all_proxies = []
    
    # 从订阅获取节点
    if args.url or args.file:
        if args.url:
            subscription_content = fetch_subscription(args.url)
        else:
            subscription_content = read_subscription_file(args.file)
        
        print("🔍 正在解析订阅内容...")
        proxies = ProxyParser.parse_subscription(subscription_content)
        
        if proxies:
            print(f"✅ 成功解析 {len(proxies)} 个节点")
            all_proxies.extend(proxies)
        else:
            print("⚠️  未能从订阅中解析到任何节点")
    
    # 添加单独的节点
    if args.nodes:
        print(f"🔍 正在解析 {len(args.nodes)} 个单独节点...")
        for node_url in args.nodes:
            proxy = ProxyParser.parse_proxy(node_url)
            if proxy:
                all_proxies.append(proxy)
                print(f"  ✅ {proxy['name']} ({proxy['type']})")
            else:
                print(f"  ❌ 解析失败: {node_url[:50]}...")
    
    # 检查是否有节点
    if not all_proxies:
        print("\n❌ 错误: 没有成功解析任何节点")
        sys.exit(1)
    
    print(f"\n📊 总计: {len(all_proxies)} 个代理节点")
    
    # 测试模式：只显示节点信息
    if args.test:
        print("\n" + "="*60)
        print("测试模式 - 解析的节点列表:")
        print("="*60)
        for i, proxy in enumerate(all_proxies, 1):
            print(f"\n节点 {i}:")
            print(f"  名称: {proxy['name']}")
            print(f"  类型: {proxy['type']}")
            print(f"  服务器: {proxy['server']}")
            print(f"  端口: {proxy['port']}")
        print("\n" + "="*60)
        return
    
    # 生成 Clash 配置
    print("\n🔧 正在生成 Clash Meta 配置...")
    generator = ClashConfigGenerator()
    
    try:
        config = generator.generate(all_proxies, args.proxy_group)
        
        # 验证配置
        if not generator.validate_config(config):
            print("❌ 配置验证失败")
            sys.exit(1)
        
        # 保存到文件
        generator.save_to_yaml(config, args.output)
        
        print("\n" + "="*60)
        print("✨ 转换完成!")
        print("="*60)
        print(f"📁 配置文件: {args.output}")
        print(f"🌐 代理节点: {len(all_proxies)} 个")
        print(f"📋 代理组: {len(config['proxy-groups'])} 个")
        print(f"📜 规则数量: {len(config['rules'])} 条")
        print("\n💡 使用提示:")
        print(f"  1. 将 {args.output} 导入到 Clash Meta 客户端")
        print("  2. 启动 Clash Meta 并开启系统代理")
        print("  3. 访问 http://clash.razord.top 进行节点测速和切换")
        print("\n🎯 分流策略:")
        print("  • 国内网站和 IP → 直连")
        print("  • 国外网站 → 代理")
        print("  • 流媒体 → 独立策略组")
        print("  • 广告域名 → 拦截")
        print("="*60)
        
    except Exception as e:
        print(f"❌ 生成配置失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

