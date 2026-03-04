import logging
from typing import Optional
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)

class LLMapiClient:
    """LLM API客户端基类"""
    
    async def summarize(self, text: str, max_length: Optional[int] = None) -> Optional[dict]:
        """
        生成摘要
        
        Args:
            text: 输入文本
            max_length: 最大长度
        
        Returns:
            {summary_text, generation_time_ms, cost}
        """
        raise NotImplementedError


class BaiduWXY_SummarizeClient(LLMapiClient):
    """百度文心千帆API客户端"""
    
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
    
    async def get_access_token(self) -> str:
        """获取access_token"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
        
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    data = await resp.json()
                    self.access_token = data.get("access_token")
                    # Token有效期30天，提前5天刷新
                    expires_in = data.get("expires_in", 2592000)
                    from datetime import timedelta
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 432000)
                    logger.info("百度文心千帆 access_token 已更新")
                    return self.access_token
        except Exception as e:
            logger.error(f"获取百度access_token失败: {str(e)}")
            raise
    
    async def summarize(self, text: str, max_length: Optional[int] = None) -> Optional[dict]:
        """使用百度文心千帆生成摘要"""
        try:
            access_token = await self.get_access_token()
            
            url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/text/summary"
            
            payload = {
                "prompt": f"请为以下文本生成简洁准确的摘要，长度约为原文的1/3:\n\n{text}",
                "temperature": 0.5,
                "top_p": 0.8,
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            start_time = datetime.now()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{url}?access_token={access_token}",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    data = await resp.json()
                    
                    generation_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    
                    if resp.status == 200 and "result" in data:
                        return {
                            "summary_text": data["result"]["summary"],
                            "generation_time_ms": generation_time,
                            "cost": data.get("usage", {}).get("total_tokens", 0),
                            "provider": "baidu"
                        }
                    else:
                        logger.error(f"百度API返回错误: {data}")
                        return None
        
        except Exception as e:
            logger.error(f"百度文心千帆摘要生成失败: {str(e)}")
            return None


class OpenAISummarizeClient(LLMapiClient):
    """OpenAI API客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def summarize(self, text: str, max_length: Optional[int] = None) -> Optional[dict]:
        """使用OpenAI生成摘要"""
        try:
            # 需要安装: pip install openai
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=self.api_key)
            
            start_time = datetime.now()
            
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的文本摘要助手。请为用户提供的文本生成简洁准确的摘要，长度为原文的1/3左右。"
                    },
                    {
                        "role": "user",
                        "content": f"请生成以下文本的摘要:\n\n{text}"
                    }
                ],
                temperature=0.5,
                max_tokens=max_length or 500
            )
            
            generation_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return {
                "summary_text": response.choices[0].message.content,
                "generation_time_ms": generation_time,
                "cost": response.usage.total_tokens if hasattr(response, 'usage') else 0,
                "provider": "openai"
            }
        
        except Exception as e:
            logger.error(f"OpenAI摘要生成失败: {str(e)}")
            return None


def create_summarizer(provider: str, **kwargs) -> LLMapiClient:
    """工厂函数，根据提供商创建摘要客户端"""
    if provider == "baidu":
        return BaiduWXY_SummarizeClient(
            api_key=kwargs.get("api_key"),
            secret_key=kwargs.get("secret_key")
        )
    elif provider == "openai":
        return OpenAISummarizeClient(
            api_key=kwargs.get("api_key")
        )
    else:
        raise ValueError(f"不支持的LLM供应商: {provider}")
