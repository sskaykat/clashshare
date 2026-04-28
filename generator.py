"""
Clash Meta 配置生成器
生成包含代理节点和分流规则的完整 Clash 配置
"""

import yaml
from typing import List, Dict, Any

try:
    from yaml import CDumper as YamlDumper
except ImportError:
    from yaml import Dumper as YamlDumper


class ClashConfigGenerator:
    """Clash Meta 配置生成器"""
    
    def __init__(self):
        self.config = {}
    
    def generate(self, proxies: List[Dict[str, Any]], 
                 proxy_group_name: str = "🚀 节点选择",
                 template_content: str = None) -> Dict[str, Any]:
        """
        生成完整的 Clash Meta 配置
        
        Args:
            proxies: 代理节点列表
            proxy_group_name: 代理组名称
            template_content: YAML模板内容（可选，如果提供则使用模板）
        
        Returns:
            完整的配置字典
        """
        if not proxies:
            raise ValueError("代理节点列表不能为空")
        
        prepared_proxies = self._prepare_proxies(proxies)
        output_proxies = prepared_proxies['output']
        selectable_proxies = prepared_proxies['selectable']

        if not selectable_proxies:
            raise ValueError("可展示的代理节点列表不能为空")
        
        # 如果提供了模板，使用模板生成配置
        if template_content:
            return self.generate_from_template(
                output_proxies,
                template_content,
                selectable_proxies
            )
        
        # 否则使用默认配置
        config = {
            'mixed-port': 7890,
            'allow-lan': False,
            'mode': 'rule',
            'log-level': 'info',
            'external-controller': '127.0.0.1:9090',
            'dns': self._generate_dns_config(),
            'proxies': output_proxies,
            'proxy-groups': self._generate_proxy_groups(selectable_proxies, proxy_group_name),
            'rules': self._generate_rules(proxy_group_name),
        }
        
        return config
    
    def _prepare_proxies(self, proxies: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        拆分最终输出节点和代理组可展示节点。

        链式节点可能依赖额外的前置/后置节点。依赖节点需要写入
        proxies 以便客户端解析，但不应该进入 proxy-groups，避免
        在客户端选择列表中单独显示。
        """
        output_proxies = []
        selectable_proxies = []
        seen_names = set()

        for proxy in proxies:
            if not isinstance(proxy, dict):
                continue

            is_hidden = proxy.get('__hidden') is True
            cleaned_proxy = self._strip_internal_fields(proxy)
            proxy_name = cleaned_proxy.get('name')

            if not proxy_name or proxy_name in seen_names:
                continue

            seen_names.add(proxy_name)
            output_proxies.append(cleaned_proxy)

            if not is_hidden:
                selectable_proxies.append(cleaned_proxy)

        return {
            'output': output_proxies,
            'selectable': selectable_proxies,
        }

    def _strip_internal_fields(self, proxy: Dict[str, Any]) -> Dict[str, Any]:
        """移除仅供服务端使用的内部字段，避免写入 Clash 配置。"""
        return {
            key: value
            for key, value in proxy.items()
            if not str(key).startswith('__')
        }

    def generate_from_template(self, proxies: List[Dict[str, Any]], 
                               template_content: str,
                               selectable_proxies: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        根据模板生成配置
        
        Args:
            proxies: 代理节点列表
            template_content: YAML模板内容
            selectable_proxies: 代理组中可展示的节点列表
        
        Returns:
            完整的配置字典
        """
        try:
            # 解析模板
            template = yaml.safe_load(template_content)
            
            # 替换 proxies 部分
            template['proxies'] = proxies
            
            # 更新 proxy-groups 中的节点列表
            if 'proxy-groups' in template:
                group_proxies = selectable_proxies if selectable_proxies is not None else proxies
                proxy_names = [p['name'] for p in group_proxies]
                template['proxy-groups'] = self._update_proxy_groups(
                    template['proxy-groups'], 
                    proxy_names
                )
            
            return template
            
        except yaml.YAMLError as e:
            raise ValueError(f"模板解析失败: {str(e)}")
    
    def _update_proxy_groups(self, groups: List[Dict[str, Any]], 
                            proxy_names: List[str]) -> List[Dict[str, Any]]:
        """
        更新代理组中的节点列表
        
        Args:
            groups: 原始代理组列表
            proxy_names: 节点名称列表
        
        Returns:
            更新后的代理组列表
        """
        updated_groups = []
        
        for group in groups:
            updated_group = group.copy()
            
            # 如果代理组的 proxies 列表包含 PROXY_NODES 占位符，替换为实际节点
            if 'proxies' in updated_group:
                new_proxies = []
                for proxy in updated_group['proxies']:
                    if proxy == 'PROXY_NODES':
                        # 替换为所有节点
                        new_proxies.extend(proxy_names)
                    else:
                        new_proxies.append(proxy)
                updated_group['proxies'] = new_proxies
            
            updated_groups.append(updated_group)
        
        return updated_groups
    
    def _generate_dns_config(self) -> Dict[str, Any]:
        """生成 DNS 配置"""
        return {
            'enable': True,
            'ipv6': False,
            'enhanced-mode': 'fake-ip',
            'fake-ip-range': '198.18.0.1/16',
            'fake-ip-filter': [
                '*.lan',
                '*.localdomain',
                '*.example',
                '*.invalid',
                '*.localhost',
                '*.test',
                '*.local',
                'time.*.com',
                'time.*.gov',
                'time.*.edu.cn',
                'time.*.apple.com',
                'time1.*.com',
                'time2.*.com',
                'time3.*.com',
                'time4.*.com',
                'time5.*.com',
                'time6.*.com',
                'time7.*.com',
                'ntp.*.com',
                'ntp1.*.com',
                'ntp2.*.com',
                'ntp3.*.com',
                'ntp4.*.com',
                'ntp5.*.com',
                'ntp6.*.com',
                'ntp7.*.com',
                '*.time.edu.cn',
                '*.ntp.org.cn',
                '+.pool.ntp.org',
                'time1.cloud.tencent.com',
            ],
            'default-nameserver': [
                '223.5.5.5',
                '119.29.29.29',
            ],
            'nameserver': [
                'https://doh.pub/dns-query',
                'https://dns.alidns.com/dns-query',
            ],
            'fallback': [
                'https://1.1.1.1/dns-query',
                'https://dns.google/dns-query',
            ],
            'fallback-filter': {
                'geoip': True,
                'geoip-code': 'CN',
                'ipcidr': [
                    '240.0.0.0/4',
                ],
            },
        }
    
    def _generate_proxy_groups(self, proxies: List[Dict[str, Any]], 
                               proxy_group_name: str) -> List[Dict[str, Any]]:
        """生成代理组配置"""
        proxy_names = [p['name'] for p in proxies]
        
        groups = [
            {
                'name': proxy_group_name,
                'type': 'select',
                'proxies': ['♻️ 自动选择', '🎯 全球直连'] + proxy_names,
            },
            {
                'name': '♻️ 自动选择',
                'type': 'url-test',
                'proxies': proxy_names,
                'url': 'http://www.gstatic.com/generate_204',
                'interval': 300,
            },
            {
                'name': '📺 流媒体',
                'type': 'select',
                'proxies': [proxy_group_name, '♻️ 自动选择'] + proxy_names,
            },
            {
                'name': '🎯 全球直连',
                'type': 'select',
                'proxies': ['DIRECT'],
            },
            {
                'name': '🛑 广告拦截',
                'type': 'select',
                'proxies': ['REJECT', 'DIRECT'],
            },
            {
                'name': '🐟 漏网之鱼',
                'type': 'select',
                'proxies': [proxy_group_name, '🎯 全球直连', '♻️ 自动选择'],
            },
        ]
        
        return groups
    
    def _generate_rules(self, proxy_group_name: str) -> List[str]:
        """生成分流规则"""
        rules = [
            # 广告拦截
            'DOMAIN-KEYWORD,adservice,🛑 广告拦截',
            'DOMAIN-KEYWORD,analytics,🛑 广告拦截',
            'DOMAIN-SUFFIX,doubleclick.net,🛑 广告拦截',
            'DOMAIN-SUFFIX,googleadservices.com,🛑 广告拦截',
            
            # 流媒体规则
            'DOMAIN-KEYWORD,youtube,📺 流媒体',
            'DOMAIN-KEYWORD,netflix,📺 流媒体',
            'DOMAIN-KEYWORD,spotify,📺 流媒体',
            'DOMAIN-SUFFIX,youtube.com,📺 流媒体',
            'DOMAIN-SUFFIX,googlevideo.com,📺 流媒体',
            'DOMAIN-SUFFIX,netflix.com,📺 流媒体',
            'DOMAIN-SUFFIX,nflxvideo.net,📺 流媒体',
            'DOMAIN-SUFFIX,spotify.com,📺 流媒体',
            'DOMAIN-SUFFIX,hulu.com,📺 流媒体',
            'DOMAIN-SUFFIX,disneyplus.com,📺 流媒体',
            'DOMAIN-SUFFIX,hbo.com,📺 流媒体',
            'DOMAIN-SUFFIX,primevideo.com,📺 流媒体',
            
            # 国内直连
            'DOMAIN-SUFFIX,cn,🎯 全球直连',
            'DOMAIN-KEYWORD,baidu,🎯 全球直连',
            'DOMAIN-KEYWORD,taobao,🎯 全球直连',
            'DOMAIN-KEYWORD,alipay,🎯 全球直连',
            'DOMAIN-KEYWORD,wechat,🎯 全球直连',
            'DOMAIN-KEYWORD,qq,🎯 全球直连',
            'DOMAIN-SUFFIX,qq.com,🎯 全球直连',
            'DOMAIN-SUFFIX,taobao.com,🎯 全球直连',
            'DOMAIN-SUFFIX,jd.com,🎯 全球直连',
            'DOMAIN-SUFFIX,tmall.com,🎯 全球直连',
            'DOMAIN-SUFFIX,alipay.com,🎯 全球直连',
            'DOMAIN-SUFFIX,aliyun.com,🎯 全球直连',
            'DOMAIN-SUFFIX,163.com,🎯 全球直连',
            'DOMAIN-SUFFIX,126.com,🎯 全球直连',
            'DOMAIN-SUFFIX,bilibili.com,🎯 全球直连',
            'DOMAIN-SUFFIX,hdslb.com,🎯 全球直连',
            'DOMAIN-SUFFIX,iqiyi.com,🎯 全球直连',
            'DOMAIN-SUFFIX,youku.com,🎯 全球直连',
            
            # 常见国外网站走代理
            'DOMAIN-KEYWORD,google,{}'.format(proxy_group_name),
            'DOMAIN-KEYWORD,facebook,{}'.format(proxy_group_name),
            'DOMAIN-KEYWORD,twitter,{}'.format(proxy_group_name),
            'DOMAIN-KEYWORD,instagram,{}'.format(proxy_group_name),
            'DOMAIN-KEYWORD,github,{}'.format(proxy_group_name),
            'DOMAIN-SUFFIX,google.com,{}'.format(proxy_group_name),
            'DOMAIN-SUFFIX,googleapis.com,{}'.format(proxy_group_name),
            'DOMAIN-SUFFIX,gstatic.com,{}'.format(proxy_group_name),
            'DOMAIN-SUFFIX,googleusercontent.com,{}'.format(proxy_group_name),
            'DOMAIN-SUFFIX,facebook.com,{}'.format(proxy_group_name),
            'DOMAIN-SUFFIX,twitter.com,{}'.format(proxy_group_name),
            'DOMAIN-SUFFIX,instagram.com,{}'.format(proxy_group_name),
            'DOMAIN-SUFFIX,github.com,{}'.format(proxy_group_name),
            'DOMAIN-SUFFIX,githubusercontent.com,{}'.format(proxy_group_name),
            'DOMAIN-SUFFIX,telegram.org,{}'.format(proxy_group_name),
            'DOMAIN-SUFFIX,t.me,{}'.format(proxy_group_name),
            
            # GeoIP 规则
            'GEOIP,CN,🎯 全球直连',
            
            # 最终规则
            'MATCH,🐟 漏网之鱼',
        ]
        
        return rules
    
    def save_to_yaml(self, config: Dict[str, Any], output_path: str):
        """
        保存配置到 YAML 文件
        
        Args:
            config: 配置字典
            output_path: 输出文件路径
        """
        # 自定义 YAML 表示器，使输出更易读
        def str_representer(dumper, data):
            if '\n' in data:
                return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
            return dumper.represent_scalar('tag:yaml.org,2002:str', data)
        
        yaml.add_representer(str, str_representer)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f,
                     Dumper=YamlDumper,
                     default_flow_style=False,
                     allow_unicode=True,
                     sort_keys=False,
                     width=float("inf"))
        
        print(f"✅ 配置文件已保存到: {output_path}")
        print(f"📊 共生成 {len(config['proxies'])} 个代理节点")
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """
        验证配置是否有效
        
        Args:
            config: 配置字典
        
        Returns:
            是否有效
        """
        required_keys = ['proxies', 'proxy-groups', 'rules']
        
        for key in required_keys:
            if key not in config:
                print(f"❌ 配置缺少必要字段: {key}")
                return False
        
        if not config['proxies']:
            print("❌ 代理节点列表为空")
            return False
        
        if not config['proxy-groups']:
            print("❌ 代理组列表为空")
            return False
        
        if not config['rules']:
            print("❌ 规则列表为空")
            return False
        
        return True
