import requests
import time
from config import Config

class OCRService:
    def __init__(self):
        # OCR.Space free API key
        self.api_key = 'helloworld'  # Free tier API key
        self.endpoint = 'https://api.ocr.space/parse/image'
        self.last_request_time = 0
        self.min_interval = 1  # 1 second between requests
        self.request_count = 0
        self.daily_limit = 25000  # OCR.Space free tier limit
        
    def process_image(self, image_file):
        """Process image using OCR.Space API - Return dict with success/error"""
        try:
            # Rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                time.sleep(sleep_time)
            
            # Read image data
            image_data = image_file.read()
            file_size = len(image_data)
            
            print(f"📦 Processing OCR - Size: {file_size} bytes")
            
            # Prepare request payload
            payload = {
                'apikey': self.api_key,
                'language': 'eng',
                'isOverlayRequired': False,
                'OCREngine': 2,
                'scale': True,
                'detectOrientation': True,
            }
            
            files = {
                'image': ('ingredients.png', image_data, 'image/png')
            }
            
            print(f"🌐 Sending to OCR.Space... (Size: {file_size} bytes)")
            
            # Send request
            response = requests.post(
                self.endpoint, 
                files=files, 
                data=payload, 
                timeout=30
            )
            
            self.last_request_time = time.time()
            
            print(f"📰 OCR.Space response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for API errors
                if result.get('IsErroredOnProcessing'):
                    error_message = result.get('ErrorMessage', 'Unknown error from OCR.Space')
                    print(f"❌ OCR.Space API error: {error_message}")
                    return {
                        'success': False,
                        'error': error_message,
                        'text': None
                    }
                
                # Extract text from parsed results
                parsed_results = result.get('ParsedResults', [])
                if parsed_results:
                    extracted_text = parsed_results[0].get('ParsedText', '').strip()
                    
                    if extracted_text:
                        print(f"✅ OCR.Space successful! Extracted {len(extracted_text)} characters")
                        print(f"📋 Preview: {extracted_text[:100]}...")
                        return {
                            'success': True,
                            'text': extracted_text,
                            'error': None
                        }
                    else:
                        print("❌ No text extracted from image")
                        return {
                            'success': False,
                            'error': 'No text could be detected in the image',
                            'text': None
                        }
                else:
                    print("❌ No parsed results from OCR.Space")
                    return {
                        'success': False,
                        'error': 'OCR processing completed but no text was found',
                        'text': None
                    }
                    
            else:
                error_msg = f"HTTP error {response.status_code}"
                print(f"❌ OCR.Space {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'text': None
                }
                
        except requests.exceptions.Timeout:
            error_msg = "OCR request timed out"
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'text': None
            }
        except requests.exceptions.ConnectionError:
            error_msg = "Unable to connect to OCR service"
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'text': None
            }
        except Exception as e:
            error_msg = f"OCR processing error: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'text': None
            }

ocr_service = OCRService()