# 项目结构说明

本文档详细说明了 Clash Meta 订阅转换器的项目结构和各个文件的作用。

## 📁 项目目录结构

```
dychange/
├── README.md                    # 项目主说明文件
├── QUICKSTART.md               # 快速开始指南
├── PROTOCOL_EXAMPLES.md        # 协议格式说明与示例
├── PROJECT_STRUCTURE.md        # 项目结构说明（本文件）
│
├── requirements.txt            # Python 依赖包列表
├── .gitignore                  # Git 忽略文件配置
│
├── parsers.py                  # 协议解析器模块
├── generator.py                # Clash 配置生成器模块
├── converter.py                # 主程序（命令行入口）
│
├── test_converter.py           # 测试脚本
│
├── example_subscription.txt    # 订阅文件示例
└── example_config.yaml         # 输出配置示例
```

## 📄 核心文件说明

### 1. parsers.py - 协议解析器

**功能**: 解析各种代理协议的分享链接

**主要类和方法**:

```python
class ProxyParser:
    # 解析 Shadowsocks 链接
    @staticmethod
    def parse_ss(url: str) -> Optional[Dict[str, Any]]
    
    # 解析 ShadowsocksR 链接
    @staticmethod
    def parse_ssr(url: str) -> Optional[Dict[str, Any]]
    
    # 解析 VMess 链接
    @staticmethod
    def parse_vmess(url: str) -> Optional[Dict[str, Any]]
    
    # 解析 VLESS 链接（包括 Reality）
    @staticmethod
    def parse_vless(url: str) -> Optional[Dict[str, Any]]
    
    # 解析 Hysteria2 链接
    @staticmethod
    def parse_hysteria2(url: str) -> Optional[Dict[str, Any]]
    
    # 自动识别并解析代理链接
    @staticmethod
    def parse_proxy(url: str) -> Optional[Dict[str, Any]]
    
    # 解析订阅内容（多个节点）
    @staticmethod
    def parse_subscription(content: str) -> List[Dict[str, Any]]
```

**支持的协议**:
- ✅ Shadowsocks (SS)
- ✅ ShadowsocksR (SSR)
- ✅ VMess
- ✅ VLESS (包括 Reality)
- ✅ Hysteria2

**特点**:
- 自动识别协议类型
- 支持 Base64 编码的订阅内容
- 容错处理，解析失败不会中断整个流程

---

### 2. generator.py - 配置生成器

**功能**: 生成完整的 Clash Meta 配置文件

**主要类和方法**:

```python
class ClashConfigGenerator:
    # 生成完整配置
    def generate(self, proxies: List[Dict[str, Any]], 
                 proxy_group_name: str) -> Dict[str, Any]
    
    # 生成 DNS 配置
    def _generate_dns_config(self) -> Dict[str, Any]
    
    # 生成代理组配置
    def _generate_proxy_groups(self, proxies: List[Dict[str, Any]], 
                               proxy_group_name: str) -> List[Dict[str, Any]]
    
    # 生成分流规则
    def _generate_rules(self, proxy_group_name: str) -> List[str]
    
    # 保存配置到 YAML 文件
    def save_to_yaml(self, config: Dict[str, Any], output_path: str)
    
    # 验证配置有效性
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool
```

**生成的配置包含**:
- ✅ 混合代理端口配置
- ✅ 智能 DNS 配置（国内外分流）
- ✅ 代理节点列表
- ✅ 多个代理组（手动选择、自动选择、流媒体等）
- ✅ 完整的分流规则

**代理组类型**:
1. **🚀 节点选择**: 手动选择节点
2. **♻️ 自动选择**: 延迟测试自动选择
3. **📺 流媒体**: 流媒体专用
4. **🎯 全球直连**: 直连不走代理
5. **🛑 广告拦截**: 拦截广告域名
6. **🐟 漏网之鱼**: 其他所有流量

---

### 3. converter.py - 主程序

**功能**: 命令行接口，整合解析和生成功能

**主要函数**:

```python
# 从 URL 获取订阅
def fetch_subscription(url: str) -> str

# 从文件读取订阅
def read_subscription_file(file_path: str) -> str

# 主函数（命令行入口）
def main()
```

**命令行参数**:
```bash
--url          # 订阅链接 URL
--file         # 本地订阅文件路径
--nodes        # 单个节点链接（可多个）
--output       # 输出文件路径（默认: clash_config.yaml）
--proxy-group  # 代理组名称（默认: 🚀 节点选择）
--test         # 测试模式，只解析不生成文件
```

---

### 4. test_converter.py - 测试脚本

**功能**: 测试转换器的各项功能

**包含的测试**:
1. 协议解析测试
2. 配置生成测试
3. 文件保存测试

**运行方式**:
```bash
python test_converter.py
```

---

## 📚 文档文件说明

### README.md
- 项目总览
- 安装说明
- 基本使用方法
- 功能特性

### QUICKSTART.md
- 快速开始指南
- 详细的使用步骤
- 常见问题解答
- 进阶使用技巧

### PROTOCOL_EXAMPLES.md
- 各种协议的格式说明
- 详细的示例
- 字段解释
- 配置建议

### PROJECT_STRUCTURE.md（本文件）
- 项目结构说明
- 文件功能介绍
- 代码架构

---

## 🔧 配置文件说明

### requirements.txt
项目依赖包：
```
pyyaml>=6.0        # YAML 文件处理
requests>=2.31.0   # HTTP 请求（获取订阅）
```

### .gitignore
忽略以下文件：
- Python 缓存文件
- 虚拟环境
- 生成的配置文件（包含敏感信息）
- 订阅文件（包含敏感信息）
- IDE 配置

### example_subscription.txt
订阅文件示例，展示如何组织节点链接

### example_config.yaml
输出配置示例，展示生成的 Clash 配置结构

---

## 🏗️ 代码架构

### 模块化设计

```
用户输入
   ↓
converter.py (主程序)
   ↓
   ├─→ parsers.py (解析节点)
   │      ↓
   │   返回节点列表
   │      ↓
   └─→ generator.py (生成配置)
          ↓
       输出 YAML 文件
```

### 数据流

1. **输入阶段**:
   - 从 URL/文件/命令行获取节点信息
   - 支持订阅链接（多个节点）或单节点

2. **解析阶段**:
   - 识别协议类型
   - 解码 Base64
   - 提取节点参数
   - 返回标准化的节点字典

3. **生成阶段**:
   - 组装配置结构
   - 添加代理组
   - 添加分流规则
   - 验证配置有效性

4. **输出阶段**:
   - 序列化为 YAML
   - 保存到文件
   - 显示统计信息

---

## 🎯 核心数据结构

### 节点字典格式

```python
# Shadowsocks 节点
{
    'name': '节点名称',
    'type': 'ss',
    'server': '服务器地址',
    'port': 端口号,
    'cipher': '加密方式',
    'password': '密码',
}

# VMess 节点
{
    'name': '节点名称',
    'type': 'vmess',
    'server': '服务器地址',
    'port': 端口号,
    'uuid': 'UUID',
    'alterId': 额外ID,
    'cipher': '加密方式',
    'network': '传输协议',
    'tls': True/False,
    'ws-opts': {...},  # WebSocket 配置
}

# VLESS 节点
{
    'name': '节点名称',
    'type': 'vless',
    'server': '服务器地址',
    'port': 端口号,
    'uuid': 'UUID',
    'network': '传输协议',
    'tls': True/False,
    'reality-opts': {...},  # Reality 配置
}

# Hysteria2 节点
{
    'name': '节点名称',
    'type': 'hysteria2',
    'server': '服务器地址',
    'port': 端口号,
    'password': '密码',
    'sni': 'SNI',
}
```

---

## 🚀 扩展开发

### 添加新协议支持

1. 在 `parsers.py` 中添加新的解析方法
2. 在 `parse_proxy()` 方法中添加协议识别
3. 确保返回的字典格式符合 Clash 要求

### 自定义分流规则

修改 `generator.py` 中的 `_generate_rules()` 方法：

```python
def _generate_rules(self, proxy_group_name: str) -> List[str]:
    rules = [
        # 在这里添加自定义规则
        'DOMAIN-SUFFIX,example.com,DIRECT',
        # ... 其他规则
    ]
    return rules
```

### 自定义代理组

修改 `generator.py` 中的 `_generate_proxy_groups()` 方法：

```python
def _generate_proxy_groups(self, proxies, proxy_group_name):
    groups = [
        # 在这里添加自定义代理组
        {
            'name': '🎮 游戏专用',
            'type': 'select',
            'proxies': proxy_names,
        },
        # ... 其他代理组
    ]
    return groups
```

---

## 📝 代码规范

- **命名**: 使用有意义的变量名和函数名
- **注释**: 所有公共方法都有文档字符串
- **类型提示**: 使用 Python 类型提示增强代码可读性
- **异常处理**: 合理的错误处理和用户提示
- **模块化**: 每个模块负责单一职责

---

## 🔍 调试技巧

### 查看解析结果

```bash
python converter.py --url "订阅链接" --test
```

### 查看详细错误

Python 脚本会自动显示详细的错误堆栈

### 验证配置文件

```bash
# 使用 Clash Meta 验证配置
clash-meta -t -f clash_config.yaml
```

---

## 📞 获取帮助

如果需要修改或扩展功能，请：

1. 阅读相关模块的源代码和注释
2. 查看 `PROTOCOL_EXAMPLES.md` 了解协议格式
3. 运行 `test_converter.py` 进行功能测试
4. 使用 `--test` 参数调试解析问题

---

**版本**: 1.0  
**更新时间**: 2025-10  
**Python 版本**: 3.7+

