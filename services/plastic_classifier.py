import requests
import cv2
import numpy as np
from PIL import Image
import io
import json
from pathlib import Path
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RoboflowPlasticClassifier:
    def __init__(self):
        self.api_key = os.getenv("ROBOFLOW_API_KEY")
        self.model_id = "plastic-type-detector-uuyyr"
        self.version = "1"
        self.api_url = f"https://detect.roboflow.com/{self.model_id}/{self.version}"
        
        # Plastic type descriptions
        self.plastic_descriptions = {
            'PET': 'Polyethylene Terephthalate - Used in water bottles, food containers. Recyclable.',
            'HDPE': 'High-Density Polyethylene - Used in milk jugs, detergent bottles. Highly recyclable.',
            'PVC': 'Polyvinyl Chloride - Used in pipes, packaging. Difficult to recycle.',
            'LDPE': 'Low-Density Polyethylene - Used in plastic bags, squeeze bottles. Sometimes recyclable.',
            'PP': 'Polypropylene - Used in yogurt containers, bottle caps. Recyclable.',
            'PS': 'Polystyrene - Used in disposable cups, packaging foam. Rarely recyclable.',
            'OTHER': 'Other plastics - Mixed or unidentified plastic materials.'
        }
        
        self.confidence_threshold = 0.5
        
        print("✅ Roboflow Plastic Classifier initialized")
        print(f"🎯 Model: {self.model_id} (v{self.version})")
        print(f"🔗 API URL: {self.api_url}")
    
    def predict_plastic_type(self, image_file):
        """Predict plastic type using Roboflow API via HTTP requests"""
        try:
            # Read image data
            image_data = image_file.read()
            
            # Convert to numpy array for processing
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {"error": "Unable to read image"}
            
            print(f"📷 Image loaded: {image.shape[1]}x{image.shape[0]}")
            
            # Encode image to base64
            success, encoded_image = cv2.imencode('.jpg', image)
            if not success:
                return {"error": "Failed to encode image"}
            
            image_base64 = base64.b64encode(encoded_image).decode('utf-8')
            
            # Make API request
            print("🔍 Calling Roboflow API...")
            response = requests.post(
                self.api_url,
                params={
                    "api_key": self.api_key,
                    "confidence": self.confidence_threshold,
                    "format": "json"
                },
                data=image_base64,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                return {"error": f"API request failed with status {response.status_code}: {response.text}"}
            
            result = response.json()
            predictions = self.process_roboflow_result(result)
            
            if not predictions:
                return {"error": "No plastic types detected with sufficient confidence"}
            
            # Get the highest confidence prediction
            best_prediction = max(predictions, key=lambda x: x['confidence'])
            
            # Prepare response
            response_data = {
                "plastic_type": best_prediction['class'],
                "description": self.plastic_descriptions.get(
                    best_prediction['class'], 
                    f"{best_prediction['class']} plastic material"
                ),
                "confidence": round(best_prediction['confidence'] * 100, 2),
                "all_predictions": {
                    pred['class']: round(pred['confidence'] * 100, 2) 
                    for pred in predictions
                },
                "detection_count": len(predictions),
                "bounding_boxes": [
                    {
                        'class': pred['class'],
                        'confidence': round(pred['confidence'] * 100, 2),
                        'bbox': pred.get('bbox', {})
                    } for pred in predictions
                ]
            }
            
            print(f"🎯 Roboflow Prediction: {response_data['plastic_type']} ({response_data['confidence']}%)")
            print(f"📊 Detected {len(predictions)} plastic types")
            
            return response_data
            
        except Exception as e:
            print(f"❌ Roboflow inference error: {e}")
            return {"error": f"Inference failed: {str(e)}"}
    
    def process_roboflow_result(self, result):
        """Process Roboflow API response"""
        predictions = []
        
        try:
            if 'predictions' in result:
                predictions_data = result['predictions']
            else:
                predictions_data = result
            
            for prediction in predictions_data:
                confidence = prediction.get('confidence', 0)
                
                # Filter by confidence threshold
                if confidence >= self.confidence_threshold:
                    predictions.append({
                        'class': prediction.get('class', 'OTHER'),
                        'confidence': confidence,
                        'bbox': {
                            'x': prediction.get('x', 0),
                            'y': prediction.get('y', 0),
                            'width': prediction.get('width', 0),
                            'height': prediction.get('height', 0)
                        }
                    })
            
            # Sort by confidence
            predictions.sort(key=lambda x: x['confidence'], reverse=True)
            
        except Exception as e:
            print(f"❌ Error processing Roboflow result: {e}")
        
        return predictions
    
    def get_model_info(self):
        """Get model information"""
        return {
            "model_type": "Roboflow HTTP API",
            "model_id": self.model_id,
            "version": self.version,
            "provider": "Roboflow Direct API",
            "confidence_threshold": self.confidence_threshold,
            "plastic_types": list(self.plastic_descriptions.keys())
        }

# Global instance
plastic_classifier = RoboflowPlasticClassifier()