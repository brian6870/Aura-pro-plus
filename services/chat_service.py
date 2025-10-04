import groq
from config import Config

class ChatService:
    def __init__(self):
        self.client = groq.Groq(api_key=Config.GROQ_API_KEY)
        self.conversation_history = {}
    
    def get_response(self, user_id, message):
        # Initialize or get conversation history for user
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = [
                {
                    "role": "system",
                    "content": """You are Aura, an environmental assistant focused on carbon footprint and sustainability. 
                    Help users understand:
                    - Carbon footprint calculation
                    - Sustainable product choices
                    - Environmental impact of ingredients
                    - Eco-friendly alternatives
                    - Climate change and sustainability topics
                    
                    Keep responses informative, practical, and encouraging. 
                    Suggest specific actions users can take to reduce their environmental impact."""
                }
            ]
        
        # Add user message to history
        self.conversation_history[user_id].append({
            "role": "user",
            "content": message
        })
        
        try:
            # Get AI response
            response = self.client.chat.completions.create(
                messages=self.conversation_history[user_id],
                model="llama-3.1-8b-instant",
                temperature=0.7,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            
            # Add AI response to history
            self.conversation_history[user_id].append({
                "role": "assistant",
                "content": ai_response
            })
            
            # Limit conversation history to last 10 messages
            if len(self.conversation_history[user_id]) > 10:
                self.conversation_history[user_id] = [
                    self.conversation_history[user_id][0]  # Keep system message
                ] + self.conversation_history[user_id][-9:]  # Keep last 9 exchanges
            
            return ai_response
            
        except Exception as e:
            return f"I'm having trouble responding right now. Please try again later. Error: {str(e)}"
    
    def clear_history(self, user_id):
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]

chat_service = ChatService()