# network-isolation

This section configures persistent routing rules to define packet forwarding paths across three network segments.

It enables IPv4 forwarding and SNAT on the proxy host to facilitate inter-segment communication and network access.

It implements granular iptables policies on the proxy host to enforce strict network isolation between attacker and internal hosts.

------

### 路由的配置

**路由：**路由是主机决定“某个目标 IP 的数据包应从哪个网卡、经过哪条路径发送出去”的过程，我们需要规定路由的路线

*攻击机和内网机：*因为他们都只有一个卡只能访问自己的网络，所以他们需要先将数据包交给代理机的IP然后通过 eth0 发出去。

例：在攻击机里面有这么个指令：

```bash
sudo ip route add 192.168.2.0/24 via 192.168.36.136 dev eth0
```

即告诉攻击机：如果目标是 192.168.2.*，就把数据包先交给192.168.36.136（代理机的外网 IP），通过 eth0 发出去

另一个IP192.168.2.*一样

而在内网机里面我们需要将内网机所有出网流量都交给代理机处理：

```bash
sudo ip route add default via 192.168.3.2 dev eth0
```

由于内网机只有内网所以内网机只能设置192.168.3.10/24网段这一条默认路由

*代理机：*由于代理机本身连接三个网段且每个网段都是直连，所以它天然就是一个三网卡路由器

所以我们在配置路由的时候直接：

```bash
sudo ip route add 192.168.2.0/24 dev eth1
sudo ip route add 192.168.3.0/24 dev eth2
sudo ip route add 192.168.36.0/24 dev eth0
```

即告诉代理机：访问 192.168.2.x 的包，直接走 eth1其余类似

**持久化设计：**

我们之前加的路由都属于手动添加并不是永久化路由，而在上面的报告中静态IP的设置时我提过通过nmcli 修改设置的静态IP、网关、DNS以及路由表都具有 **持久化效果**所以我们也可以用该方法配置路由：

内网机：

```bash
sudo nmcli connection modify "Wired connection 1" ipv4.method manual ipv4.addresses "192.168.3.10/24" ipv4.gateway "192.168.3.2" ipv4.dns "8.8.8.8"
sudo nmcli connection up "Wired connection 1"
```

攻击机：

```bash
sudo nmcli connection modify "Wired connection 1" +ipv4.routes "192.168.2.0/24 192.168.36.136"
sudo nmcli connection modify "Wired connection 1" +ipv4.routes "192.168.3.0/24 192.168.36.136"
```

代理机：

```bash
sudo nmcli connection modify "eth1-connection" ipv4.routes "192.168.2.0/24"
sudo nmcli connection modify "eth2-connection" ipv4.routes "192.168.3.0/24"
sudo nmcli connection modify "eth0-connection" ipv4.routes "192.168.36.0/24"
```

### IP转发的配置

**IP转发：**Linux默认不允许自己成为“路由器”即不允许自己承担一个数据传输者的功能，在IP转发开启后，Linux才能把收到的数据包转发给其他网段设备，所以如果代理机的转发不开启，那么两端的互ping也没办法成功。

在配置环境过程中主要的操作是IPv4的转发设置，这是需要做一个全局的转发(攻击机和代理机可以互ping，代理机和内网机也可以互ping)：

```css
sudo sysctl -w net.ipv4.ip_forward=1
```

这段命令就表示让 Linux 允许把收到的 IPv4 包按照路由表继续“转发”出去。

**持久化设计**：

我们需要编辑一个文件将该命令保存在该文档里面然后启动配置就可以实现开机自启了：

```bash
sudo nano /etc/sysctl.conf
```

```ini
net.ipv4.ip_forward = 1
```

```bash
sudo sysctl -p
```

### NAT的配置

**NAT：**NAT又称网络地址转换，它主要有两种作用：

一个是把内网设备的源 IP 替换成路由器的 IP，使其能访问外网(该转换即源地址转换**SNAT**)

另一个通常用于端口转发等功能，使外部流量能访问内部服务器(即目标地址转换**DNAT**)

在我们的实验中，要让内网机能够通过代理机访问网络就需要开启SNAT。

我们在代理机执行：

```bash
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```

其中"-t nat"就表示在NAT表上操作，”POSTROUTING“表示对“即将发出本机”的数据包做转换，“-o eth0”即离开代理机，从eth0网卡出去的流量执行NAT，最后的“MASQUERADE”表明自动使用该网卡当前的 IP 来做 SNAT

我们在给代理机设置NAT其实就相当于把代理机变成了内网机的路由器模式让内网机通过替换成代理机IP最终实现正常访问互联网的需求。

同时，由于我们的NAT只做SNAT，不做DNAT，那么外部流量就不能访问内部服务器，也就实现了隔离，即攻击机永远无法直接访问内网。

**持久化设计：**

NAT的持久化我们需要借助iptables-persistent服务，所以我们要先安装：

```bash
sudo apt install iptables-persistent
sudo netfilter-persistent save
```

该指令将当前的iptables规则写入了/etc/iptables/rules.v4在下次开机就可以自动恢复 NAT 规则，这个也是Kali最标准、稳定的持久化方法。

### 代理机iptables策略设计

在我们的实验中，代理机同时连接了三个网段，在前面的分析中我们可以总结出来：代理机需要运行攻击机访问ip.2禁止访问ip.3，而要实现这个也就需要我们进行防火墙规则设置，相当于在代理机上搭了个防火墙阻止攻击机访问子网实现隔离。

由于 iptables 是 Linux 下最基础且最强大的防火墙控制工具，所以我们使用它对代理机进行访问控制。

在完成了上面所有操作后，我们只是实现了虚拟机间基本的连通性，这样会导致攻击机可以直接访问内网这是不符合我们预期的，所以最终我通过编写iptables 策略成功限制了攻击机的访问，这使得攻击机只能访问IP.2，而不能进入IP.3。

**清空旧的规则：**

为了避免之前调试时添加的规则影响最终结果，我首先清空所有表、链：

```bash
sudo iptables -F
sudo iptables -X
sudo iptables -t nat -F
sudo iptables -t nat -X
```

**设置默认策略：**

我们首先默认全部拒绝，只放行运行的流量来实现防火墙的“防”：

```bash
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT ACCEPT
```

其中，“INPUT DROP”表示外部进入代理机的流量默认解决；“FORWARD DROP”表示任何跨网段的转发都默认被阻断；而“OUTPUT ACCEPT”指代理机可以自由访问外界。

接下来我们需要细化“INPUT”和“FORWARD”来实现防火墙：

**INPUT链策略：**

我们需要允许回环、本机会话、以及攻击机访问代理机即将这些从拒绝范畴去掉：

```bash
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A INPUT -s 192.168.36.0/24 -j ACCEPT
```

其中lo是回环流量，在这段指令中，我们实现了包允许被返回以及外部攻击机运行访问代理机(第三行命令.36是代理机net的IP)

**FORWARD 链策略：**

我们在配流量转发的时候需要实现三个部分：

首先是允许代理机发出的流量返回给攻击机：

```bash
sudo iptables -A FORWARD -s 192.168.36.0/24 -d 192.168.2.0/24 -j ACCEPT
sudo iptables -A FORWARD -s 192.168.2.0/24 -d 192.168.36.0/24 -m state --state ESTABLISHED,RELATED -j ACCEPT
```

其次是要禁止攻击机直接访问内网,攻击机只能访问代理机：

```bash
sudo iptables -A FORWARD -s 192.168.36.0/24 -d 192.168.3.0/24 -j DROP
```

最后还要允许代理机发出的流量和内网机发出的流量能够互通：

```bash
sudo iptables -A FORWARD -s 192.168.2.0/24 -d 192.168.3.0/24 -j ACCEPT
sudo iptables -A FORWARD -s 192.168.3.0/24 -d 192.168.2.0/24 -m state --state ESTABLISHED,RELATED -j ACCEPT
```

这样我们就实现了在流量方面对防火墙的控制！

**持久化：**和NAT相同，我们也使用 iptables-persistent对其进行持久化：

```bash
sudo apt install iptables-persistent
sudo netfilter-persistent save
```

该部分小结：**只有在加入“禁止攻击机访问内网 3”的 FORWARD 规则后，整个多网段隔离模型才真正稳定运作**

