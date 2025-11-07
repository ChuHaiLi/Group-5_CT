"""
Task 6: Module Cảnh Báo Ngữ Cảnh và Tính Năng Đặc Biệt
Mô phỏng các tính năng đặc biệt và cảnh báo linh hoạt dựa trên điều kiện thời gian thực
"""

from datetime import datetime
from typing import Dict, List, Any
import json


class ContextAlertSystem:
    """Hệ thống cảnh báo và tính năng đặc biệt cho du lịch"""
    
    def __init__(self):
        # Ngưỡng để xác định Hot Trend
        self.HOT_TREND_THRESHOLD = {
            'min_rating': 4.5,
            'min_reviews': 100,
            'recent_growth': 0.2  # Tăng trưởng 20% review trong tháng gần đây
        }
        
        # Quy tắc cảnh báo thời tiết
        self.WEATHER_RULES = {
            'rain': {'indoor': True, 'message': '🌧️ Trời mưa - Ưu tiên hoạt động trong nhà'},
            'hot': {'message': '☀️ Trời nắng nóng - Nên mang nước và kem chống nắng'},
            'cold': {'message': '❄️ Trời lạnh - Mang áo ấm'},
            'storm': {'outdoor': False, 'message': '⛈️ Cảnh báo bão - Tránh hoạt động ngoài trời'}
        }
        
        # Quy tắc cảnh báo theo thời gian
        self.TIME_RULES = {
            'rush_hour': {'hours': [7, 8, 17, 18, 19], 'message': '🚗 Giờ cao điểm - Giao thông đông đúc'},
            'lunch_time': {'hours': [11, 12, 13], 'message': '🍽️ Giờ ăn trưa - Nhà hàng có thể đông'},
            'night_time': {'hours': [22, 23, 0, 1, 2, 3, 4, 5], 'message': '🌙 Tối muộn - Chú ý an toàn'}
        }
        
        # Quy tắc cảnh báo ngân sách
        self.BUDGET_RULES = {
            'overspend_warning': 0.8,  # Cảnh báo khi đã dùng 80% ngân sách
            'overspend_critical': 0.95  # Cảnh báo nghiêm trọng ở 95%
        }
    
    
    def check_hot_trend(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kiểm tra xem địa điểm có phải Hot Trend không
        
        Args:
            location: Thông tin địa điểm với rating, số review, growth_rate
            
        Returns:
            Dict chứa is_hot_trend và lý do
        """
        rating = location.get('rating', 0)
        total_reviews = location.get('total_reviews', 0)
        recent_growth = location.get('review_growth_rate', 0)
        
        is_hot = (
            rating >= self.HOT_TREND_THRESHOLD['min_rating'] and
            total_reviews >= self.HOT_TREND_THRESHOLD['min_reviews'] and
            recent_growth >= self.HOT_TREND_THRESHOLD['recent_growth']
        )
        
        reasons = []
        if rating >= self.HOT_TREND_THRESHOLD['min_rating']:
            reasons.append(f"Đánh giá cao ({rating}⭐)")
        if total_reviews >= self.HOT_TREND_THRESHOLD['min_reviews']:
            reasons.append(f"Nhiều lượt đánh giá ({total_reviews} reviews)")
        if recent_growth >= self.HOT_TREND_THRESHOLD['recent_growth']:
            reasons.append(f"Tăng trưởng nhanh (+{recent_growth*100:.0f}%)")
        
        return {
            'is_hot_trend': is_hot,
            'tag': '🔥 HOT TREND' if is_hot else '',
            'reasons': reasons if is_hot else []
        }
    
    
    def generate_weather_alerts(self, weather_condition: str, 
                                location_type: str) -> List[Dict[str, str]]:
        """
        Tạo cảnh báo dựa trên điều kiện thời tiết
        
        Args:
            weather_condition: 'rain', 'hot', 'cold', 'storm', 'clear'
            location_type: 'indoor', 'outdoor', 'both'
            
        Returns:
            Danh sách các cảnh báo
        """
        alerts = []
        
        if weather_condition in self.WEATHER_RULES:
            rule = self.WEATHER_RULES[weather_condition]
            
            # Cảnh báo chung
            alerts.append({
                'type': 'weather',
                'level': 'warning' if weather_condition in ['rain', 'storm'] else 'info',
                'message': rule['message']
            })
            
            # Cảnh báo đặc biệt cho địa điểm ngoài trời
            if location_type == 'outdoor':
                if rule.get('indoor'):
                    alerts.append({
                        'type': 'recommendation',
                        'level': 'warning',
                        'message': '⚠️ Địa điểm ngoài trời - Cân nhắc thay đổi kế hoạch'
                    })
                if rule.get('outdoor') == False:
                    alerts.append({
                        'type': 'recommendation',
                        'level': 'danger',
                        'message': '🚫 Không nên đi - Điều kiện thời tiết nguy hiểm'
                    })
        
        return alerts
    
    
    def generate_time_alerts(self, visit_time: datetime) -> List[Dict[str, str]]:
        """
        Tạo cảnh báo dựa trên thời gian trong ngày
        
        Args:
            visit_time: Thời gian dự kiến đến
            
        Returns:
            Danh sách các cảnh báo theo thời gian
        """
        alerts = []
        hour = visit_time.hour
        
        # Kiểm tra giờ cao điểm
        if hour in self.TIME_RULES['rush_hour']['hours']:
            alerts.append({
                'type': 'traffic',
                'level': 'info',
                'message': self.TIME_RULES['rush_hour']['message']
            })
        
        # Kiểm tra giờ ăn trưa
        if hour in self.TIME_RULES['lunch_time']['hours']:
            alerts.append({
                'type': 'crowd',
                'level': 'info',
                'message': self.TIME_RULES['lunch_time']['message']
            })
        
        # Kiểm tra giờ tối muộn
        if hour in self.TIME_RULES['night_time']['hours']:
            alerts.append({
                'type': 'safety',
                'level': 'warning',
                'message': self.TIME_RULES['night_time']['message']
            })
        
        return alerts
    
    
    def check_budget_status(self, spent: float, total_budget: float) -> Dict[str, Any]:
        """
        Kiểm tra tình trạng ngân sách và đưa ra cảnh báo
        
        Args:
            spent: Số tiền đã chi
            total_budget: Tổng ngân sách
            
        Returns:
            Dict chứa thông tin trạng thái ngân sách
        """
        if total_budget == 0:
            return {'status': 'unknown', 'alerts': []}
        
        ratio = spent / total_budget
        alerts = []
        
        if ratio >= self.BUDGET_RULES['overspend_critical']:
            alerts.append({
                'type': 'budget',
                'level': 'danger',
                'message': f'💸 CẢNH BÁO: Đã chi {ratio*100:.1f}% ngân sách!'
            })
        elif ratio >= self.BUDGET_RULES['overspend_warning']:
            alerts.append({
                'type': 'budget',
                'level': 'warning',
                'message': f'⚠️ Chú ý: Đã chi {ratio*100:.1f}% ngân sách'
            })
        
        return {
            'spent': spent,
            'remaining': total_budget - spent,
            'percentage': ratio * 100,
            'status': 'critical' if ratio >= 0.95 else 'warning' if ratio >= 0.8 else 'good',
            'alerts': alerts
        }
    
    
    def generate_explainability_tags(self, location: Dict[str, Any], 
                                     user_preferences: Dict[str, Any],
                                     score_breakdown: Dict[str, float]) -> List[str]:
        """
        Tạo các thẻ giải thích tại sao địa điểm này được khuyến nghị
        
        Args:
            location: Thông tin địa điểm
            user_preferences: Sở thích người dùng
            score_breakdown: Chi tiết điểm số từng tiêu chí
            
        Returns:
            Danh sách các thẻ giải thích
        """
        tags = []
        
        # Giải thích về sở thích
        location_tags = set(location.get('tags', []))
        user_tags = set(user_preferences.get('interests', []))
        matched_interests = location_tags & user_tags
        
        if matched_interests:
            tags.append(f"✓ Khớp sở thích: {', '.join(list(matched_interests)[:2])}")
        
        # Giải thích về rating
        if location.get('rating', 0) >= 4.5:
            tags.append(f"⭐ Đánh giá xuất sắc ({location['rating']}/5)")
        
        # Giải thích về khoảng cách
        if score_breakdown.get('distance_score', 0) > 0.7:
            tags.append("📍 Vị trí thuận tiện")
        
        # Giải thích về giá
        if score_breakdown.get('price_score', 0) > 0.7:
            tags.append("💰 Phù hợp ngân sách")
        
        # Giải thích về xu hướng
        hot_trend = self.check_hot_trend(location)
        if hot_trend['is_hot_trend']:
            tags.append("🔥 Đang thịnh hành")
        
        # Giải thích về thời gian
        if location.get('suitable_time') == user_preferences.get('travel_time'):
            tags.append("⏰ Thời gian phù hợp")
        
        return tags
    
    
    def generate_comprehensive_report(self, location: Dict[str, Any],
                                     user_data: Dict[str, Any],
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tạo báo cáo tổng hợp cho một địa điểm với đầy đủ cảnh báo và giải thích
        
        Args:
            location: Thông tin địa điểm
            user_data: Dữ liệu người dùng (preferences, budget)
            context: Ngữ cảnh (weather, time, current_spending)
            
        Returns:
            Báo cáo tổng hợp
        """
        report = {
            'location_name': location.get('name'),
            'location_type': location.get('type'),
            'alerts': [],
            'tags': [],
            'hot_trend': {},
            'budget_status': {},
            'recommendations': []
        }
        
        # 1. Kiểm tra Hot Trend
        report['hot_trend'] = self.check_hot_trend(location)
        
        # 2. Cảnh báo thời tiết
        if 'weather' in context:
            weather_alerts = self.generate_weather_alerts(
                context['weather'],
                location.get('environment_type', 'both')
            )
            report['alerts'].extend(weather_alerts)
        
        # 3. Cảnh báo thời gian
        if 'visit_time' in context:
            time_alerts = self.generate_time_alerts(context['visit_time'])
            report['alerts'].extend(time_alerts)
        
        # 4. Kiểm tra ngân sách
        if 'current_spending' in context and 'total_budget' in user_data:
            estimated_cost = location.get('estimated_cost', 0)
            new_spending = context['current_spending'] + estimated_cost
            budget_status = self.check_budget_status(
                new_spending,
                user_data['total_budget']
            )
            report['budget_status'] = budget_status
            report['alerts'].extend(budget_status['alerts'])
        
        # 5. Tạo thẻ giải thích
        score_breakdown = context.get('score_breakdown', {})
        explainability_tags = self.generate_explainability_tags(
            location,
            user_data.get('preferences', {}),
            score_breakdown
        )
        report['tags'] = explainability_tags
        
        # 6. Tổng hợp khuyến nghị
        if not any(alert['level'] == 'danger' for alert in report['alerts']):
            report['recommendations'].append("✅ Địa điểm phù hợp để ghé thăm")
        else:
            report['recommendations'].append("⚠️ Cân nhắc kỹ trước khi ghé thăm")
        
        return report


# ========== DEMO VÀ TEST ==========
def demo_context_alert_system():
    """Demo hệ thống cảnh báo ngữ cảnh"""
    
    system = ContextAlertSystem()
    
    # Dữ liệu mẫu địa điểm
    sample_location = {
        'name': 'Bảo tàng Lịch sử TP.HCM',
        'type': 'museum',
        'environment_type': 'indoor',
        'rating': 4.6,
        'total_reviews': 250,
        'review_growth_rate': 0.25,
        'estimated_cost': 50000,
        'tags': ['history', 'culture', 'education'],
        'suitable_time': 'morning'
    }
    
    # Dữ liệu người dùng
    user_data = {
        'preferences': {
            'interests': ['history', 'culture', 'food'],
            'travel_time': 'morning'
        },
        'total_budget': 500000
    }
    
    # Ngữ cảnh hiện tại
    context = {
        'weather': 'rain',
        'visit_time': datetime(2025, 11, 5, 8, 30),  # 8:30 sáng
        'current_spending': 350000,
        'score_breakdown': {
            'preference_score': 0.85,
            'distance_score': 0.75,
            'price_score': 0.80,
            'rating_score': 0.92
        }
    }
    
    # Tạo báo cáo tổng hợp
    print("=" * 60)
    print("BÁO CÁO CẢNH BÁO NGỮ CẢNH VÀ TÍNH NĂNG ĐẶC BIỆT")
    print("=" * 60)
    
    report = system.generate_comprehensive_report(
        sample_location,
        user_data,
        context
    )
    
    print(f"\n📍 ĐỊA ĐIỂM: {report['location_name']}")
    print(f"   Loại: {report['location_type']}")
    
    # Hot Trend
    if report['hot_trend']['is_hot_trend']:
        print(f"\n{report['hot_trend']['tag']}")
        for reason in report['hot_trend']['reasons']:
            print(f"   • {reason}")
    
    # Cảnh báo
    if report['alerts']:
        print("\n⚠️ CẢNH BÁO:")
        for alert in report['alerts']:
            print(f"   {alert['message']}")
    
    # Trạng thái ngân sách
    if report['budget_status']:
        budget = report['budget_status']
        print(f"\n💰 NGÂN SÁCH:")
        print(f"   Đã chi: {budget['spent']:,.0f} VNĐ ({budget['percentage']:.1f}%)")
        print(f"   Còn lại: {budget['remaining']:,.0f} VNĐ")
    
    # Thẻ giải thích
    if report['tags']:
        print("\n🏷️ TẠI SAO KHUYẾN NGHỊ:")
        for tag in report['tags']:
            print(f"   {tag}")
    
    # Khuyến nghị
    print("\n💡 KHUYẾN NGHỊ:")
    for rec in report['recommendations']:
        print(f"   {rec}")
    
    print("\n" + "=" * 60)
    
    # Test thêm các trường hợp khác
    print("\n\nKIỂM TRA CÁC TÌNH HUỐNG KHÁC:")
    print("-" * 60)
    
    # Test 1: Địa điểm ngoài trời + Bão
    print("\n1. Địa điểm ngoài trời khi có bão:")
    outdoor_location = sample_location.copy()
    outdoor_location['environment_type'] = 'outdoor'
    outdoor_location['name'] = 'Công viên Tao Đàn'
    
    storm_context = context.copy()
    storm_context['weather'] = 'storm'
    
    storm_alerts = system.generate_weather_alerts('storm', 'outdoor')
    for alert in storm_alerts:
        print(f"   {alert['message']}")
    
    # Test 2: Giờ tối muộn
    print("\n2. Cảnh báo giờ tối muộn:")
    late_time = datetime(2025, 11, 5, 23, 0)
    late_alerts = system.generate_time_alerts(late_time)
    for alert in late_alerts:
        print(f"   {alert['message']}")
    
    # Test 3: Vượt ngân sách
    print("\n3. Cảnh báo ngân sách:")
    budget_test = system.check_budget_status(480000, 500000)
    print(f"   Đã chi: {budget_test['percentage']:.1f}%")
    for alert in budget_test['alerts']:
        print(f"   {alert['message']}")
    
    print("\n" + "=" * 60)
    print("HOÀN THÀNH DEMO TASK 6")
    print("=" * 60)


if __name__ == "__main__":
    demo_context_alert_system()