# 协议格式说明与示例

本文档详细说明了各种代理协议的链接格式和示例。

## 支持的协议

- [Shadowsocks (SS)](#shadowsocks-ss)
- [ShadowsocksR (SSR)](#shadowsocksr-ssr)
- [VMess](#vmess)
- [VLESS](#vless)
- [Hysteria2](#hysteria2)
- [Trojan](#trojan)
- [HTTP/HTTPS](#httphttps)
- [SOCKS](#socks)

---

## Shadowsocks (SS)

### 格式说明

```
ss://base64(method:password@server:port)#备注名称
```

或者：

```
ss://base64(method:password)@server:port#备注名称
```

### 字段说明

- `method`: 加密方式（如 aes-256-gcm, chacha20-ietf-poly1305）
- `password`: 密码
- `server`: 服务器地址
- `port`: 端口号
- `备注名称`: 节点显示名称（可选）

### 示例

```
ss://YWVzLTI1Ni1nY206dGVzdHBhc3N3b3JkQDE5Mi4xNjguMS4xOjg4ODg=#我的SS节点
```

解码后的内容：
```
method: aes-256-gcm
password: testpassword
server: 192.168.1.1
port: 8888
```

### 常用加密方式

- `aes-128-gcm` ⭐ 推荐
- `aes-256-gcm` ⭐ 推荐
- `chacha20-ietf-poly1305` ⭐ 推荐
- `aes-128-cfb`
- `aes-256-cfb`

---

## ShadowsocksR (SSR)

### 格式说明

```
ssr://base64(server:port:protocol:method:obfs:base64(password)/?obfsparam=base64(混淆参数)&protoparam=base64(协议参数)&remarks=base64(备注)&group=base64(分组))
```

### 字段说明

- `server`: 服务器地址
- `port`: 端口号
- `protocol`: 协议（如 origin, auth_sha1_v4, auth_aes128_md5）
- `method`: 加密方式
- `obfs`: 混淆方式（如 plain, http_simple, tls1.2_ticket_auth）
- `password`: 密码（base64 编码）
- `obfsparam`: 混淆参数（可选）
- `protoparam`: 协议参数（可选）
- `remarks`: 备注名称（可选）

### 示例

SSR 链接通常较长，这里提供一个简化的结构示例：

```
ssr://c2VydmVyLmNvbTo4MDg4OmF1dGhfc2hhMV92NDphZXMtMjU2LWNmYjpodHRwX3NpbXBsZTpiYXNlNjRfcGFzc3dvcmQvP29iZnNwYXJhbT0mcmVtYXJrcz1TU1LoioLngrk=
```

---

## VMess

### 格式说明

```
vmess://base64(json配置)
```

JSON 配置结构：

```json
{
  "v": "2",
  "ps": "备注名称",
  "add": "服务器地址",
  "port": "端口",
  "id": "UUID",
  "aid": "额外ID",
  "scy": "加密方式",
  "net": "传输协议",
  "type": "伪装类型",
  "host": "伪装域名",
  "path": "路径",
  "tls": "tls或空",
  "sni": "SNI"
}
```

### 字段说明

#### 基础字段
- `v`: 版本号，固定为 "2"
- `ps`: 节点名称（备注）
- `add`: 服务器地址
- `port`: 端口号
- `id`: UUID（用户ID）
- `aid`: 额外ID（alterId），现在通常为 0
- `scy`: 加密方式，通常为 "auto" 或 "aes-128-gcm"

#### 传输协议（net）
- `tcp`: TCP 传输 ⭐ 默认
- `ws`: WebSocket ⭐ 常用
- `h2`: HTTP/2
- `grpc`: gRPC
- `kcp`: KCP

#### TLS 配置
- `tls`: 填 "tls" 表示启用，空表示不启用
- `sni`: SNI（服务器名称指示）

### 示例

#### WebSocket + TLS

```json
{
  "v": "2",
  "ps": "香港节点-WS",
  "add": "hk.example.com",
  "port": "443",
  "id": "12345678-1234-1234-1234-123456789abc",
  "aid": "0",
  "scy": "auto",
  "net": "ws",
  "type": "none",
  "host": "hk.example.com",
  "path": "/v2ray",
  "tls": "tls",
  "sni": "hk.example.com"
}
```

编码后：
```
vmess://eyJ2IjoiMiIsInBzIjoi6aaZ5riv6IqC54K5LVdTIiwiYWRkIjoiaGsuZXhhbXBsZS5jb20iLCJwb3J0IjoiNDQzIiwiaWQiOiIxMjM0NTY3OC0xMjM0LTEyMzQtMTIzNC0xMjM0NTY3ODlhYmMiLCJhaWQiOiIwIiwic2N5IjoiYXV0byIsIm5ldCI6IndzIiwidHlwZSI6Im5vbmUiLCJob3N0IjoiaGsuZXhhbXBsZS5jb20iLCJwYXRoIjoiL3YycmF5IiwidGxzIjoidGxzIiwic25pIjoiaGsuZXhhbXBsZS5jb20ifQ==
```

---

## VLESS

### 格式说明

```
vless://uuid@server:port?参数列表#备注名称
```

### 字段说明

#### 基础字段
- `uuid`: 用户ID
- `server`: 服务器地址
- `port`: 端口号

#### URL 参数
- `encryption`: 加密方式，通常为 "none"
- `security`: 安全类型（none, tls, reality）
- `type`: 传输协议（tcp, ws, grpc, http）
- `sni`: SNI
- `path`: 路径（WebSocket）
- `host`: Host 头（WebSocket）
- `serviceName`: 服务名（gRPC）

### 示例

#### WebSocket + TLS

```
vless://12345678-1234-1234-1234-123456789abc@example.com:443?encryption=none&security=tls&type=ws&host=example.com&path=%2Fvless&sni=example.com#VLESS-WS-TLS
```

#### Reality

```
vless://uuid@example.com:443?encryption=none&security=reality&type=tcp&pbk=公钥&sid=短ID&sni=example.com#VLESS-Reality
```

### Reality 特殊参数

- `pbk`: Public Key（公钥）
- `sid`: Short ID（短ID）
- `fp`: Fingerprint（指纹）

---

## Hysteria2

### 格式说明

```
hysteria2://password@server:port?参数列表#备注名称
```

或：

```
hy2://password@server:port?参数列表#备注名称
```

### 字段说明

#### 基础字段
- `password`: 认证密码
- `server`: 服务器地址
- `port`: 端口号

#### URL 参数
- `sni`: SNI
- `insecure`: 跳过证书验证（1=是，0=否）
- `obfs`: 混淆类型（如 salamander）
- `obfs-password`: 混淆密码

### 示例

#### 基础配置

```
hysteria2://mypassword@example.com:443?sni=example.com#Hysteria2节点
```

#### 带混淆

```
hy2://mypassword@example.com:443?sni=example.com&obfs=salamander&obfs-password=obfspass#Hysteria2-混淆
```

---

## Trojan

### 格式说明

```
trojan://password@server:port?参数列表#备注名称
```

### 字段说明

#### 基础字段
- `password`: 密码（认证密钥）
- `server`: 服务器地址
- `port`: 端口号

#### URL 参数
- `sni`: SNI（Server Name Indication）
- `allowInsecure`: 跳过证书验证（1=是，0=否）
- `skipCertVerify`: 跳过证书验证（1=是，0=否）
- `alpn`: ALPN 协议列表（逗号分隔）
- `type`: 传输协议（tcp, ws, grpc）
- `path`: 路径（WebSocket/HTTP）
- `host`: Host 头（WebSocket）
- `serviceName`: 服务名（gRPC）

### 示例

#### 基础配置

```
trojan://mypassword123@example.com:443?sni=example.com#Trojan节点
```

#### WebSocket 传输

```
trojan://mypassword@example.com:443?type=ws&host=example.com&path=%2Ftrojan&sni=example.com#Trojan-WS
```

#### gRPC 传输

```
trojan://mypassword@example.com:443?type=grpc&serviceName=TrojanService&sni=example.com#Trojan-gRPC
```

#### 自定义 ALPN

```
trojan://mypassword@example.com:443?sni=example.com&alpn=h2,http/1.1#Trojan-ALPN
```

### 配置建议

- ✅ 始终使用强密码
- ✅ 正确配置 SNI
- ✅ 使用有效的 TLS 证书
- ✅ 默认端口 443，伪装效果更好

---

## HTTP/HTTPS

### 格式说明

```
http://[username:password@]server:port#备注名称
https://[username:password@]server:port#备注名称
```

### 字段说明

- `username`: 用户名（可选，需要认证时使用）
- `password`: 密码（可选，需要认证时使用）
- `server`: 服务器地址
- `port`: 端口号（HTTP 默认 80，HTTPS 默认 443）

### 示例

#### HTTP 代理（无认证）

```
http://proxy.example.com:8080#HTTP代理
```

#### HTTP 代理（带认证）

```
http://user:pass123@proxy.example.com:8080#HTTP认证代理
```

#### HTTPS 代理

```
https://secure-proxy.example.com:8443#HTTPS代理
```

#### HTTPS 代理（带认证）

```
https://admin:secret@secure-proxy.example.com:443#HTTPS认证代理
```

### 使用场景

- 🏢 **公司代理**: 企业内网代理服务器
- 🌐 **HTTP 隧道**: 简单的 HTTP 代理转发
- 🔒 **HTTPS 代理**: 加密的 HTTP 代理连接

### 注意事项

- HTTP 代理不加密流量，仅适用于内网环境
- HTTPS 代理提供传输加密
- 用户名和密码中的特殊字符需要 URL 编码

---

## SOCKS

### 格式说明

```
socks4://[username:password@]server:port#备注名称
socks5://[username:password@]server:port#备注名称
```

### 字段说明

- `username`: 用户名（可选，SOCKS5 支持）
- `password`: 密码（可选，SOCKS5 支持）
- `server`: 服务器地址
- `port`: 端口号（默认 1080）

### 示例

#### SOCKS5（无认证）

```
socks5://127.0.0.1:1080#本地SOCKS5
```

#### SOCKS5（带认证）

```
socks5://user:pass@proxy.example.com:1080#SOCKS5认证
```

#### SOCKS4

```
socks4://proxy.example.com:1080#SOCKS4代理
```

### SOCKS4 vs SOCKS5

| 特性 | SOCKS4 | SOCKS5 |
|------|--------|--------|
| 认证支持 | ❌ | ✅ |
| IPv6 支持 | ❌ | ✅ |
| UDP 支持 | ❌ | ✅ |
| 域名解析 | 部分 | ✅ |

### 推荐使用

- ✅ **优先使用 SOCKS5**: 功能更全面
- ✅ **需要认证时**: 必须使用 SOCKS5
- ✅ **本地代理**: 常用于 SSH 隧道、本地应用

### 使用场景

- 🔧 **SSH 隧道**: `ssh -D 1080 user@server`
- 🌐 **本地代理工具**: V2Ray、Shadowsocks 的本地端口
- 🖥️ **应用级代理**: 为特定应用提供代理服务

---

## 转换器支持说明

### ✅ 完全支持
- Shadowsocks (所有主流加密方式)
- ShadowsocksR (所有主流配置)
- VMess (TCP, WebSocket, HTTP/2, gRPC)
- VLESS (包括 Reality)
- Hysteria2
- Trojan (TCP, WebSocket, gRPC)
- HTTP/HTTPS (带认证/不带认证)
- SOCKS4/SOCKS5 (带认证/不带认证)

### 🔧 配置建议

1. **加密方式选择**
   - 优先使用 AEAD 加密：`aes-128-gcm`, `aes-256-gcm`, `chacha20-ietf-poly1305`
   - 避免使用过时的 CFB 模式

2. **传输协议选择**
   - 追求性能：TCP
   - 规避检测：WebSocket + TLS + CDN
   - 低延迟游戏：Hysteria2

3. **TLS 配置**
   - 始终启用 TLS
   - 正确设置 SNI
   - 使用有效的证书

### 📝 注意事项

1. **Base64 编码**
   - 标准 Base64 可能包含 padding（`=`）
   - 某些实现会省略 padding
   - 转换器会自动处理两种情况

2. **URL 编码**
   - 路径和参数需要正确的 URL 编码
   - 例如：`/` 应编码为 `%2F`

3. **UUID 格式**
   - 标准格式：`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
   - 必须是有效的 UUID v4

## 获取更多帮助

如果你的节点格式不在上述范围内，或者遇到解析问题，请：

1. 使用 `--test` 参数查看详细解析日志
2. 检查节点格式是否符合标准
3. 确认使用的是最新版本的转换器

