# architecture

This project builds a three-virtual-machine architecture for simulating network penetration attacks.

It defines a multi-segment network with attacker, proxy, and internal hosts in separate subnets.

It specifies strict network isolation and access rules to mimic real-world attack paths.

------

我们搭建了一个三虚拟机环境，用于模拟真实攻击路径中的“外网攻击 → 代理穿透 → 内网横向”的攻击链路。

首先我们需要三个虚拟机：一个虚拟机作为攻击机(外网网段)，用于模拟攻击者攻破内网找到漏洞；一个虚拟机作为中间代理机(跳板)，用于从网络上下载配置，并作为攻击者访问内网的唯一入口；还有一个虚拟机作为内网机(目标)，用于构造漏洞环境供攻击机最终解出来环境。

## IP地址要求

攻击机无IP要求

中间代理机IP为192.168.2.*

内网机IP为192.168.3.*

## 联网要求

首先是攻击机，因为攻击机是不需要提供的所以言外之意就是不用对攻击机的网络作过多限制所以**net模式**就行同时作为攻击机要**能够访问代理机**且**不能直接访问内网机**(相当于在模拟真实攻击中“外网攻击者 → 先打代理机 → 再进入内网”的路径)

其次是代理机，这个机子需要做到能与外网连接即**net模式**(因为题目要求需要从网络上下载配置所以代理机需要满足能联网这一要求)以及**能直接访问内网机**(因为代理机是为了将网络上下载的配置传给内网机所以需要连接内网机)

最后是内网机，这个机子需要做到**与外网断连**即不能联网(因为内网机是用来构造漏洞的且由于题目要求有代理机所以便不再需要联网下载配置)并且该机子只能**访问代理机**(因为代理机下载的配置需要传给它)