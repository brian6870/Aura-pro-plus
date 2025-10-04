import groq
import json
import re
from config import Config

class GroqClient:
    def __init__(self):
        try:
            self.client = groq.Groq(api_key=Config.GROQ_API_KEY)
            print("✅ Groq client initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Groq client: {e}")
            self.client = None
    
    def analyze_ingredients(self, product_name, ingredients_text):
        if not self.client:
            return self._get_fallback_response("Groq client not initialized")
        
        # Clean and prepare the inputs
        product_name = (product_name or "").strip()
        ingredients_text = ingredients_text.strip()
        
        if not ingredients_text:
            return self._get_fallback_response("No ingredients provided")
        
        prompt = f"""Analyze this product for environmental impact and carbon footprint. 

Product Name: {product_name}
Ingredients: {ingredients_text}

First, identify the main product type from the name and ingredients. Then analyze for environmental impact considering factors like resource consumption, manufacturing process, biodegradability, toxicity, and overall sustainability.

Return your analysis as a valid JSON object with exactly these fields:
- "detected_product_name": the main product name you identified (use the provided name if clear, otherwise infer from ingredients)
- "rating": one of "friendly", "moderate", "harmful", "hazardous"
- "points": a number between 0-100
- "analysis": detailed explanation of environmental impact, mentioning the product name naturally in the analysis
- "alternatives": suggestions for more eco-friendly alternatives AS A PLAIN TEXT STRING

IMPORTANT: 
- The "analysis" field should naturally incorporate the product name in the explanation
- The "alternatives" field must be a plain text string, NOT a dictionary or list
- Use the provided product name when relevant in your analysis

Rating guidelines:
- "friendly": Minimal environmental impact, sustainable ingredients (80-100 points)
- "moderate": Some concerning ingredients but overall acceptable (40-79 points) 
- "harmful": Significant environmental concerns (10-39 points)
- "hazardous": Severe environmental impact, highly unsustainable (0-9 points)

Return ONLY the JSON object, no additional text or formatting."""
        
        try:
            print(f"🔍 Analyzing product: '{product_name}' with {len(ingredients_text)} chars of ingredients")
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an environmental scientist analyzing products. Always return valid JSON with product name detection and natural language analysis that includes the product name."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                model="llama-3.1-8b-instant",
                temperature=0.1,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content.strip()
            print(f"📨 Raw API response: {result_text}")
            
            # Parse JSON response
            try:
                result_data = json.loads(result_text)
                
                # Validate required fields
                required_fields = ['detected_product_name', 'rating', 'points', 'analysis', 'alternatives']
                if all(field in result_data for field in required_fields):
                    
                    # Validate rating value
                    valid_ratings = ['friendly', 'moderate', 'harmful', 'hazardous']
                    if result_data['rating'] not in valid_ratings:
                        result_data['rating'] = 'moderate'
                    
                    # Validate points range
                    try:
                        points = int(result_data['points'])
                        result_data['points'] = max(0, min(100, points))
                    except (ValueError, TypeError):
                        result_data['points'] = 50
                    
                    # Use provided product name if detected name is generic
                    detected_name = result_data['detected_product_name']
                    if (not detected_name or 
                        detected_name.lower() in ['product', 'item', 'unknown', 'unidentified'] or
                        (product_name and len(product_name) > len(detected_name))):
                        result_data['detected_product_name'] = product_name or detected_name
                    
                    # ENSURE alternatives is a string, not a dictionary or list
                    if isinstance(result_data['alternatives'], (dict, list)):
                        # Convert dictionary/list to readable string
                        if isinstance(result_data['alternatives'], dict):
                            alternatives_text = ""
                            for category, items in result_data['alternatives'].items():
                                if isinstance(items, list):
                                    alternatives_text += f"{category}: {', '.join(items)}. "
                                else:
                                    alternatives_text += f"{category}: {items}. "
                            result_data['alternatives'] = alternatives_text.strip()
                        elif isinstance(result_data['alternatives'], list):
                            result_data['alternatives'] = ". ".join([str(item) for item in result_data['alternatives']])
                    elif not isinstance(result_data['alternatives'], str):
                        # Convert any other type to string
                        result_data['alternatives'] = str(result_data['alternatives'])
                    
                    # Ensure analysis is also a string
                    if not isinstance(result_data['analysis'], str):
                        result_data['analysis'] = str(result_data['analysis'])
                    
                    print(f"✅ Analysis successful: {result_data['detected_product_name']} - {result_data['rating']} ({result_data['points']} points)")
                    return result_data
                else:
                    print(f"❌ Missing fields in response. Found: {list(result_data.keys())}")
                    return self._get_fallback_response("Invalid response format from API", product_name)
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"❌ Response was: {result_text}")
                return self._get_fallback_response("Failed to parse API response", product_name)
            
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            return self._get_fallback_response(f"API error: {str(e)}", product_name)
    
    def chat_response(self, message):
        """Method used by chatbot - simpler prompt, no JSON requirement"""
        if not self.client:
            return "I'm having trouble connecting right now. Please try again later."
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are Aura, an environmental assistant focused on carbon footprint and sustainability. Help users understand carbon footprint calculation, sustainable product choices, environmental impact of ingredients, and eco-friendly alternatives. Keep responses informative, practical, and encouraging."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                model="llama-3.1-8b-instant",
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Chat API error: {e}")
            return "I'm having trouble responding right now. Please try again later."
    
    def _get_fallback_response(self, reason="", product_name=""):
        """Return a fallback response when analysis fails"""
        print(f"🔄 Using fallback response. Reason: {reason}")
        product_ref = f" for {product_name}" if product_name else ""
        
        return {
            "detected_product_name": product_name or "Product",
            "rating": "moderate",
            "points": 50,
            "analysis": f"Unable to complete analysis{product_ref} at this time. {reason} Please try again in a moment. For now, consider products with natural, biodegradable ingredients and minimal synthetic chemicals.",
            "alternatives": "Look for products with certified organic ingredients, minimal packaging, and clear sustainability certifications. Consider DIY alternatives using natural ingredients."
        }

# Global instance
groq_client = GroqClient()