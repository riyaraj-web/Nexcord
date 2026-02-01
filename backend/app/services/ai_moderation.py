from openai import AsyncOpenAI
from app.core.config import settings

class AIModerationService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
    
    async def moderate_content(self, content: str) -> dict:
        if not self.client:
            return {"is_toxic": False, "categories": {}, "scores": {}}
        
        try:
            response = await self.client.moderations.create(input=content)
            result = response.results[0]
            
            return {
                "is_toxic": result.flagged,
                "categories": {
                    "hate": result.categories.hate,
                    "harassment": result.categories.harassment,
                    "sexual": result.categories.sexual,
                    "violence": result.categories.violence,
                    "self_harm": result.categories.self_harm
                },
                "scores": {
                    "hate": result.category_scores.hate,
                    "harassment": result.category_scores.harassment,
                    "sexual": result.category_scores.sexual,
                    "violence": result.category_scores.violence,
                    "self_harm": result.category_scores.self_harm
                }
            }
        except Exception as e:
            print(f"AI Moderation error: {e}")
            return {"is_toxic": False, "categories": {}, "scores": {}}
    
    async def ai_chatbot_response(self, message: str, context: list = None) -> str:
        if not self.client:
            return "AI chatbot is not configured."
        
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant in a chat application. Be concise and friendly."}
            ]
            if context:
                messages.extend(context)
            messages.append({"role": "user", "content": message})
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"AI Chatbot error: {e}")
            return "Sorry, I'm having trouble responding right now."
