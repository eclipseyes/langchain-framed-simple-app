import streamlit as st
from langchain.llms import OpenAI
import openai
from functools import lru_cache
import time

# 设置应用标题
st.title('🦜🔗 Quickstart App')

# 获取用户的 OpenAI API 密钥
openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password')

# 初始化会话状态以跟踪 API 调用次数
if 'api_calls' not in st.session_state:
    st.session_state['api_calls'] = 0
if 'last_reset' not in st.session_state:
    st.session_state['last_reset'] = time.time()

# 定义每小时最大 API 调用次数
MAX_API_CALLS_PER_HOUR = 10

# 缓存函数，用于缓存相同输入的响应
@st.cache_data(show_spinner=False)
def get_cached_response(input_text, api_key):
    llm = OpenAI(temperature=0.7, openai_api_key=api_key, max_tokens=150)  # 设置 max_tokens 以优化成本
    return llm(input_text)

# 生成响应的函数
def generate_response(input_text):
    response = get_cached_response(input_text, openai_api_key)
    st.info(response)

# 表单用于用户输入
with st.form('my_form'):
    text = st.text_area('Enter text:', 'What are the three key pieces of advice for learning how to code?')
    submitted = st.form_submit_button('Submit')

    # 验证 API 密钥格式
    if not openai_api_key.startswith('sk-'):
        st.warning('Please enter a valid OpenAI API key!', icon='⚠')

    # 处理用户提交
    if submitted and openai_api_key.startswith('sk-'):
        current_time = time.time()
        elapsed_time = current_time - st.session_state['last_reset']

        # 每小时重置一次调用次数
        if elapsed_time > 3600:
            st.session_state['api_calls'] = 0
            st.session_state['last_reset'] = current_time

        if st.session_state['api_calls'] < MAX_API_CALLS_PER_HOUR:
            try:
                generate_response(text)
                st.session_state['api_calls'] += 1
                st.success(f'API 调用次数：{st.session_state["api_calls"]}/{MAX_API_CALLS_PER_HOUR}')
            except openai.error.RateLimitError:
                st.error('抱歉，您已超出当前的 API 配额。请稍后再试或升级您的计划。')
            except Exception as e:
                st.error(f'发生错误：{e}')
        else:
            st.error('您已达到本小时的最大 API 调用次数，请稍后再试。')
