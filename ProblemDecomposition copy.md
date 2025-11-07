# Task 3 – Recommendation & Ranking (Phân rã bài toán chi tiết)

---

## [1️] Mục tiêu

Xây dựng module gợi ý địa điểm du lịch dựa trên hồ sơ người dùng.

**Kết quả:** Top 3–5 địa điểm phù hợp với sở thích, ngân sách, vị trí, và độ “hot trend” (mô phỏng).

---

## [2️] Input / Output / Context / Constraints

**Input:**

1. Dữ liệu địa điểm (`sample_places.json`) gồm:  
   - name (tên địa điểm)  
   - type (loại: museum, park, tour…)  
   - price (giá vé)  
   - rating (4–5 scale)  
   - tags (thẻ: museum, park, boat…)  
   - lat/lon (tọa độ)  
   - trend_score (0–1, mô phỏng mức độ “hot”)

2. Hồ sơ người dùng (`user profile`) gồm:  
   - preferences (sở thích: museum, park, boat…)  
   - budget (ngân sách)  
   - location (tọa độ GPS)  
   - time (thời gian dự kiến)  
   - optional: từ khóa tìm kiếm

**Output:**  
- Top 3–5 địa điểm gợi ý, gồm:  
  - name  
  - composite_score (0–1, tính toán dựa trên nhiều tiêu chí)  
  - explain_tags (“Matches preference”, “High rating”, “Hot trend”)

**Context:**  
- Module Task 3 là phần **xếp hạng & gợi ý** trong hệ thống Smart Tourism.  
- Kết quả sẽ được dùng bởi Task 4 (Route Optimization) và Task 5 (Decision Process).

**Constraints:**  
- Không thay đổi dữ liệu gốc.  
- Sử dụng **rule-based scoring**, không phải machine learning.  
- Có thể dễ dàng điều chỉnh trọng số (w1–w4) để cân bằng điểm.  
- Phải đảm bảo **top 3–5 địa điểm** là hợp lý với profile user.  
- Mã nguồn phải **dễ đọc, dễ test**, phù hợp với Git workflow nhóm.

---

## [3️] Phân rã bài toán (Decomposition)

Task 3 được chia thành **6 module nhỏ**:

1. **Load Data**  
   - **Mục tiêu:** Đọc danh sách địa điểm từ file JSON  
   - **Input:** `sample_places.json`  
   - **Output:** List/dict các địa điểm  
   - **Mô tả:** Sử dụng Python `json` hoặc `pandas` để load dữ liệu

2. **User Profile**  
   - **Mục tiêu:** Lấy thông tin người dùng  
   - **Input:** Hồ sơ user (preferences, budget, location, time)  
   - **Output:** Dict `user`  
   - **Mô tả:** Mô phỏng UI gửi dữ liệu hoặc dùng mock data

3. **Compute Score**  
   - **Mục tiêu:** Tính composite_score cho mỗi địa điểm  
   - **Input:** Data địa điểm + user profile  
   - **Output:** Mỗi địa điểm có `composite_score`  
   - **Mô tả:** Rule-based scoring:  
     - w1*preference_score  
     - w2*distance_score  
     - w3*rating  
     - w4*trend_score

4. **Filter & Ranking**  
   - **Mục tiêu:** Chọn top N địa điểm  
   - **Input:** Danh sách địa điểm có score  
   - **Output:** Top 3–5 địa điểm  
   - **Mô tả:** Sắp xếp theo `composite_score` giảm dần

5. **Explainability**  
   - **Mục tiêu:** Gắn nhãn giải thích cho kết quả  
   - **Input:** Top 3–5 địa điểm  
   - **Output:** Nhãn “Matches preference”, “High rating”, “Hot trend”  
   - **Mô tả:** Giúp người dùng hiểu tại sao địa điểm được gợi ý

6. **Output**  
   - **Mục tiêu:** Xuất kết quả  
   - **Input:** Top 3–5 địa điểm + explain tags  
   - **Output:** Console hoặc dict/json output  
   - **Mô tả:** Có thể in ra console hoặc trả về JSON cho Task 4/Task 5 sử dụng

---

## [4️] Algorithm (Các bước thực hiện)

1. Load dữ liệu địa điểm từ JSON (`sample_places.json`).  
2. Lấy profile người dùng (mock hoặc từ UI).  
3. Với mỗi địa điểm, tính **composite_score**:

composite_score = w1*preference_score + w2*distance_score + w3*rating + w4*trend_score


- **preference_score:** 1 nếu địa điểm trùng sở thích user, 0 nếu không  
- **distance_score:** tính khoảng cách từ user location → normalize 0–1  
- **rating:** chuẩn hóa 0–1  
- **trend_score:** đã có trong dữ liệu mô phỏng  

**Các bước xử lý:**  
1. Sắp xếp địa điểm theo `composite_score` giảm dần  
2. Chọn top 3–5 địa điểm  
3. Gắn nhãn `explain_tags` cho mỗi địa điểm  
4. Xuất kết quả ra console hoặc JSON  

---

## [5] Công cụ quan trọng nhất

**Python** là công cụ chính.

**Lý do chọn Python:**

- Dễ thao tác với JSON/CSV, mock data  
- Dễ viết hàm tính score và rule-based logic  
- Dễ test, debug và hiển thị kết quả nhanh  
- Hỗ trợ phát triển module tách rời, phù hợp với workflow Git nhóm  
- Khi cần nâng cấp thuật toán hoặc tích hợp ML trong tương lai, Python thuận tiện nhất

---

## [6️] Input/Output ví dụ

**Input (user profile):**

user = {
    "preferences": ["museum", "park"],
    "budget": 50,
    "location": (10.776, 106.700)
}


**Input (`sample_places.json`):**

[
  {
    "name": "City Museum",
    "type": "museum",
    "price": 20,
    "rating": 4.5,
    "tags": ["museum"],
    "lat": 10.780,
    "lon": 106.700,
    "trend_score": 0.8
  },
  {
    "name": "Central Park",
    "type": "park",
    "price": 0,
    "rating": 4.2,
    "tags": ["park"],
    "lat": 10.775,
    "lon": 106.702,
    "trend_score": 0.7
  }
]

**Output:**
1. City Museum - Score: 0.91 - Tags: ['Matches preference', 'High rating', 'Hot trend']
2. Central Park - Score: 0.88 - Tags: ['Matches preference', 'High rating']