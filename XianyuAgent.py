import time
from typing import List, Dict
import os
from openai import OpenAI
from loguru import logger


class XianyuReplyBot:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("API_KEY"),
            base_url=os.getenv("MODEL_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        )
        self._init_system_prompts()
        self.agent = GetWechatAgent(self.client, self.get_wechat_prompt, self._safe_filter)

    def _init_system_prompts(self):
        """初始化提示词，优先加载用户自定义文件，否则使用 example 文件"""
        prompt_dir = "prompts"

        def load_prompt_content(name: str) -> str:
            target_path = os.path.join(prompt_dir, f"{name}.txt")
            if os.path.exists(target_path):
                file_path = target_path
            else:
                file_path = os.path.join(prompt_dir, f"{name}_example.txt")

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                logger.debug(f"已加载 {name} 提示词，路径: {file_path}, 长度: {len(content)} 字符")
                return content

        try:
            self.get_wechat_prompt = load_prompt_content("get_wechat_prompt")
            logger.info("成功加载提示词")
        except Exception as e:
            logger.error(f"加载提示词时出错: {e}")
            raise

    def _safe_filter(self, text: str) -> str:
        """安全过滤模块"""
        blocked_phrases = ["微信", "QQ", "支付宝", "银行卡", "线下"]
        return "[安全提醒]请通过平台沟通" if any(p in text for p in blocked_phrases) else text

    def format_history(self, context: List[Dict]) -> str:
        """格式化对话历史，返回完整的对话记录"""
        user_assistant_msgs = [msg for msg in context if msg['role'] in ['user', 'assistant']]
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in user_assistant_msgs])

    def generate_reply(self, user_msg: str, item_desc: str, context: List[Dict]) -> str:
        """生成回复主流程"""
        formatted_context = self.format_history(context)

        t_generate = time.perf_counter()
        reply = self.agent.generate(
            user_msg=user_msg,
            item_desc=item_desc,
            context=formatted_context,
        )
        generate_ms = (time.perf_counter() - t_generate) * 1000
        logger.info(f"回复生成耗时: {generate_ms:.0f}ms")
        return reply

    def reload_prompts(self):
        """重新加载所有提示词"""
        logger.info("正在重新加载提示词...")
        self._init_system_prompts()
        self.agent = GetWechatAgent(self.client, self.get_wechat_prompt, self._safe_filter)
        logger.info("提示词重新加载完成")


class BaseAgent:
    """Agent 基类"""

    def __init__(self, client, system_prompt, safety_filter):
        self.client = client
        self.system_prompt = system_prompt
        self.safety_filter = safety_filter

    def generate(self, user_msg: str, item_desc: str, context: str, **kwargs) -> str:
        messages = self._build_messages(user_msg, item_desc, context)
        response = self._call_llm(messages)
        return self.safety_filter(response)

    def _build_messages(self, user_msg: str, item_desc: str, context: str) -> List[Dict]:
        return [
            {"role": "system", "content": f"【商品信息】{item_desc}\n【你与客户对话历史】{context}\n{self.system_prompt}"},
            {"role": "user", "content": user_msg}
        ]

    def _call_llm(self, messages: List[Dict], temperature: float = 0.4) -> str:
        model = os.getenv("MODEL_NAME", "qwen-max")
        t0 = time.perf_counter()
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=500,
            top_p=0.8
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000
        logger.info(f"LLM调用 [{self.__class__.__name__}] model={model} 耗时: {elapsed_ms:.0f}ms")
        return response.choices[0].message.content


class GetWechatAgent(BaseAgent):
    """引导客户留联系方式的智能体"""
    pass
