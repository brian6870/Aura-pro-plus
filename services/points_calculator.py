class PointsCalculator:
    @staticmethod
    def calculate_points(rating, base_points):
        """Calculate final points with potential bonuses/penalties"""
        rating_multipliers = {
            'friendly': 1.2,
            'moderate': 1.0,
            'harmful': 0.8,
            'hazardous': 0.5
        }
        
        multiplier = rating_multipliers.get(rating, 1.0)
        return max(0, min(100, int(base_points * multiplier)))
    
    @staticmethod
    def get_rating_color(rating):
        colors = {
            'friendly': 'success',
            'moderate': 'warning',
            'harmful': 'danger',
            'hazardous': 'dark'
        }
        return colors.get(rating, 'secondary')
    
    @staticmethod
    def get_rating_description(rating):
        descriptions = {
            'friendly': 'Environmentally Friendly - Minimal impact',
            'moderate': 'Moderate Impact - Some concerns',
            'harmful': 'Harmful - Significant environmental concerns',
            'hazardous': 'Hazardous - Severe environmental impact'
        }
        return descriptions.get(rating, 'Unknown rating')

points_calculator = PointsCalculator()