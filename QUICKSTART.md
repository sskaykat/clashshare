# 快速开始指南

## 1. 环境准备

确保你已经安装了 Python 3.7 或更高版本。

```bash
# 检查 Python 版本
python --version
# 或
python3 --version
```

## 2. 安装依赖

```bash
pip install -r requirements.txt
```

如果你在中国大陆，可以使用国内镜像加速：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 3. 基本使用

### 方式 1：从订阅链接转换（最常用）

```bash
python converter.py --url "你的订阅链接" --output my_clash_config.yaml
```

### 方式 2：从本地文件转换

1. 创建一个文本文件，例如 `my_nodes.txt`
2. 将节点分享链接逐行粘贴到文件中
3. 运行转换命令：

```bash
python converter.py --file my_nodes.txt --output my_clash_config.yaml
```

### 方式 3：直接添加节点

```bash
python converter.py \
  --nodes "ss://xxx..." "vmess://yyy..." \
  --output my_clash_config.yaml
```

### 方式 4：混合使用

```bash
python converter.py \
  --url "订阅链接" \
  --nodes "额外的节点1" "额外的节点2" \
  --output my_clash_config.yaml
```

## 4. 测试解析

在实际生成配置文件之前，你可以先测试节点是否能被正确解析：

```bash
python converter.py --url "你的订阅链接" --test
```

这会显示所有解析到的节点信息，但不会生成配置文件。

## 5. 导入到 Clash Meta

### Windows:
1. 找到生成的 `my_clash_config.yaml` 文件
2. 打开 Clash Meta（Clash Verge、Clash for Windows Meta 版等）
3. 在配置文件管理中导入该文件
4. 启用新配置

### macOS:
1. 打开 ClashX Meta
2. 配置 > 管理配置 > 导入配置文件
3. 选择生成的 YAML 文件

### Linux:
```bash
# 复制配置文件到 Clash Meta 配置目录
cp my_clash_config.yaml ~/.config/clash/config.yaml

# 重启 Clash Meta 服务
systemctl restart clash-meta
```

## 6. 验证配置

1. 启动 Clash Meta
2. 开启系统代理
3. 访问测试网站：
   - 国内网站（应该直连）：https://www.baidu.com
   - 国外网站（应该走代理）：https://www.google.com

4. 打开 Clash 控制面板进行节点测速：
   - 通常地址：http://clash.razord.top
   - 或：http://127.0.0.1:9090/ui

## 7. 常见问题

### Q: 提示"没有成功解析任何节点"怎么办？

A: 检查以下几点：
- 订阅链接是否有效（可以在浏览器中打开试试）
- 节点格式是否正确
- 使用 `--test` 参数查看详细的解析日志

### Q: 生成的配置文件无法在 Clash 中使用？

A: 确保你使用的是 **Clash Meta** 核心，而不是普通的 Clash 核心。某些高级功能（如 VLESS Reality）只有 Meta 核心支持。

### Q: 如何自定义代理组名称？

A: 使用 `--proxy-group` 参数：

```bash
python converter.py --url "订阅链接" --proxy-group "我的代理" --output config.yaml
```

### Q: 需要定期更新订阅吗？

A: 是的，建议定期（如每周）重新运行转换器，以获取最新的节点信息。

## 8. 进阶技巧

### 自动化脚本（Windows PowerShell）

创建 `update_clash.ps1`：

```powershell
$subscription = "你的订阅链接"
$output = "clash_config.yaml"

python converter.py --url $subscription --output $output

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 订阅更新成功！" -ForegroundColor Green
    # 可选：自动复制到 Clash 配置目录
    # Copy-Item $output "C:\Users\你的用户名\.config\clash\config.yaml"
} else {
    Write-Host "❌ 订阅更新失败！" -ForegroundColor Red
}
```

### 自动化脚本（Linux/macOS）

创建 `update_clash.sh`：

```bash
#!/bin/bash

SUBSCRIPTION="你的订阅链接"
OUTPUT="clash_config.yaml"

python3 converter.py --url "$SUBSCRIPTION" --output "$OUTPUT"

if [ $? -eq 0 ]; then
    echo "✅ 订阅更新成功！"
    # 可选：自动复制到 Clash 配置目录
    # cp "$OUTPUT" ~/.config/clash/config.yaml
    # systemctl restart clash-meta
else
    echo "❌ 订阅更新失败！"
fi
```

然后设置可执行权限：

```bash
chmod +x update_clash.sh
```

## 9. 获取帮助

查看所有可用选项：

```bash
python converter.py --help
```

遇到问题？请检查：
1. Python 版本是否符合要求
2. 依赖包是否正确安装
3. 订阅链接是否可访问
4. 节点格式是否正确

如果问题仍然存在，请提供详细的错误信息以便排查。

