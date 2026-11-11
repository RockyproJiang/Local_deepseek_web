# AI 伴侣

AI 伴侣——基于 Streamlit + Ollama 的智能对话应用，支持长期记忆、多会话管理、自定义 AI 角色、思考过程展示与对话导出/清空，数据本地保存。

## 功能特性

- **长期记忆**：自动记住个人信息、重要对话与用户偏好（如「我叫」「我喜欢」「我住在」等语句），并在后续对话中自然调用；长期记忆保存为 `ai_long_term_memory.json`。
- **多会话管理**：创建、切换、重命名、删除多个相互独立的会话，会话数据保存为 `ai_companion_data.pkl`。
- **自定义 AI 角色**：在侧边栏设置 AI 角色名称与性格特征，作为系统提示词注入请求。
- **思考过程展示**：解析模型输出中的 `<think></think>` 标签（`parse_ai_response`），以灰色斜体「💭」先展示推理过程，再以粗体给出正式回复。
- **对话历史与长期记忆自动保存**：消息、会话结构与记忆均落盘，重启应用后继续沿用。
- **导出与清空管理**：支持导出长期记忆 JSON（`st.download_button`）、清空全部长期记忆、清空全部会话。

## 技术栈 / 依赖

- Python 3.8+、[Streamlit](https://streamlit.io/)（`streamlit>=1.28.0`）
- `requests>=2.31.0`（见 `requirements.txt`）
- 本机 [Ollama](https://ollama.com/) 服务及 DeepSeek 模型（默认 `deepseek-r1:8b`，定义于 `app.py` 的 `DEFAULT_MODEL`）

## 目录结构

```text
Local_deepseek_web/
├── app.py            # Streamlit 主程序：界面、会话/记忆管理、Ollama 请求与流式渲染
├── requirements.txt  # Python 依赖
├── LICENSE.txt       # MIT 许可证
├── .gitignore        # 忽略缓存、.env、数据与日志等
└── README.md
```

> 运行后会在同目录自动生成 `ai_companion_data.pkl`（会话数据）与 `ai_long_term_memory.json`（长期记忆），两者由 `.gitignore` 覆盖，不纳入版本控制。

## 快速开始

1. 安装并启动 Ollama，拉取模型：

```bash
git clone https://github.com/RockyproJiang/Local_deepseek_web.git
cd Local_deepseek_web

ollama serve
ollama pull deepseek-r1:8b
```

2. 安装依赖并启动 Web 应用：

```bash
pip install -r requirements.txt
streamlit run app.py
```

启动后在浏览器访问 `http://localhost:8501`。如需修改 Ollama 地址或模型，编辑 `app.py` 中的 `OLLAMA_API_URL` 与 `DEFAULT_MODEL`。

## 配置与安全说明

- **无 API Key、无密钥、数据本地存储**：本项目不调用任何云端大模型，也不需要任何凭据；对话、会话与长期记忆均保存在本机文件（`ai_companion_data.pkl`、`ai_long_term_memory.json`）。
- 依赖本机 Ollama 服务（`http://localhost:11434/api/chat`），须自行确保 `ollama serve` 已启动并已拉取对应模型；连接失败时请先检查服务状态。
- Streamlit 默认仅监听本机（`localhost`），请勿在未加认证的情况下把服务直接暴露到公网；如需远程访问，应自行配置反向代理与访问控制。
- `.gitignore` 已包含 `.env`、`*.db`、`*.log` 等条目；本地生成的数据文件请勿随仓库公开提交，其中可能包含个人隐私内容。

## 许可证

本项目采用 MIT License，详见 `LICENSE.txt`（Copyright (c) 2024 AI Companion）。
