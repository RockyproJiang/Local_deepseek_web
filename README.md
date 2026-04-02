# 🤖 AI 伴侣

一个基于Streamlit和Ollama的智能AI对话伴侣应用，支持长期记忆、多会话管理和个性化角色配置。

## ✨ 功能特点

- 🧠 **长期记忆系统**：AI能够记住用户的重要信息和对话历史
- 💬 **多会话管理**：支持创建、切换、重命名和删除多个对话会话
- 🎭 **个性化角色配置**：自定义AI的角色名称和性格特征
- 📝 **智能对话总结**：自动总结长对话，保持上下文连贯
- 🔄 **流式响应**：实时显示AI的思考过程和回复内容
- 💾 **数据持久化**：自动保存会话历史和长期记忆

## 🚀 快速开始

### 前置要求

- Python 3.8+
- [Ollama](https://ollama.ai/) 已安装并运行
- DeepSeek-R1 模型已下载

### 安装Ollama和模型

```bash
# 安装Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# 或访问 https://ollama.ai/download 下载Windows版本

# 下载DeepSeek-R1模型
ollama pull deepseek-r1:8b
安装Python依赖
bash
pip install -r requirements.txt
运行应用
bash
streamlit run app.py
应用将在 http://localhost:8501 启动

📖 使用说明
基础功能
对话：在输入框输入消息，AI会实时响应

新建会话：点击侧边栏的"新建会话"按钮

切换会话：点击会话列表中的会话名称

查看AI记忆：点击右上角的"AI记忆"按钮

AI角色配置
在侧边栏可以自定义：

AI角色名称：如"心理咨询师"、"学习伙伴"等

AI性格特征：描述AI的说话风格和行为特点

长期记忆系统
AI会自动记住：

用户的个人信息（姓名、年龄、职业等）

重要的对话内容

用户偏好和喜好

记忆可以通过侧边栏的"AI记忆"按钮查看和管理。

🏗️ 项目结构
text
ai-companion/
├── app.py                 # 主程序
├── requirements.txt       # Python依赖
├── README.md             # 项目文档
├── .gitignore            # Git忽略文件
├── ai_companion_data.pkl # 会话数据（自动生成）
└── ai_long_term_memory.json # 长期记忆（自动生成）
🔧 配置说明
API配置
默认使用本地Ollama API：http://localhost:11434/api/chat

如需修改，请编辑 app.py 中的 url 变量。

模型配置
默认使用 deepseek-r1:8b 模型，可以在 app.py 中修改 payload["model"] 来使用其他模型。

📝 依赖包
streamlit>=1.28.0 - Web应用框架

requests>=2.31.0 - HTTP请求库


❓ 常见问题
Q: 启动时提示连接Ollama失败？
A: 请确保Ollama服务正在运行：ollama serve

Q: 模型响应很慢？
A: 首次运行需要加载模型，之后会变快。也可以尝试使用更小的模型。

Q: 记忆数据保存在哪里？
A: 保存在同目录下的 ai_companion_data.pkl 和 ai_long_term_memory.json 文件中。


🌟 Star History
如果这个项目对你有帮助，欢迎给个Star ⭐