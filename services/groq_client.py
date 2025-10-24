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
    
    def analyze_ingredients(self, ingredients_text, product_name=None):
        """Analyze product ingredients - focuses ONLY on ingredients, not packaging"""
        if not self.client:
            return self._get_fallback_response("Groq client not initialized")
        
        # Clean and prepare the ingredients text
        ingredients_text = ingredients_text.strip()
        if not ingredients_text:
            return self._get_fallback_response("No ingredients provided")
        
        prompt = f"""
        Analyze these product ingredients for environmental impact and carbon footprint. 
        Focus ONLY on the chemical/environmental impact of the ingredients themselves.
        
        IMPORTANT: IGNORE any packaging materials, containers, or external factors. 
        Only analyze the environmental impact of the actual ingredients listed.
        
        Ingredients: {ingredients_text}
        
        Consider these factors for the INGREDIENTS ONLY:
        - Biodegradability and environmental persistence
        - Toxicity to ecosystems and wildlife
        - Resource consumption and sustainability
        - Manufacturing environmental impact
        - Water pollution potential
        - Soil impact and agricultural consequences
        - Bioaccumulation potential
        - Renewable vs synthetic sourcing
        
        Return your analysis as a valid JSON object with exactly these fields:
        - "rating": "friendly|moderate|harmful|hazardous"
        - "points": 0-100
        - "analysis": "Detailed explanation focusing ONLY on ingredient environmental impact"
        - "alternatives": "Suggestions for more eco-friendly ingredient alternatives"
        
        Rating guidelines (based on INGREDIENTS only):
        - "friendly": Natural, biodegradable, low environmental impact ingredients (80-100 points)
        - "moderate": Some synthetic ingredients but overall acceptable environmental profile (40-79 points)
        - "harmful": Significant synthetic chemicals, environmental concerns (10-39 points)
        - "hazardous": Highly toxic, persistent, severe environmental impact ingredients (0-9 points)
        
        Return ONLY the JSON object, no additional text or formatting.
        """
        
        try:
            print(f"🔍 Analyzing ingredients (ignoring packaging): {ingredients_text[:100]}...")
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an environmental scientist analyzing product ingredients. Focus ONLY on the environmental impact of the ingredients themselves, ignoring packaging and external factors. Always return valid JSON."
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
                required_fields = ['rating', 'points', 'analysis', 'alternatives']
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
                    
                    # Ensure alternatives is a string
                    if isinstance(result_data['alternatives'], (dict, list)):
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
                        result_data['alternatives'] = str(result_data['alternatives'])
                    
                    # Ensure analysis is also a string
                    if not isinstance(result_data['analysis'], str):
                        result_data['analysis'] = str(result_data['analysis'])
                    
                    print(f"✅ Ingredients analysis successful: {result_data['rating']} ({result_data['points']} points)")
                    return result_data
                else:
                    print(f"❌ Missing fields in response. Found: {list(result_data.keys())}")
                    return self._get_fallback_response("Invalid response format from API")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"❌ Response was: {result_text}")
                return self._get_fallback_response("Failed to parse API response")
            
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            return self._get_fallback_response(f"API error: {str(e)}")
    
    def analyze_plastic_material(self, plastic_type, description):
        """Specialized analysis for plastic materials"""
        if not self.client:
            return self._get_fallback_response("Groq client not initialized")
        
        prompt = f"""
        Analyze the environmental impact of {plastic_type} plastic material.
        
        Description: {description}
        
        Focus specifically on the PLASTIC MATERIAL properties and environmental impact:
        
        1. **Material Production**: Resource consumption, energy use, emissions from manufacturing
        2. **Chemical Composition**: Toxicity, additives, environmental persistence, microplastic generation
        3. **Recyclability**: Recycling rates, process limitations, economic viability, circular economy potential
        4. **Decomposition**: Biodegradability, timeline, breakdown products, environmental persistence
        5. **Environmental Fate**: Ecosystem impact, wildlife toxicity, soil and water contamination
        6. **Carbon Footprint**: Total lifecycle emissions from production to disposal
        7. **Health Impacts**: Potential human health effects from exposure
        8. **Sustainability**: Renewable alternatives and circular economy potential
        
        Return as JSON with these exact fields:
        - "rating": "friendly|moderate|harmful|hazardous"
        - "points": 0-100
        - "analysis": "Detailed plastic material environmental analysis"
        - "alternatives": "Sustainable alternative materials"
        - "recycling_guidance": "Proper recycling instructions"
        - "carbon_footprint": "Carbon impact assessment"
        - "decomposition_time": "Environmental decomposition timeline"
        
        Rating guidelines for plastic materials:
        - "friendly": Highly recyclable, low environmental impact (PET, HDPE) - 80-100 points
        - "moderate": Moderate recyclability and environmental impact (PP) - 40-79 points
        - "harmful": Limited recyclability, significant environmental concerns (LDPE, PS) - 10-39 points
        - "hazardous": Very difficult to recycle, high toxicity/persistence (PVC) - 0-9 points
        
        Return ONLY the JSON object, no additional text or formatting.
        """
        
        try:
            print(f"🔍 Analyzing plastic material: {plastic_type}")
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a materials scientist specializing in plastic environmental impact. Analyze plastic materials specifically, not products or packaging. Focus on material properties, recyclability, and environmental persistence."
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
            print(f"📨 Plastic analysis response: {result_text}")
            
            # Parse JSON response
            try:
                result_data = json.loads(result_text)
                
                # Validate required fields for plastic analysis
                required_fields = ['rating', 'points', 'analysis', 'alternatives', 'recycling_guidance']
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
                    
                    # Ensure all text fields are strings
                    for field in ['analysis', 'alternatives', 'recycling_guidance', 'carbon_footprint', 'decomposition_time']:
                        if field in result_data and not isinstance(result_data[field], str):
                            result_data[field] = str(result_data[field])
                        elif field not in result_data:
                            result_data[field] = "Not specified"
                    
                    print(f"✅ Plastic analysis successful: {result_data['rating']} ({result_data['points']} points)")
                    return result_data
                else:
                    print(f"❌ Missing fields in plastic response. Found: {list(result_data.keys())}")
                    return self._get_plastic_fallback_response(plastic_type)
                    
            except json.JSONDecodeError as e:
                print(f"❌ Plastic JSON decode error: {e}")
                print(f"❌ Response was: {result_text}")
                return self._get_plastic_fallback_response(plastic_type)
            
        except Exception as e:
            print(f"❌ Plastic analysis error: {e}")
            return self._get_plastic_fallback_response(plastic_type)
    
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
    
    def _get_fallback_response(self, reason=""):
        """Return a fallback response when ingredients analysis fails"""
        print(f"🔄 Using fallback response. Reason: {reason}")
        return {
            "rating": "moderate",
            "points": 50,
            "analysis": f"Unable to complete ingredient analysis at this time. {reason} Please try again in a moment. For now, consider products with natural, biodegradable ingredients and minimal synthetic chemicals.",
            "alternatives": "Look for products with certified organic ingredients, minimal processing, and clear ingredient transparency. Consider DIY alternatives using natural ingredients."
        }
    
    def _get_plastic_fallback_response(self, plastic_type):
        """Return a plastic-specific fallback response"""
        print(f"🔄 Using plastic fallback response for: {plastic_type}")
        
        # Basic plastic type fallbacks
        plastic_fallbacks = {
            'PET': {
                'rating': 'friendly',
                'points': 80,
                'analysis': 'PET is highly recyclable and has relatively low environmental impact compared to other plastics.',
                'alternatives': 'Glass containers, aluminum cans, or reusable stainless steel bottles.',
                'recycling_guidance': 'Wash and place in recycling bin. Check local guidelines for specific requirements.',
                'carbon_footprint': 'Moderate carbon footprint due to recyclability',
                'decomposition_time': '450+ years in environment'
            },
            'HDPE': {
                'rating': 'friendly', 
                'points': 85,
                'analysis': 'HDPE is one of the most recyclable plastics with good environmental profile.',
                'alternatives': 'Glass, metal containers, or certified compostable materials.',
                'recycling_guidance': 'Accepted in most recycling programs. Rinse before recycling.',
                'carbon_footprint': 'Relatively low for plastic materials',
                'decomposition_time': '450+ years in environment'
            },
            'PP': {
                'rating': 'moderate',
                'points': 60,
                'analysis': 'PP has moderate recyclability and environmental impact.',
                'alternatives': 'Glass, stainless steel, or reusable silicone containers.',
                'recycling_guidance': 'Check local recycling guidelines as acceptance varies.',
                'carbon_footprint': 'Moderate carbon footprint',
                'decomposition_time': '20-30 years in environment'
            },
            'PS': {
                'rating': 'harmful',
                'points': 25,
                'analysis': 'PS (polystyrene) has limited recyclability and significant environmental concerns.',
                'alternatives': 'Paper-based packaging, molded pulp, or reusable containers.',
                'recycling_guidance': 'Rarely recycled. Check for specialized recycling facilities.',
                'carbon_footprint': 'High carbon footprint due to low recyclability',
                'decomposition_time': '500+ years in environment'
            },
            'PVC': {
                'rating': 'hazardous',
                'points': 15,
                'analysis': 'PVC is difficult to recycle and contains concerning additives.',
                'alternatives': 'PE or PP plastics, metal, or wood alternatives.',
                'recycling_guidance': 'Very limited recycling options. Often not accepted in curbside recycling.',
                'carbon_footprint': 'High carbon footprint with toxic byproducts',
                'decomposition_time': '450+ years in environment'
            }
        }
        
        fallback = plastic_fallbacks.get(plastic_type, {
            'rating': 'moderate',
            'points': 50,
            'analysis': f'General plastic material with standard environmental considerations.',
            'alternatives': 'Consider reusable, recyclable, or biodegradable alternatives.',
            'recycling_guidance': 'Check local recycling guidelines for proper disposal.',
            'carbon_footprint': 'Varies based on specific plastic type',
            'decomposition_time': '20-500+ years depending on conditions'
        })
        
        fallback['analysis'] += " (Note: This is a fallback analysis due to API unavailability)"
        return fallback

# Global instance
groq_client = GroqClient()