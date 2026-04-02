"""
AI 伴侣 - 基于Streamlit和Ollama的智能对话应用
支持长期记忆、多会话管理和个性化角色配置
"""

import streamlit as st
import requests
import json
from datetime import datetime
import hashlib
import os
import pickle
from typing import List, Dict, Any
import re

# 常量定义
DATA_FILE = "ai_companion_data.pkl"
MEMORY_FILE = "ai_long_term_memory.json"
OLLAMA_API_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "deepseek-r1:8b"

# 页面配置
st.set_page_config(
    page_title="AI 伴侣",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)


class LongTermMemory:
    """AI长期记忆系统"""
    
    def __init__(self, memory_file: str = MEMORY_FILE):
        self.memory_file = memory_file
        self.memories = self.load_memories()
    
    def load_memories(self) -> Dict:
        """加载长期记忆"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return self._get_default_memories()
        return self._get_default_memories()
    
    def _get_default_memories(self) -> Dict:
        """获取默认记忆结构"""
        return {
            "user_info": {},
            "important_facts": [],
            "conversation_summaries": []
        }
    
    def save_memories(self) -> bool:
        """保存长期记忆"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memories, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存记忆失败: {e}")
            return False
    
    def extract_and_store_memory(self, user_message: str, ai_response: str) -> None:
        """从对话中提取并存储重要信息"""
        important_keywords = [
            "我是", "我叫", "我今年", "我喜欢", "我讨厌", "我的工作",
            "我是做", "我住在", "我的爱好", "我最近", "我计划",
            "我生日", "我记得"
        ]
        
        for keyword in important_keywords:
            if keyword in user_message:
                sentences = user_message.split("。")
                for sentence in sentences:
                    if keyword in sentence:
                        fact = sentence.strip()
                        if fact not in [f["fact"] for f in self.memories["important_facts"]]:
                            self.memories["important_facts"].append({
                                "fact": fact,
                                "timestamp": datetime.now().isoformat(),
                                "context": user_message[:100]
                            })
                            self.save_memories()
                        break
        
        # 存储对话摘要
        summary = {
            "user": user_message[:200],
            "ai": ai_response[:200],
            "timestamp": datetime.now().isoformat()
        }
        self.memories["conversation_summaries"].append(summary)
        
        # 只保留最近50条
        if len(self.memories["conversation_summaries"]) > 50:
            self.memories["conversation_summaries"] = self.memories["conversation_summaries"][-50:]
        self.save_memories()
    
    def get_relevant_memories(self, current_query: str, limit: int = 5) -> str:
        """获取与当前查询相关的记忆"""
        relevant_memories = []
        
        if self.memories["user_info"]:
            relevant_memories.append("【用户信息】")
            for key, value in self.memories["user_info"].items():
                relevant_memories.append(f"- {key}: {value}")
        
        if self.memories["important_facts"]:
            relevant_memories.append("\n【重要记忆】")
            for fact in self.memories["important_facts"][-10:]:
                relevant_memories.append(f"- {fact['fact']}")
        
        if self.memories["conversation_summaries"]:
            relevant_memories.append("\n【近期对话回顾】")
            for summary in self.memories["conversation_summaries"][-5:]:
                relevant_memories.append(f"- 用户: {summary['user'][:50]}...")
        
        return "\n".join(relevant_memories) if relevant_memories else ""
    
    def update_user_info(self, key: str, value: str) -> None:
        """更新用户信息"""
        self.memories["user_info"][key] = value
        self.save_memories()
    
    def clear_memories(self) -> None:
        """清空所有记忆"""
        self.memories = self._get_default_memories()
        self.save_memories()


def save_data_to_file() -> bool:
    """保存所有会话数据到文件"""
    try:
        data_to_save = {
            "sessions": st.session_state.sessions,
            "summary_count": st.session_state.summary_count,
            "current_session_id": st.session_state.current_session_id
        }
        with open(DATA_FILE, 'wb') as f:
            pickle.dump(data_to_save, f)
        return True
    except Exception as e:
        print(f"保存数据失败: {e}")
        return False


def load_data_from_file() -> Dict:
    """从文件加载会话数据"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'rb') as f:
                return pickle.load(f)
    except Exception as e:
        print(f"加载数据失败: {e}")
    return None


def init_session_state() -> None:
    """初始化会话状态"""
    loaded_data = load_data_from_file()
    
    if loaded_data and "sessions" in loaded_data and loaded_data["sessions"]:
        st.session_state.sessions = loaded_data["sessions"]
        st.session_state.summary_count = loaded_data.get("summary_count", 0)
        st.session_state.current_session_id = loaded_data.get("current_session_id")
        
        if st.session_state.current_session_id not in st.session_state.sessions:
            st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]
    else:
        if "sessions" not in st.session_state or not st.session_state.sessions:
            st.session_state.sessions = {}
        
        if not st.session_state.sessions:
            session_id = hashlib.md5(f"session_{datetime.now()}".encode()).hexdigest()
            st.session_state.sessions[session_id] = {
                "name": f"会话 1",
                "messages": [],
                "created_at": datetime.now(),
                "ai_role": "AI 伴侣",
                "ai_personality": "温柔、体贴、善解人意"
            }
            st.session_state.current_session_id = session_id
            st.session_state.summary_count = 0
    
    if "summary_count" not in st.session_state:
        st.session_state.summary_count = 0
    
    if "long_term_memory" not in st.session_state:
        st.session_state.long_term_memory = LongTermMemory()


def get_current_session() -> Dict:
    """获取当前会话"""
    return st.session_state.sessions[st.session_state.current_session_id]


def save_message(role: str, content: str) -> None:
    """保存消息到当前会话"""
    current_session = get_current_session()
    current_session["messages"].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now()
    })
    save_data_to_file()


def create_new_session() -> None:
    """创建新会话"""
    session_id = hashlib.md5(f"session_{datetime.now()}".encode()).hexdigest()
    current_session = get_current_session()
    st.session_state.sessions[session_id] = {
        "name": f"会话 {len(st.session_state.sessions) + 1}",
        "messages": [],
        "created_at": datetime.now(),
        "ai_role": current_session.get("ai_role", "AI 伴侣"),
        "ai_personality": current_session.get("ai_personality", "温柔、体贴、善解人意")
    }
    st.session_state.current_session_id = session_id
    save_data_to_file()
    st.rerun()


def delete_session(session_id: str) -> bool:
    """安全删除会话"""
    if session_id in st.session_state.sessions:
        is_current = (session_id == st.session_state.current_session_id)
        del st.session_state.sessions[session_id]
        
        if st.session_state.sessions:
            if is_current:
                st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]
        else:
            new_session_id = hashlib.md5(f"session_{datetime.now()}".encode()).hexdigest()
            st.session_state.sessions[new_session_id] = {
                "name": "会话 1",
                "messages": [],
                "created_at": datetime.now(),
                "ai_role": "AI 伴侣",
                "ai_personality": "温柔、体贴、善解人意"
            }
            st.session_state.current_session_id = new_session_id
        
        save_data_to_file()
        return True
    return False


def switch_session(session_id: str) -> None:
    """切换会话"""
    if session_id in st.session_state.sessions:
        st.session_state.current_session_id = session_id
        save_data_to_file()
        st.rerun()


def update_ai_config() -> None:
    """更新AI角色和性格"""
    current_session = get_current_session()
    current_session["ai_role"] = st.session_state.ai_role_input
    current_session["ai_personality"] = st.session_state.ai_personality_input
    save_data_to_file()
    st.success("AI配置已更新！")


def parse_ai_response(content: str) -> tuple:
    """解析AI响应，分离思考内容和正式回复"""
    think_pattern = r'<think>(.*?)</think>'
    think_matches = re.findall(think_pattern, content, re.DOTALL)
    clean_content = re.sub(think_pattern, '', content, flags=re.DOTALL)
    return think_matches, clean_content.strip()


def show_ai_memory() -> None:
    """显示AI的长期记忆"""
    with st.expander("🧠 AI 的长期记忆", expanded=False):
        st.markdown("### AI记住的重要信息")
        
        memory = st.session_state.long_term_memory
        tab1, tab2, tab3, tab4 = st.tabs(["📝 用户信息", "⭐ 重要记忆", "📚 对话回顾", "⚙️ 记忆管理"])
        
        with tab1:
            st.markdown("#### 用户个人信息")
            if memory.memories["user_info"]:
                for key, value in memory.memories["user_info"].items():
                    st.info(f"**{key}**: {value}")
            else:
                st.info("还没有记住用户信息。当您告诉AI关于自己的事情时，AI会记住。")
            
            with st.form("add_user_info"):
                col1, col2 = st.columns(2)
                with col1:
                    info_key = st.text_input("信息类别", placeholder="例如：姓名、年龄、职业")
                with col2:
                    info_value = st.text_input("信息内容", placeholder="具体内容")
                
                if st.form_submit_button("记住这条信息"):
                    if info_key and info_value:
                        memory.update_user_info(info_key, info_value)
                        st.success(f"已记住：{info_key} = {info_value}")
                        st.rerun()
        
        with tab2:
            st.markdown("#### 重要记忆片段")
            if memory.memories["important_facts"]:
                for idx, fact in enumerate(memory.memories["important_facts"][-20:], 1):
                    st.markdown(f"**{idx}.** {fact['fact']}")
                    st.caption(f"📅 {fact['timestamp'][:10]}")
                    st.divider()
            else:
                st.info("还没有重要记忆。")
        
        with tab3:
            st.markdown("#### 最近的对话回顾")
            if memory.memories["conversation_summaries"]:
                for summary in memory.memories["conversation_summaries"][-10:]:
                    with st.chat_message("user"):
                        st.markdown(summary['user'])
                    with st.chat_message("assistant"):
                        st.markdown(summary['ai'][:100] + "..." if len(summary['ai']) > 100 else summary['ai'])
                    st.caption(f"📅 {summary['timestamp'][:10]}")
                    st.divider()
            else:
                st.info("还没有对话记录。")
        
        with tab4:
            st.markdown("#### 记忆管理")
            if st.button("🧹 清空所有长期记忆", type="primary"):
                if st.button("确认清空", key="confirm_clear"):
                    memory.clear_memories()
                    st.success("已清空所有记忆！")
                    st.rerun()
            
            export_memory = json.dumps(memory.memories, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 导出长期记忆",
                data=export_memory,
                file_name=f"ai_memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )


def render_sidebar() -> None:
    """渲染侧边栏"""
    with st.sidebar:
        st.title("💬 AI 伴侣控制台")
        
        if st.button("➕ 新建会话", use_container_width=True):
            create_new_session()
        
        st.divider()
        
        st.subheader("🤖 AI 角色配置")
        current_session = get_current_session()
        
        st.text_input(
            "AI 角色",
            value=current_session.get("ai_role", "AI 伴侣"),
            key="ai_role_input"
        )
        
        st.text_area(
            "AI 性格与属性",
            value=current_session.get("ai_personality", "温柔、体贴、善解人意，喜欢倾听，善于安慰"),
            height=100,
            key="ai_personality_input"
        )
        
        if st.button("💾 保存配置", use_container_width=True):
            update_ai_config()
        
        st.divider()
        
        st.subheader("📚 会话历史")
        
        sessions_to_delete = []
        for session_id, session in st.session_state.sessions.items():
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                if session_id == st.session_state.current_session_id:
                    st.markdown(f"**✨ {session['name']}**")
                else:
                    if st.button(f"💬 {session['name']}", key=f"switch_{session_id}"):
                        switch_session(session_id)
            with col2:
                if st.button("🗑️", key=f"del_{session_id}"):
                    sessions_to_delete.append(session_id)
            with col3:
                if st.button("✏️", key=f"rename_{session_id}"):
                    st.session_state.rename_target = session_id
        
        for session_id in sessions_to_delete:
            if delete_session(session_id):
                st.rerun()
        
        if "rename_target" in st.session_state:
            target_id = st.session_state.rename_target
            if target_id in st.session_state.sessions:
                new_name = st.text_input("新会话名称", value=st.session_state.sessions[target_id]["name"], key="rename_input")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("确认"):
                        st.session_state.sessions[target_id]["name"] = new_name
                        save_data_to_file()
                        del st.session_state.rename_target
                        st.rerun()
                with col2:
                    if st.button("取消"):
                        del st.session_state.rename_target
                        st.rerun()
        
        st.divider()
        
        if st.button("🗑️ 清空所有会话", use_container_width=True, type="secondary"):
            st.session_state.sessions = {}
            create_new_session()
            save_data_to_file()
            st.rerun()
        
        st.caption(f"📊 当前会话消息数: {len(get_current_session()['messages'])}")
        st.caption(f"📝 已总结次数: {st.session_state.summary_count}")
        
        st.divider()
        
        st.subheader("💾 数据管理")
        
        if st.button("⚠️ 重置所有数据", use_container_width=True, type="primary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            if os.path.exists(MEMORY_FILE):
                os.remove(MEMORY_FILE)
            st.session_state.clear()
            init_session_state()
            st.session_state.long_term_memory = LongTermMemory()
            save_data_to_file()
            st.rerun()


def render_chat_interface() -> None:
    """渲染聊天界面"""
    st.title("🤖 AI 伴侣")
    
    current_session = get_current_session()
    st.caption(f"当前AI: {current_session.get('ai_role', 'AI 伴侣')} | 性格: {current_session.get('ai_personality', '温柔体贴')}")
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🧠 AI记忆", use_container_width=True):
            st.session_state.show_memory = not st.session_state.get("show_memory", False)
    
    if st.session_state.get("show_memory", False):
        show_ai_memory()
    
    # 显示聊天历史
    for message in get_current_session()["messages"]:
        if message.get("is_summary"):
            with st.chat_message("📝", avatar="📋"):
                st.caption(message["content"])
        else:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant":
                    think_contents, clean_content = parse_ai_response(message["content"])
                    for think in think_contents:
                        st.markdown(f'<p style="font-size: 0.8em; color: gray; font-style: italic;">💭 {think}</p>', 
                                   unsafe_allow_html=True)
                    if clean_content.strip():
                        st.markdown(f'<p style="font-weight: bold; font-size: 1em;">{clean_content}</p>', 
                                   unsafe_allow_html=True)
                else:
                    st.markdown(message["content"])
    
    # 输入框
    prompt = st.chat_input("💬 输入您的问题...")
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        save_message("user", prompt)
        
        long_term_memory = st.session_state.long_term_memory
        relevant_memories = long_term_memory.get_relevant_memories(prompt)
        
        system_prompt = f"""你是{current_session.get('ai_role', 'AI 伴侣')}，你的性格是：{current_session.get('ai_personality', '温柔、体贴、善解人意')}。

【长期记忆】
{relevant_memories if relevant_memories else "暂无长期记忆"}

请用温柔体贴的语气回答问题。对于需要深度思考的问题，请在<think></think>标签内写出思考过程，然后在标签外给出正式回答。
如果用户提到个人信息（如姓名、年龄、喜好等），请记住并在后续对话中使用。"""
        
        messages_for_api = [{"role": "system", "content": system_prompt}]
        
        recent_messages = get_current_session()["messages"][-20:]
        for msg in recent_messages:
            if not msg.get("is_summary"):
                messages_for_api.append({"role": msg["role"], "content": msg["content"]})
        
        messages_for_api.append({"role": "user", "content": prompt})
        
        payload = {
            "model": DEFAULT_MODEL,
            "messages": messages_for_api,
            "stream": True
        }
        
        try:
            response = requests.post(OLLAMA_API_URL, json=payload, stream=True, timeout=60)
            
            if response.status_code == 200:
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    for line in response.iter_lines():
                        if line:
                            try:
                                chunk = json.loads(line.decode('utf-8'))
                                if 'message' in chunk and 'content' in chunk['message']:
                                    content = chunk['message']['content']
                                    full_response += content
                                    
                                    think_contents, clean_content = parse_ai_response(full_response)
                                    
                                    display_content = ""
                                    for think in think_contents:
                                        display_content += f'<p style="font-size: 0.8em; color: gray; font-style: italic;">💭 {think}</p>'
                                    if clean_content:
                                        display_content += f'<p style="font-weight: bold; font-size: 1em;">{clean_content}</p>'
                                    
                                    if display_content:
                                        message_placeholder.markdown(display_content + "▌", unsafe_allow_html=True)
                            except json.JSONDecodeError:
                                continue
                    
                    think_contents, clean_content = parse_ai_response(full_response)
                    final_display = ""
                    for think in think_contents:
                        final_display += f'<p style="font-size: 0.8em; color: gray; font-style: italic;">💭 {think}</p>'
                    if clean_content:
                        final_display += f'<p style="font-weight: bold; font-size: 1em;">{clean_content}</p>'
                    message_placeholder.markdown(final_display, unsafe_allow_html=True)
                    
                    save_message("assistant", full_response)
                    long_term_memory.extract_and_store_memory(prompt, clean_content if clean_content else full_response)
            else:
                st.error(f"请求失败，状态码：{response.status_code}")
                
        except Exception as e:
            st.error(f"发生错误：{str(e)}")


def main() -> None:
    """主函数"""
    init_session_state()
    render_sidebar()
    render_chat_interface()


if __name__ == "__main__":
    main()