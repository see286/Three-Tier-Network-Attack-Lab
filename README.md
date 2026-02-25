# Three-Tier-Network-Attack-Lab

# 三层网络攻击靶场

本仓库包含一个完整的网络安全实验环境，模拟"外网攻击 → 代理穿透 → 内网横向"的攻击链路。

## 环境构成
- 攻击机 (Kali) - 外网
- 代理机 (Kali) - 跳板机，IP: 192.168.2.10
- 内网机 (Kali) - 目标机，IP: 192.168.3.10

## 漏洞设计
- 代理机：弱口令SSH (student/students) + Redis未授权访问
- 内网机：Flask SSTI漏洞 + RCE + 文件读取

## 文件说明
- `实验报告.md` - 完整的环境搭建过程、漏洞构造细节、攻击复现步骤

- `images/` - 报告中的配图

- `attack-vm` - 攻击机

  链接：https://pan.quark.cn/s/544ffe5e29be 提取码：gwSi

- `proxy-vm` - 代理机

  链接：https://pan.quark.cn/s/2ecbb90052e8 提取码：Ta1n

- ` internal-vm` - 内网机

  链接：https://pan.quark.cn/s/4f5b19734cb8 提取码：B4bC

## 快速使用
详见实验报告。

虚拟机账号密码均为kali。