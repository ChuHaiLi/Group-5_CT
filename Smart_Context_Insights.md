# TASK 6: PHÁT TRIỂN CẢNH BÁO NGỮ CẢNH VÀ TÍNH NĂNG ĐẶC BIỆT

## 1. MỤC TIÊU

### Mục tiêu chính
Xây dựng hệ thống cảnh báo thông minh và tính năng giải thích để nâng cao trải nghiệm người dùng, giúp họ đưa ra quyết định du lịch tốt hơn dựa trên ngữ cảnh thời gian thực.

### Mục tiêu cụ thể
1. **Phát hiện Hot Trend**: Tự động nhận diện địa điểm đang thịnh hành dựa trên dữ liệu đánh giá
2. **Cảnh báo Ngữ cảnh**: Đưa ra cảnh báo linh hoạt dựa trên điều kiện thời tiết, thời gian, và ngân sách
3. **Giải thích Khuyến nghị**: Tạo các thẻ giải thích minh bạch về lý do đề xuất từng địa điểm
4. **Bảo vệ Người dùng**: Cảnh báo kịp thời các rủi ro tiềm ẩn (thời tiết xấu, vượt ngân sách, giờ không an toàn)

### Tầm quan trọng
- **UX Enhancement**: Tăng độ tin cậy và sự hài lòng của người dùng
- **Safety First**: Bảo vệ an toàn và tài chính cho du khách
- **Transparency**: Xây dựng lòng tin qua tính minh bạch trong thuật toán
- **Personalization**: Cá nhân hóa cảnh báo theo từng ngữ cảnh cụ thể

---

## 2. PHÂN TÍCH CHI TIẾT

### 2.1. Phân tích Bài toán

#### Vấn đề cần giải quyết
1. **Thiếu Ngữ cảnh**: Hệ thống đề xuất thông thường không xem xét điều kiện thời gian thực
2. **Hộp Đen (Black Box)**: Người dùng không hiểu tại sao địa điểm được đề xuất
3. **Rủi ro Tiềm ẩn**: Không cảnh báo về thời tiết xấu, ngân sách vượt, hoặc thời gian không phù hợp
4. **Thiếu Xu hướng**: Không nắm bắt được các địa điểm đang "hot" trong cộng đồng

#### Yêu cầu Chức năng
- **Real-time Adaptation**: Thích ứng với điều kiện thay đổi liên tục
- **Rule-based Logic**: Sử dụng IF-THEN để dễ kiểm soát và điều chỉnh
- **Multi-criteria Alert**: Cảnh báo đa tiêu chí (thời tiết, thời gian, ngân sách)
- **Explainable AI**: Giải thích rõ ràng mọi quyết định của hệ thống

### 2.2. Các Thành phần Chính

#### A. Hot Trend Detection System
**Chức năng**: Phát hiện địa điểm đang thịnh hành

**Tiêu chí Hot Trend**:
- Rating ≥ 4.5/5.0 (Chất lượng cao)
- Tổng reviews ≥ 100 (Độ tin cậy)
- Tăng trưởng review ≥ 20% trong tháng gần (Đang "lên ngôi")

**Giá trị**:
- Giúp người dùng khám phá điểm đến mới nổi
- Tạo FOMO (Fear Of Missing Out) tích cực
- Tăng độ "fresh" cho khuyến nghị

#### B. Weather Alert System
**Chức năng**: Cảnh báo dựa trên điều kiện thời tiết

**Các tình huống xử lý**:
1. **Mưa (Rain)**: 
   - Đề xuất chuyển sang hoạt động trong nhà
   - Cảnh báo cấp độ: Warning
   
2. **Nắng nóng (Hot)**: 
   - Nhắc nhở mang đồ bảo vệ
   - Cảnh báo cấp độ: Info
   
3. **Lạnh (Cold)**: 
   - Khuyến nghị mang áo ấm
   - Cảnh báo cấp độ: Info
   
4. **Bão (Storm)**: 
   - Tuyệt đối không hoạt động ngoài trời
   - Cảnh báo cấp độ: Danger

#### C. Time-based Alert System
**Chức năng**: Cảnh báo theo thời gian trong ngày

**Các khung giờ quan trọng**:
- **Giờ cao điểm** (7-8h, 17-19h): Cảnh báo giao thông
- **Giờ ăn trưa** (11-13h): Cảnh báo nhà hàng đông
- **Giờ tối muộn** (22h-5h): Cảnh báo an toàn

#### D. Budget Tracking System
**Chức năng**: Theo dõi và cảnh báo ngân sách

**Ngưỡng cảnh báo**:
- **80% ngân sách**: Warning - "Chú ý chi tiêu"
- **95% ngân sách**: Critical - "Sắp hết tiền!"

#### E. Explainability Tag System
**Chức năng**: Giải thích lý do khuyến nghị

**Các loại thẻ giải thích**:
- ✓ Khớp sở thích
- ⭐ Đánh giá cao
- 📍 Vị trí thuận tiện
- 💰 Phù hợp ngân sách
- 🔥 Đang thịnh hành
- ⏰ Thời gian phù hợp

---

## 3. ĐẦU VÀO (INPUT)

### 3.1. Dữ liệu Địa điểm
```json
{
  "name": "Bảo tàng Lịch sử TP.HCM",
  "type": "museum",
  "environment_type": "indoor",
  "rating": 4.6,
  "total_reviews": 250,
  "review_growth_rate": 0.25,
  "estimated_cost": 50000,
  "tags": ["history", "culture", "education"],
  "suitable_time": "morning",
  "coordinates": {"lat": 10.7769, "lng": 106.7009}
}
```

**Mô tả các trường**:
- `environment_type`: "indoor" | "outdoor" | "both"
- `review_growth_rate`: Tỷ lệ tăng trưởng review (0.25 = +25%)
- `suitable_time`: Thời gian phù hợp nhất để ghé thăm

### 3.2. Dữ liệu Người dùng
```json
{
  "preferences": {
    "interests": ["history", "culture", "food"],
    "travel_time": "morning",
    "travel_style": "relaxed"
  },
  "total_budget": 500000,
  "current_spending": 350000
}
```

### 3.3. Ngữ cảnh (Context)
```json
{
  "weather": "rain",
  "visit_time": "2025-11-05T08:30:00",
  "current_spending": 350000,
  "score_breakdown": {
    "preference_score": 0.85,
    "distance_score": 0.75,
    "price_score": 0.80,
    "rating_score": 0.92
  }
}
```

**Mô tả các trường**:
- `weather`: "rain" | "hot" | "cold" | "storm" | "clear"
- `visit_time`: Thời gian dự kiến đến (ISO format)
- `score_breakdown`: Điểm số chi tiết từ Task 3

---

## 4. ĐẦU RA (OUTPUT)

### 4.1. Báo cáo Tổng hợp
```json
{
  "location_name": "Bảo tàng Lịch sử TP.HCM",
  "location_type": "museum",
  
  "hot_trend": {
    "is_hot_trend": true,
    "tag": "🔥 HOT TREND",
    "reasons": [
      "Đánh giá cao (4.6⭐)",
      "Nhiều lượt đánh giá (250 reviews)",
      "Tăng trưởng nhanh (+25%)"
    ]
  },
  
  "alerts": [
    {
      "type": "weather",
      "level": "warning",
      "message": "🌧️ Trời mưa - Ưu tiên hoạt động trong nhà"
    },
    {
      "type": "traffic",
      "level": "info",
      "message": "🚗 Giờ cao điểm - Giao thông đông đúc"
    },
    {
      "type": "budget",
      "level": "warning",
      "message": "⚠️ Chú ý: Đã chi 80.0% ngân sách"
    }
  ],
  
  "budget_status": {
    "spent": 400000,
    "remaining": 100000,
    "percentage": 80.0,
    "status": "warning"
  },
  
  "tags": [
    "✓ Khớp sở thích: history, culture",
    "⭐ Đánh giá xuất sắc (4.6/5)",
    "📍 Vị trí thuận tiện",
    "💰 Phù hợp ngân sách",
    "🔥 Đang thịnh hành",
    "⏰ Thời gian phù hợp"
  ],
  
  "recommendations": [
    "✅ Địa điểm phù hợp để ghé thăm"
  ]
}
```

### 4.2. Các Level Cảnh báo
- **info**: Thông tin tham khảo (màu xanh)
- **warning**: Cần chú ý (màu vàng)
- **danger**: Nghiêm trọng, nên tránh (màu đỏ)

---

## 5. GIẢI THÍCH LOGIC (PSEUDOCODE)

### 5.1. Hot Trend Detection Algorithm

```
FUNCTION check_hot_trend(location):
    // Lấy thông tin địa điểm
    rating = location.rating
    total_reviews = location.total_reviews
    growth_rate = location.review_growth_rate
    
    // Định nghĩa ngưỡng
    MIN_RATING = 4.5
    MIN_REVIEWS = 100
    MIN_GROWTH = 0.20  // 20%
    
    // Kiểm tra điều kiện
    IF rating >= MIN_RATING AND 
       total_reviews >= MIN_REVIEWS AND 
       growth_rate >= MIN_GROWTH THEN
        
        // Thu thập lý do
        reasons = []
        IF rating >= MIN_RATING:
            ADD "Đánh giá cao ({rating}⭐)" TO reasons
        IF total_reviews >= MIN_REVIEWS:
            ADD "Nhiều lượt đánh giá ({total_reviews})" TO reasons
        IF growth_rate >= MIN_GROWTH:
            ADD "Tăng trưởng nhanh (+{growth_rate*100}%)" TO reasons
        
        RETURN {
            is_hot_trend: TRUE,
            tag: "🔥 HOT TREND",
            reasons: reasons
        }
    ELSE
        RETURN {
            is_hot_trend: FALSE,
            tag: "",
            reasons: []
        }
END FUNCTION
```

**Giải thích**:
1. Kiểm tra 3 điều kiện đồng thời (AND logic)
2. Nếu thỏa mãn cả 3 → Hot Trend
3. Thu thập lý do cụ thể để giải thích cho người dùng
4. Trả về kết quả có cấu trúc rõ ràng

---

### 5.2. Weather Alert Algorithm

```
FUNCTION generate_weather_alerts(weather_condition, location_type):
    alerts = []
    
    // Định nghĩa quy tắc thời tiết
    WEATHER_RULES = {
        'rain': {
            'indoor': TRUE,
            'message': '🌧️ Trời mưa - Ưu tiên hoạt động trong nhà',
            'level': 'warning'
        },
        'storm': {
            'outdoor': FALSE,
            'message': '⛈️ Cảnh báo bão - Tránh hoạt động ngoài trời',
            'level': 'danger'
        },
        'hot': {
            'message': '☀️ Trời nắng nóng - Nên mang nước',
            'level': 'info'
        },
        'cold': {
            'message': '❄️ Trời lạnh - Mang áo ấm',
            'level': 'info'
        }
    }
    
    // Kiểm tra điều kiện thời tiết
    IF weather_condition IN WEATHER_RULES THEN
        rule = WEATHER_RULES[weather_condition]
        
        // Cảnh báo chung
        ADD {
            type: 'weather',
            level: rule.level,
            message: rule.message
        } TO alerts
        
        // Cảnh báo đặc biệt cho outdoor
        IF location_type == 'outdoor' THEN
            IF rule.indoor == TRUE THEN
                ADD {
                    type: 'recommendation',
                    level: 'warning',
                    message: '⚠️ Địa điểm ngoài trời - Cân nhắc thay đổi'
                } TO alerts
            
            IF rule.outdoor == FALSE THEN
                ADD {
                    type: 'recommendation',
                    level: 'danger',
                    message: '🚫 Không nên đi - Nguy hiểm'
                } TO alerts
    
    RETURN alerts
END FUNCTION
```

**Giải thích**:
1. **Rule-based approach**: Mỗi điều kiện thời tiết có quy tắc riêng
2. **Layered warnings**: Cảnh báo chung + cảnh báo đặc biệt cho outdoor
3. **Level escalation**: Mưa (warning) → Bão (danger)
4. **Actionable advice**: Không chỉ cảnh báo mà còn gợi ý hành động

---

### 5.3. Time-based Alert Algorithm

```
FUNCTION generate_time_alerts(visit_time):
    alerts = []
    hour = EXTRACT_HOUR(visit_time)
    
    // Định nghĩa khung giờ
    RUSH_HOURS = [7, 8, 17, 18, 19]
    LUNCH_HOURS = [11, 12, 13]
    NIGHT_HOURS = [22, 23, 0, 1, 2, 3, 4, 5]
    
    // Kiểm tra giờ cao điểm
    IF hour IN RUSH_HOURS THEN
        ADD {
            type: 'traffic',
            level: 'info',
            message: '🚗 Giờ cao điểm - Giao thông đông đúc'
        } TO alerts
    
    // Kiểm tra giờ ăn trưa
    IF hour IN LUNCH_HOURS THEN
        ADD {
            type: 'crowd',
            level: 'info',
            message: '🍽️ Giờ ăn trưa - Nhà hàng có thể đông'
        } TO alerts
    
    // Kiểm tra giờ tối muộn
    IF hour IN NIGHT_HOURS THEN
        ADD {
            type: 'safety',
            level: 'warning',
            message: '🌙 Tối muộn - Chú ý an toàn'
        } TO alerts
    
    RETURN alerts
END FUNCTION
```

**Giải thích**:
1. **Temporal awareness**: Nhận biết thời gian trong ngày
2. **Pattern recognition**: Xác định các mẫu thời gian quan trọng
3. **Contextual advice**: Lời khuyên phù hợp từng khung giờ
4. **Safety-first**: Ưu tiên cảnh báo an toàn

---

### 5.4. Budget Tracking Algorithm

```
FUNCTION check_budget_status(spent, total_budget):
    IF total_budget == 0 THEN
        RETURN {status: 'unknown', alerts: []}
    
    // Tính tỷ lệ chi tiêu
    ratio = spent / total_budget
    alerts = []
    
    // Ngưỡng cảnh báo
    WARNING_THRESHOLD = 0.80   // 80%
    CRITICAL_THRESHOLD = 0.95  // 95%
    
    // Kiểm tra ngưỡng
    IF ratio >= CRITICAL_THRESHOLD THEN
        ADD {
            type: 'budget',
            level: 'danger',
            message: '💸 CẢNH BÁO: Đã chi {ratio*100}% ngân sách!'
        } TO alerts
        status = 'critical'
        
    ELSE IF ratio >= WARNING_THRESHOLD THEN
        ADD {
            type: 'budget',
            level: 'warning',
            message: '⚠️ Chú ý: Đã chi {ratio*100}% ngân sách'
        } TO alerts
        status = 'warning'
        
    ELSE
        status = 'good'
    
    RETURN {
        spent: spent,
        remaining: total_budget - spent,
        percentage: ratio * 100,
        status: status,
        alerts: alerts
    }
END FUNCTION
```

**Giải thích**:
1. **Progressive alerts**: Cảnh báo dần dần khi tiến gần ngưỡng
2. **Threshold-based**: Sử dụng 2 ngưỡng (80% và 95%)
3. **Visual feedback**: Emoji và màu sắc để tăng nhận thức
4. **Actionable info**: Hiển thị số tiền còn lại để người dùng quyết định

---

### 5.5. Explainability Tag Generation

```
FUNCTION generate_explainability_tags(location, user_prefs, score_breakdown):
    tags = []
    
    // 1. Kiểm tra sở thích khớp
    location_tags = SET(location.tags)
    user_interests = SET(user_prefs.interests)
    matched = location_tags INTERSECT user_interests
    
    IF matched IS NOT EMPTY THEN
        top_2 = TAKE_FIRST(matched, 2)
        ADD "✓ Khớp sở thích: {JOIN(top_2, ', ')}" TO tags
    
    // 2. Kiểm tra rating cao
    IF location.rating >= 4.5 THEN
        ADD "⭐ Đánh giá xuất sắc ({location.rating}/5)" TO tags
    
    // 3. Kiểm tra khoảng cách
    IF score_breakdown.distance_score > 0.7 THEN
        ADD "📍 Vị trí thuận tiện" TO tags
    
    // 4. Kiểm tra giá
    IF score_breakdown.price_score > 0.7 THEN
        ADD "💰 Phù hợp ngân sách" TO tags
    
    // 5. Kiểm tra hot trend
    hot_trend = check_hot_trend(location)
    IF hot_trend.is_hot_trend THEN
        ADD "🔥 Đang thịnh hành" TO tags
    
    // 6. Kiểm tra thời gian
    IF location.suitable_time == user_prefs.travel_time THEN
        ADD "⏰ Thời gian phù hợp" TO tags
    
    RETURN tags
END FUNCTION
```

**Giải thích**:
1. **Multi-criteria explanation**: Giải thích từ nhiều góc độ
2. **Set intersection**: Tìm điểm chung giữa sở thích và địa điểm
3. **Threshold-based**: Chỉ hiển thị điểm nổi bật (>0.7)
4. **User-centric**: Tập trung vào lý do quan trọng với người dùng
5. **Visual clarity**: Emoji giúp nhận diện nhanh

---

### 5.6. Comprehensive Report Generator (Main Logic)

```
FUNCTION generate_comprehensive_report(location, user_data, context):
    report = INITIALIZE_REPORT(location)
    
    // BƯỚC 1: Kiểm tra Hot Trend
    report.hot_trend = check_hot_trend(location)
    
    // BƯỚC 2: Cảnh báo Thời tiết
    IF 'weather' IN context THEN
        weather_alerts = generate_weather_alerts(
            context.weather,
            location.environment_type
        )
        APPEND weather_alerts TO report.alerts
    
    // BƯỚC 3: Cảnh báo Thời gian
    IF 'visit_time' IN context THEN
        time_alerts = generate_time_alerts(context.visit_time)
        APPEND time_alerts TO report.alerts
    
    // BƯỚC 4: Kiểm tra Ngân sách
    IF 'current_spending' IN context AND 'total_budget' IN user_data THEN
        estimated_cost = location.estimated_cost
        new_spending = context.current_spending + estimated_cost
        
        budget_status = check_budget_status(
            new_spending,
            user_data.total_budget
        )
        
        report.budget_status = budget_status
        APPEND budget_status.alerts TO report.alerts
    
    // BƯỚC 5: Tạo Thẻ giải thích
    tags = generate_explainability_tags(
        location,
        user_data.preferences,
        context.score_breakdown
    )
    report.tags = tags
    
    // BƯỚC 6: Tổng hợp Khuyến nghị
    danger_alerts = COUNT_ALERTS_BY_LEVEL(report.alerts, 'danger')
    
    IF danger_alerts == 0 THEN
        ADD "✅ Địa điểm phù hợp để ghé thăm" TO report.recommendations
    ELSE
        ADD "⚠️ Cân nhắc kỹ trước khi ghé thăm" TO report.recommendations
    
    RETURN report
END FUNCTION
```

**Giải thích Logic tổng hợp**:

1. **Modular Design**: Mỗi chức năng là một module độc lập
2. **Sequential Processing**: Xử lý tuần tự từng phần
3. **Accumulation**: Tích lũy alerts từ nhiều nguồn
4. **Final Decision**: Quyết định cuối dựa trên tất cả thông tin
5. **Fail-safe**: Kiểm tra tồn tại dữ liệu trước khi xử lý

**Flow tổng quát**:
```
Input → Hot Trend Check → Weather Alert → Time Alert 
     → Budget Check → Explainability Tags → Final Report
```

---
