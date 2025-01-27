## Reader - 一个专为科研人员涉及的论文阅读神器

> ##### 1. 高级参数可以调整模型温度和输出最大长度。
> ##### 2. 生成的精读报告会保存在 summaries 文件夹中。
> ##### 3. 点击快捷提问中的问题可以进行快速提问。
> ##### 4. 如果想修改提示词可以在 prompts 文件夹下修改。
> #### 如果你想鼓励这个项目并希望它能被更多人发现和使用，非常欢迎您给予一个宝贵的⭐star 支持！每一颗星都是对我们团队努力的认可和激励。只需点击项目的主页上的“Star”按钮，就能帮助我们提升项目的知名度。感谢您的支持与鼓励，让我们能够持续改进并带来更多有价值的功能和更新！如果您对项目有任何建议或想法，也非常欢迎分享给我们。再次感谢您的贡献！
 
### 上手指南

###### **安装准备**
> 两个都有免费额度，可以先试用。
> 使用 TextIn 的原因：TextIn 解析速度快，效果好，可以更好地处理论文。

1. 获取 DeepSeek API [https://platform.deepseek.com](https://platform.deepseek.com)
2. 获取 TextIn 的 **apiid** 和 **apisecret**  [https://www.textin.com](https://www.textin.com)


###### **克隆项目**
```sh
git clone https://github.com/EvoNexusX/reader.git
```

###### **配置环境**
```sh
pip install -r requirements.txt
```

##### **配置 key**
> 在根目录下新建 .env 文件，参考以下格式填入。（可替换模型）
```
MODEL="xxx"
DEEPSEEK_API_KEY="sk-xxx"
DEEPSEEK_BASE_URL="xxx"
TEXTIN_API_ID="xxx"
TEXTIN_API_SECRET="xxx"
```


###### **启动项目**
```sh
python main.py
```
点击 http://127.0.0.1:7860 或者在浏览器访问链接即可。

### **使用说明**
1. 上传文件后，会自动生成精读报告，保存在 summaries 文件夹中。
2. 可以通过快捷提问或者输入问题进行提问。
3. 高级设置里可以调节模型 temperature 和 max_tokens。

### 作者
evonexusx@gmail.com
 
 