import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

def generate_points_chart(dates, points):
    plt.figure(figsize=(10, 6))
    plt.plot(dates, points, marker='o', linewidth=2, markersize=4)
    plt.title('Points Earned Over Time')
    plt.xlabel('Date')
    plt.ylabel('Points')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Convert to base64 for embedding in HTML
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=100)
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode('utf-8')

def generate_rating_distribution_chart(rating_data):
    ratings = [item[0] for item in rating_data]
    counts = [item[1] for item in rating_data]
    
    plt.figure(figsize=(8, 6))
    colors = ['#4CAF50', '#FFC107', '#FF9800', '#F44336']  # Green, Yellow, Orange, Red
    plt.bar(ratings, counts, color=colors[:len(ratings)])
    plt.title('Product Rating Distribution')
    plt.xlabel('Environmental Rating')
    plt.ylabel('Number of Products')
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=100)
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode('utf-8')