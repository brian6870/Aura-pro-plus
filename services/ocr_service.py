import requests
import time
import pytesseract
from PIL import Image
import io
import cv2
import numpy as np
from config import Config

class OCRService:
    def __init__(self):
        # Get API key from environment variables via Config with proper error handling
        self.api_key = getattr(Config, 'OCR_SPACE_API_KEY', None)
        self.endpoint = 'https://api.ocr.space/parse/image'
        self.last_request_time = 0
        self.min_interval = 1  # 1 second between requests
        self.request_count = 0
        self.daily_limit = 25000  # OCR.Space free tier limit
        
        # Tesseract OCR fallback
        self.tesseract_available = self._check_tesseract()
        
        print(f"🔑 OCR Service initialized with API key: {self.api_key[:8] if self.api_key else 'NOT SET'}...")
        if self.tesseract_available:
            print("🔤 Tesseract OCR fallback available")
        
    def _check_tesseract(self):
        """Check if Tesseract OCR is properly installed"""
        try:
            # Get Tesseract version
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract OCR initialized: {version}")
            return True
        except Exception as e:
            print(f"❌ Tesseract not found: {e}")
            print("💡 Please install Tesseract OCR:")
            print("   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
            print("   macOS: brew install tesseract")
            print("   Linux: sudo apt install tesseract-ocr")
            return False
    
    def _tesseract_fallback(self, image_file):
        """Fallback OCR using Tesseract OCR"""
        if not self.tesseract_available:
            return {
                'success': False,
                'error': 'Tesseract OCR fallback not available',
                'text': None
            }
        
        try:
            print("🔄 Trying Tesseract OCR fallback...")
            
            # Read and process image
            image_data = image_file.read()
            
            # Convert to numpy array for OpenCV processing
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {
                    'success': False,
                    'error': 'Unable to read image file',
                    'text': None
                }
            
            print(f"📷 Image loaded: {image.shape[1]}x{image.shape[0]}")
            
            # Preprocess image for better OCR results
            processed_image = self._preprocess_image(image)
            
            # Perform OCR with different configurations
            extracted_text = self._extract_text_with_tesseract(processed_image)
            
            # Clean and validate the extracted text
            cleaned_text = self._clean_text(extracted_text)
            
            if cleaned_text and cleaned_text != "No text detected in image.":
                print(f"✅ Tesseract OCR successful! Extracted {len(cleaned_text)} characters")
                print(f"📋 Preview: {cleaned_text[:100]}...")
                return {
                    'success': True,
                    'text': cleaned_text,
                    'source': 'tesseract'
                }
            else:
                print("❌ No text extracted with Tesseract OCR")
                return {
                    'success': False,
                    'error': 'No text could be detected in the image with Tesseract OCR',
                    'text': None
                }
                
        except Exception as e:
            error_msg = f"Tesseract OCR error: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'text': None
            }
    
    def _preprocess_image(self, image):
        """Preprocess image to improve Tesseract OCR accuracy"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply different preprocessing techniques
            techniques = [
                self._basic_preprocessing,
                self._advanced_preprocessing,
                self._adaptive_threshold
            ]
            
            best_text = ""
            best_image = gray
            
            # Try different preprocessing techniques and keep the best one
            for technique in techniques:
                try:
                    processed = technique(gray.copy())
                    text = pytesseract.image_to_string(processed, config='--psm 6')
                    if len(text.strip()) > len(best_text):
                        best_text = text.strip()
                        best_image = processed
                except Exception as e:
                    print(f"⚠️ Preprocessing technique failed: {e}")
                    continue
            
            return best_image
            
        except Exception as e:
            print(f"⚠️ Image preprocessing failed, using original: {e}")
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def _basic_preprocessing(self, gray):
        """Basic preprocessing: noise removal and thresholding"""
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply Otsu's thresholding
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh
    
    def _advanced_preprocessing(self, gray):
        """Advanced preprocessing for difficult images"""
        # Apply median blur to preserve edges while removing noise
        blurred = cv2.medianBlur(gray, 3)
        
        # Apply morphological operations to clean up the image
        kernel = np.ones((2, 2), np.uint8)
        morphed = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel)
        
        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(morphed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        return thresh
    
    def _adaptive_threshold(self, gray):
        """Adaptive thresholding for varying lighting conditions"""
        return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    
    def _extract_text_with_tesseract(self, image):
        """Extract text using multiple Tesseract configurations"""
        configurations = [
            '--psm 6',  # Uniform block of text
            '--psm 4',  # Single column of text
            '--psm 8',  # Single word
            '--psm 13', # Raw line
            '--psm 11', # Sparse text
        ]
        
        all_text = []
        
        for config in configurations:
            try:
                text = pytesseract.image_to_string(image, config=config)
                if text.strip():
                    all_text.append(text.strip())
            except Exception as e:
                print(f"⚠️ Tesseract config {config} failed: {e}")
                continue
        
        # Also try with English language specifically
        try:
            text_eng = pytesseract.image_to_string(image, config='--psm 6 -l eng')
            if text_eng.strip():
                all_text.append(text_eng.strip())
        except:
            pass
        
        # Combine all results, remove duplicates while preserving order
        seen = set()
        unique_text = []
        for text in all_text:
            if text not in seen:
                seen.add(text)
                unique_text.append(text)
        
        return '\n'.join(unique_text)
    
    def _clean_text(self, text):
        """Clean and format extracted text"""
        if not text:
            return "No text detected in image."
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Split into lines and clean each line
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) > 2:  # Only keep lines with meaningful content
                cleaned_lines.append(line)
        
        # Join back with proper spacing
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Final cleanup
        cleaned_text = cleaned_text.strip()
        
        return cleaned_text if cleaned_text else "No text detected in image."
    
    def _ocr_space_primary(self, image_file):
        """Primary OCR using OCR.Space API"""
        # Check if API key is available
        if not self.api_key:
            print("❌ OCR.Space API key not configured")
            return {
                'success': False,
                'error': 'OCR.Space API key not configured',
                'text': None
            }
        
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
                            'source': 'ocr.space'
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
    
    def process_image(self, image_file):
        """Process image using OCR.Space API with Tesseract OCR fallback"""
        # Reset file pointer to beginning
        image_file.seek(0)
        
        # Try OCR.Space first (if API key is available)
        if self.api_key:
            print("🔄 Attempting OCR.Space...")
            result = self._ocr_space_primary(image_file)
            
            if result['success']:
                return result
        else:
            print("🔄 OCR.Space API key not available, skipping to Tesseract...")
            result = {'success': False, 'error': 'API key not configured'}
        
        # If OCR.Space fails or is not available, try Tesseract OCR fallback
        print("🔄 Using Tesseract OCR fallback...")
        image_file.seek(0)  # Reset file pointer again
        fallback_result = self._tesseract_fallback(image_file)
        
        if fallback_result['success']:
            return fallback_result
        
        # Both methods failed
        print("❌ All OCR methods failed")
        return {
            'success': False,
            'error': 'All OCR methods failed. ' + 
                    (result.get('error', '') or fallback_result.get('error', '')),
            'text': None
        }

ocr_service = OCRService()