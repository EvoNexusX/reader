import gradio as gr
from openai import OpenAI
import os
import json
from dotenv import load_dotenv, find_dotenv
import requests
from datetime import datetime

from prompts.summary import intensive_reading

# 加载环境变量
_ = load_dotenv(find_dotenv())

# 初始化配置
def load_config():
    if os.path.exists(".env"):
        load_dotenv(find_dotenv())
        return [
            os.environ.get('DEEPSEEK_API_KEY', ""),
            os.environ.get('DEEPSEEK_BASE_URL', ""),
            os.environ.get('MODEL', "deepseek-chat"),
            os.environ.get('TEXTIN_API_ID', ""),
            os.environ.get('TEXTIN_API_SECRET', "")
        ]

# 定义 reasoning 函数
def reasoning(prompt, history, file_content, api_key, base_url, model, temperature, max_tokens):
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # 初始化消息列表
    messages = [{"role": "system", "content": "你是一个杰出的科研工作者，经常精读论文并且擅长写论文精读报告。"}]
    
    # 将文件内容附加到系统消息中（不显示在聊天界面）
    if file_content:
        messages.append({"role": "system", "content": f"论文内容:\n{file_content}"})
    
    # 添加历史消息
    for user_msg, assistant_msg in history:
        if user_msg is not None:
            messages.append({"role": "user", "content": user_msg})
        if assistant_msg is not None:
            messages.append({"role": "assistant", "content": assistant_msg})
    
    # 添加当前用户输入
    if prompt:  # 只有当用户输入不为空时才添加
        messages.append({"role": "user", "content": prompt})
    
    # 调用模型生成回复
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=30,
        stream=True
    )
    reply = ""
    for chunk in response:
        if hasattr(chunk.choices[0].delta, 'content'):
            reply += chunk.choices[0].delta.content
            yield reply

# 处理用户输入并生成回复
def generate_response(prompt, history, file_content, temperature, max_tokens):
    # 从 .env 文件中读取配置
    config = load_config()
    api_key = config[0]
    base_url = config[1]
    model = config[2]
    
    if not api_key or not base_url:
        raise gr.Error("⚠️ 请先在 .env 文件中配置 DeepSeek API Key 和 Base URL")
    
    try:
        reply = ""
        for partial_reply in reasoning(prompt, history, file_content, api_key, base_url, model, temperature, max_tokens):
            reply = partial_reply
            # 返回最新的部分回复，并更新历史记录
            yield history + [(prompt, reply)], gr.update(choices=[
                "这篇论文的核心贡献是什么？",
                "这篇论文的研究方法是什么？",
                "这篇论文的实验结果如何？"
            ]), history + [(prompt, reply)]  # 更新历史记录

        # 生成后续问题并更新悬浮按钮组
        # follow_up_questions = generate_follow_up_questions(history + [(prompt, reply)])
        yield history + [(prompt, reply)], gr.update(choices=[
            "这篇论文的核心贡献是什么？",
            "这篇论文的研究方法是什么？",
            "这篇论文的实验结果如何？"
        ]), history + [(prompt, reply)]  # 更新历史记录
    
    except Exception as e:
        history.append((None, f"❌ 请求失败：{str(e)}"))
        yield history, gr.update(choices=[
            "这篇论文的核心贡献是什么？",
            "这篇论文的研究方法是什么？",
            "这篇论文的实验结果如何？"
        ]), history  # 更新历史记录

# 保存总结到 Markdown 文件
def save_summary_to_markdown(summary, file_name):
    # 获取当前时间
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 创建保存目录
    save_dir = "summaries"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 生成文件名
    base_name = os.path.splitext(file_name)[0]
    summary_file_name = f"{base_name}_summary.md"
    summary_file_path = os.path.join(save_dir, summary_file_name)
    
    # 写入 Markdown 文件
    with open(summary_file_path, "w", encoding="utf-8") as f:
        f.write(f"# 论文总结：{file_name}\n\n")
        f.write(summary)
    
    print(f"总结已保存到：{summary_file_path}")

# 文件上传后生成总结
def summarize_after_upload(file_content, history, temp, tokens):
    # 直接调用 reasoning 函数生成总结，不显示提示词
    summary_response = reasoning(intensive_reading, history, file_content, initial_config[0], initial_config[1], initial_config[2], temp, tokens)

    # 流式返回生成器的结果
    reply = ""
    for partial_reply in summary_response:
        reply = partial_reply
        yield history + [(f"📄 {file_name}", reply)], gr.update(choices=[
            "这篇论文的核心贡献是什么？",
            "这篇论文的研究方法是什么？",
            "这篇论文的实验结果如何？"
        ]), history + [(f"📄 {file_name}", reply)]  # 更新历史记录

    # 保存总结到本地
    save_summary_to_markdown(reply, file_name)

# TextinOcr 类
class TextinOcr:
    def __init__(self, app_id, app_secret):
        self._app_id = app_id
        self._app_secret = app_secret
        self.host = 'https://api.textin.com'

    def recognize_pdf2md(self, image_path, options, is_url=False):
        url = self.host + '/ai/service/v1/pdf_to_markdown'
        headers = {
            'x-ti-app-id': self._app_id,
            'x-ti-secret-code': self._app_secret
        }
        if is_url:
            image = image_path
            headers['Content-Type'] = 'text/plain'
        else:
            with open(image_path, 'rb') as fp:
                image = fp.read()
            headers['Content-Type'] = 'application/octet-stream'

        return requests.post(url, data=image, headers=headers, params=options)

# 动态主题系统
theme_styles = {
    "翡翠绿": "--primary-50: #ecfdf5; --primary-100: #d1fae5; --primary-200: #a7f3d0; --primary-300: #6ee7b7; --primary-400: #34d399; --primary-500: #10b981;",
    "科技蓝": "--primary-50: #eff6ff; --primary-100: #dbeafe; --primary-200: #bfdbfe; --primary-300: #93c5fd; --primary-400: #60a5fa; --primary-500: #3b82f6;",
    "活力橙": "--primary-50: #fff7ed; --primary-100: #ffedd5; --primary-200: #fed7aa; --primary-300: #fdba74; --primary-400: #fb923c; --primary-500: #f97316;",
    "暗夜紫": "--primary-50: #f5f3ff; --primary-100: #ede9fe; --primary-200: #ddd6fe; --primary-300: #c4b5fd; --primary-400: #a78bfa; --primary-500: #8b5cf6;",
    "浪漫粉": "--primary-50: #fdf2f8; --primary-100: #fce7f3; --primary-200: #fbcfe8; --primary-300: #f9a8d4; --primary-400: #f472b6; --primary-500: #ec4899;",
    "深海蓝": "--primary-50: #f0f9ff; --primary-100: #e0f2fe; --primary-200: #bae6fd; --primary-300: #7dd3fc; --primary-400: #38bdf8; --primary-500: #0ea5e9;",
    "经典红": "--primary-50: #fef2f2; --primary-100: #fee2e2; --primary-200: #fecaca; --primary-300: #fca5a5; --primary-400: #f87171; --primary-500: #ef4444;"
}

# 创建 Gradio 界面
with gr.Blocks(theme=gr.themes.Soft(primary_hue="emerald")) as demo:
    # 动态 CSS 注入
    theme_css = gr.HTML("""
    <style id="dynamic-theme">
    :root {
        %THEME_CSS%
    }
    .preset-questions {
        position: sticky;
        top: 10px;
        z-index: 100;
        background: var(--primary-50);
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    </style>
    """)

    # 初始化配置
    initial_config = load_config()

    # 标题栏
    with gr.Row():
        gr.Markdown("""<h1 style='text-align:center; display:inline-block; margin-right:20px'>🚀 Reader 论文阅读助手</h1>""")
        theme_selector = gr.Dropdown(
            label="主题色系",
            choices=list(theme_styles.keys()),
            value="翡翠绿",
            scale=0,
            min_width=120,
            interactive=True
        )

    # 界面布局
    with gr.Row():
        # 右侧主界面
        with gr.Column(scale=4):
            # 介绍区
            gr.Markdown("""
            <div style='
                background: linear-gradient(145deg, #f9f9f9, #ffffff);
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin: 10px 0;
            '>
            <h3 style='color: #333; margin-top: 0;'>欢迎使用 Reader！</h3>
            <p style='color: #555; line-height: 1.6;'>
                        
            #### 1. 高级参数可以调整模型温度和输出最大长度。\n
            #### 2. 生成的精读报告会保存在 summaries 文件夹中。\n
            #### 3. 点击快捷提问中的问题可以进行快速提问。\n
            #### 4. 如果想修改提示词可以在 prompts 文件夹下修改。\n
            #### 如果你想鼓励这个项目并希望它能被更多人发现和使用，非常欢迎您给予一个宝贵的⭐star 支持！每一颗星都是对我们团队努力的认可和激励。只需点击项目的主页上的“Star”按钮，就能帮助我们提升项目的知名度。感谢您的支持与鼓励，让我们能够持续改进并带来更多有价值的功能和更新！如果您对项目有任何建议或想法，也非常欢迎分享给我们。再次感谢您的贡献！
 
            </p>
            </div>
            """)

            # 聊天区
            chatbot = gr.Chatbot(
                label="对话记录",
                height=500,
                bubble_full_width=False
            )

            # 文件上传提示
            file_info = gr.Markdown("", elem_classes="file-info")

            # 悬浮按钮组
            with gr.Row():
                with gr.Column(scale=1):
                    preset_questions = gr.Radio(
                        label="快捷提问",
                        choices=[
                            "这篇论文的核心贡献是什么？",
                            "这篇论文的研究方法是什么？",
                            "这篇论文的实验结果如何？"
                        ],  # 初始设置三个问题
                        value=None,
                        interactive=True,
                        elem_classes="preset-questions"
                    )

            # 输入控制区
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="输入消息...",
                    show_label=False,
                    container=False,
                    scale=5,
                    lines=3,
                    elem_classes="input-textbox"
                )
                with gr.Column(scale=1):
                    submit_btn = gr.Button("发送", variant="primary", size="lg")
                    file_btn = gr.UploadButton("📁 上传文件", file_types=[".pdf"], size="lg")

            # 参数设置
            with gr.Accordion("⚙️ 高级参数", open=False):
                with gr.Row():
                    temp = gr.Slider(0.0, 2.0, value=1.0, label="随机性")
                    tokens = gr.Slider(64, 8192*4, value=4096, step=64, label="最大长度")

    # 状态变量
    file_content = gr.State("")
    history_state = gr.State([])  # 用于保存聊天历史记录

    global file_name
    # 文件上传后解析文档
    def parse_document(file):
        # 从 .env 文件中读取配置
        config = load_config()
        textin_app_id = config[3]
        textin_app_secret = config[4]
        
        if not textin_app_id or not textin_app_secret:
            raise gr.Error("⚠️ 请先在 .env 文件中配置 Textin App ID 和 App Secret")
        
        try:
            textin = TextinOcr(textin_app_id, textin_app_secret)
            resp = textin.recognize_pdf2md(file.name, {
                'page_start': 0,
                'page_count': 1000,
                'table_flavor': 'md',
                'parse_mode': 'scan',
                'page_details': 0,
                'markdown_details': 1,
                'apply_document_tree': 1,
                'dpi': 144
            })
            result = json.loads(resp.text)
            file_content = result.get("result", {}).get("markdown", "解析失败")
            file_content = file_content.encode().decode()
            global file_name
            # 提取文件名（去掉路径）
            file_name = os.path.basename(file.name)
            
            # 返回解析结果和文件名
            return file_content, f"📄 **已上传文件:** {file_name}"
        except Exception as e:
            return "", f"❌ 文件解析失败：{str(e)}"
 
    # 处理用户输入并生成回复
    submit_btn.click(
        generate_response,
        [msg, history_state, file_content, temp, tokens],
        [chatbot, preset_questions, history_state]
    ).then(
        lambda: "", None, [msg]
    )

    # 处理预设问题点击事件
    def ask_preset_question(question, chatbot, history, file_content, temp, tokens):
        if question:
            # 模拟用户输入
            return question, history
        return "", history

    preset_questions.change(
        ask_preset_question,
        [preset_questions, chatbot, history_state, file_content, temp, tokens],
        [msg, history_state]
    ).then(
        generate_response,
        [msg, history_state, file_content, temp, tokens],
        [chatbot, preset_questions, history_state],
        queue=True
    ).then(
        lambda: "", None, [msg]
    )

    # 动态主题切换
    def update_theme(theme_name):
        return gr.HTML(value=f"""
        <style id="dynamic-theme">
        :root {{
            {theme_styles[theme_name]}
        }}
        </style>
        """)

    theme_selector.change(
        update_theme,
        [theme_selector],
        [theme_css],
        queue=False
    )

    # 文件上传后生成总结
    file_btn.upload(
        parse_document,
        [file_btn],
        [file_content, file_info]
    ).then(
        summarize_after_upload,
        [file_content, history_state, temp, tokens],
        [chatbot, preset_questions, history_state]
    )

# 启动应用
demo.launch(
    server_name="0.0.0.0" if os.getenv('ENVIRONMENT') == 'prod' else "127.0.0.1",
    server_port=int(os.getenv('PORT', 7860)),
    share=False  
)