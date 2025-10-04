import requests
import time
from config import Config

class OCRService:
    def __init__(self):
        # OCR.Space free API key - "helloworld" is their demo key
        self.api_key = 'helloworld'  # Free tier API key
        self.endpoint = 'https://api.ocr.space/parse/image'
        self.last_request_time = 0
        self.min_interval = 1  # 1 second between requests (free tier limit)
        self.request_count = 0
        self.daily_limit = 25000  # OCR.Space free tier limit
        
    def process_image(self, image_file):
        """Process image using OCR.Space API"""
        try:
            # Rate limiting for free tier
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                print(f"⏳ Rate limiting: waiting {sleep_time:.2f}s")
                time.sleep(sleep_time)
            
            # Check daily limit (approximate)
            self.request_count += 1
            if self.request_count > self.daily_limit:
                return "Daily OCR limit reached. Please try again tomorrow."
            
            # Read image data
            image_data = image_file.read()
            file_size = len(image_data)
            
            print(f"🔍 Sending to OCR.Space... (Size: {file_size} bytes)")
            
            # Prepare request payload for OCR.Space
            payload = {
                'apikey': self.api_key,
                'language': 'eng',  # English language
                'isOverlayRequired': False,  # We don't need bounding boxes
                'OCREngine': 2,  # Engine 2 is more accurate
                'scale': True,  # Scale image for better OCR
                'isTable': False,  # Not a table
                'detectOrientation': True,  # Auto-rotate if needed
            }
            
            files = {
                'image': ('ingredients.png', image_data, 'image/png')
            }
            
            # Send request to OCR.Space
            response = requests.post(
                self.endpoint, 
                files=files, 
                data=payload, 
                timeout=30
            )
            
            self.last_request_time = time.time()
            
            print(f"📨 OCR.Space response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for API errors
                if result.get('IsErroredOnProcessing'):
                    error_message = result.get('ErrorMessage', 'Unknown error from OCR.Space')
                    error_details = result.get('ErrorDetails', '')
                    print(f"❌ OCR.Space API error: {error_message} - {error_details}")
                    
                    # Handle common errors
                    if 'limit' in error_message.lower():
                        return "OCR API limit reached. Please try again later."
                    elif 'size' in error_message.lower():
                        return "Image file too large. Please try a smaller image."
                    else:
                        return f"OCR processing failed: {error_message}"
                
                # Extract text from parsed results
                parsed_results = result.get('ParsedResults', [])
                if parsed_results:
                    extracted_text = parsed_results[0].get('ParsedText', '').strip()
                    
                    if extracted_text:
                        print(f"✅ OCR.Space successful! Extracted {len(extracted_text)} characters")
                        print(f"📝 Preview: {extracted_text[:100]}...")
                        return extracted_text
                    else:
                        print("❌ No text extracted from image")
                        return "No text could be detected in the image. Please ensure the image is clear and contains visible text."
                else:
                    print("❌ No parsed results from OCR.Space")
                    return "OCR processing completed but no text was found."
                    
            elif response.status_code == 403:
                print("❌ OCR.Space: API key invalid or blocked")
                return "OCR service temporarily unavailable. Please try again later."
            elif response.status_code == 429:
                print("❌ OCR.Space: Rate limit exceeded")
                return "OCR rate limit exceeded. Please wait a moment and try again."
            else:
                print(f"❌ OCR.Space HTTP error: {response.status_code} - {response.text}")
                return f"OCR service error (HTTP {response.status_code}). Please try again."
                
        except requests.exceptions.Timeout:
            print("❌ OCR.Space request timed out")
            return "OCR request timed out. Please try again."
        except requests.exceptions.ConnectionError:
            print("❌ OCR.Space connection error")
            return "Unable to connect to OCR service. Please check your internet connection."
        except Exception as e:
            print(f"❌ OCR.Space processing error: {e}")
            return f"OCR processing error: {str(e)}"

# Global instance
ocr_service = OCRService()