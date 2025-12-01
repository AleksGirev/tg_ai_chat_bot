"""
Клиент для работы с публичной LLM API
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class LLMClient:
    """Клиент для взаимодействия с LLM API"""
    
    def __init__(self):
        """Инициализация клиента с настройками из переменных окружения"""
        self.api_key = os.getenv("LLM_API_KEY")
        self.api_url = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
        self.model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        
        if not self.api_key:
            logger.warning(
                "LLM_API_KEY не установлен. "
                "Бот будет работать в режиме заглушки."
            )
    
    async def get_response(self, user_message: str) -> str:
        """
        Получить ответ от LLM на сообщение пользователя
        
        Args:
            user_message: Сообщение от пользователя
            
        Returns:
            Ответ от LLM
        """
        if not self.api_key:
            return (
                "Извините, LLM API не настроен. "
                "Пожалуйста, установите переменную окружения LLM_API_KEY."
            )
        
        try:
            if self.provider == "openai":
                return await self._get_openai_response(user_message)
            elif self.provider == "anthropic":
                return await self._get_anthropic_response(user_message)
            elif self.provider == "custom":
                return await self._get_custom_response(user_message)
            else:
                return await self._get_openai_response(user_message)
        except Exception as e:
            logger.error(f"Ошибка при запросе к LLM: {e}")
            raise
    
    async def _get_openai_response(self, user_message: str) -> str:
        """Получить ответ от OpenAI API"""
        import aiohttp
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Ты полезный ассистент, который отвечает на вопросы пользователей."},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    raise Exception(f"Ошибка API: {response.status} - {error_text}")
    
    async def _get_anthropic_response(self, user_message: str) -> str:
        """Получить ответ от Anthropic (Claude) API"""
        import aiohttp
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "max_tokens": 1000,
            "messages": [
                {"role": "user", "content": user_message}
            ]
        }
        
        api_url = "https://api.anthropic.com/v1/messages"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["content"][0]["text"]
                else:
                    error_text = await response.text()
                    raise Exception(f"Ошибка API: {response.status} - {error_text}")
    
    async def _get_custom_response(self, user_message: str) -> str:
        """Получить ответ от кастомного API"""
        import aiohttp
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Настройте структуру запроса под ваш API
        data = {
            "message": user_message,
            "model": self.model
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    # Настройте путь к ответу под структуру вашего API
                    return result.get("response", result.get("text", str(result)))
                else:
                    error_text = await response.text()
                    raise Exception(f"Ошибка API: {response.status} - {error_text}")

