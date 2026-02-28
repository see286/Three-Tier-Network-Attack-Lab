# environment-setup

This document details the network adapter and IP configuration for a three-VM penetration testing environment.

It specifies custom VMnet subnets with disabled DHCP and host adapter access for network isolation.

It outlines static IP setup via nmcli for persistent network configuration across Kali Linux hosts.

------

## 网卡的配置

虚拟机比较好准备令人比较头疼的是网卡的设置，首先我们需要一个192.168.2.和一个192.168.3.的IP地址还有一个无要求的net，所以我们需要先把该IP的网卡配置好，打开VM的菜单栏里面的“编辑”找到“虚拟网络编辑器”我们放管理员权限后向里面添加两个所需网卡如图：

![image-20251125234918885](D:\LJY\Github\Three-Tier-Network-Attack-Lab\images\image-20251125234918885.png)

VMnet2和Vmnet3是我自己加的，分别填子网地址作为所需网卡

需要注意的是，在配置VMnet3的时候建议把“将主机虚拟适配器连接到此网络”取消勾选(这个IP是内网机的，为了防止内网和攻击机直接访问我们将该选项取消勾选)

此外，创建VMnet2和VMnet3的时候一定要取消DHCP(DHCP的作用是自动将IP会自动给机子分配IP，将这个打开后就不利于控制IP因为到时候IP我们是需要自己设置的)

### 三个机子IP地址规划

*攻击机：*因为其是net模式，所以开机前先确定它是不是net不是换成net就ok了

![image-20251125235857333](D:\LJY\Github\Three-Tier-Network-Attack-Lab\images\image-20251125235857333.png)

*代理机*：代理机的作用比较多，从上面的分析我们可以得出来首先需要一个net网卡；因为其IP是固定的所以我们还需要加一个配置其IP(192.168.2)的网卡(VMnet2)；又因为代理机需要和内网相连，所以代理机通内网IP(192.168.3)，所以我们还需要加一个网卡(VMnet3)

![image-20251126000455656](D:\LJY\Github\Three-Tier-Network-Attack-Lab\images\image-20251126000455656.png)

内网机：由于其不能联网所以不需要net网卡；又因为其IP是固定的所以我们还需要加一个配置其IP(192.168.3)的网卡(VMnet3)

![image-20251126000618085](D:\LJY\Github\Three-Tier-Network-Attack-Lab\images\image-20251126000618085.png)

## 系统的配置

由于我的三台虚拟机均使用 Kali Linux，因此系统初始化操作一致。我在这里先统一介绍所有机子都需要执行的通用配置

### 1.查看网络配置

我们首先需要明确我当下正在配的机子的网卡名称：

```css
ip a
```

在这里放一个例子：

![image-20251126002244072](D:\LJY\Github\Three-Tier-Network-Attack-Lab\images\image-20251126002244072.png)

(运行出来大概长这样，我的IP是以及配置好了的配置之前应该eth1和eth2里面没有IP地址)

我们还需要查一下连接名(即确认 “Wired connection 2” 对应的是 eth1、eth2、eth0 中哪一个)：

```css
nmcli con show
```

![image-20251126003033433](D:\LJY\Github\Three-Tier-Network-Attack-Lab\images\image-20251126003033433.png)

(输出大概长这样，这也是配置好了的)

### 2.设置静态IP

命令行如下：

```css
sudo nmcli con mod "连接名字" ipv4.method manual ipv4.addresses 192.168.3.10/24
sudo nmcli con up "连接名字"
```

“连接名字”就是我们刚刚查出来的NAME里面的字符

注意：在题目分析中我曾提到需要持久化操作的事情，在设置静态IP的时候由于Kali 虚拟机均使用 NetworkManager 进行网络管理。通过命令所做的所有修改均会自动写入系统的持久化配置文件，所以通过nmcli 修改设置的静态IP、网关、DNS以及路由表都具有 **持久化效果**，在虚拟机重启后仍然会自动应用，无需再次操作。