from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

@app.route("/")
def index():
    name = request.args.get("name", "Guest")
    template = f"Hello, {name}!"
    return render_template_string(template)

# 任意文件读取
@app.route("/read")
def read():
    path = request.args.get("file")
    if not path:
        return "Please specify ?file="
    try:
        return open(path, "r").read()
    except Exception as e:
        return str(e)

# RCE
@app.route("/rce")
def rce():
    cmd = request.args.get("cmd")
    return os.popen(cmd).read()

# ----------------------------
#       新增：SSTI 漏洞点
# ----------------------------
@app.route('/ssti', methods=['GET', 'POST'])
def ssti():
    if request.method == 'POST':
        name = request.form['name']

        # 漏洞点：用户输入拼接模板
        tmpl = f"<h1>{name} is sb</h1>"

        MODE = "echo"  # "noecho" 为无回显模式

        if MODE == "echo":
            return render_template_string(tmpl)

        elif MODE == "noecho":
            render_template_string(tmpl)
            return "success"

    return '''
    <form method="POST">
        <input name="name">
        <button type="submit">Submit</button>
    </form>
    '''

app.run(host="0.0.0.0", port=5000)