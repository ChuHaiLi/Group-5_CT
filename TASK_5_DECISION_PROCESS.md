# Task 5: Nghiên cứu Logic Tích hợp Quyết định (Decision Process)

**Thành viên thực hiện - MSSV:** Nguyễn Gia Quốc Uy - 24127261

## 1. Mục Tiêu

Nhiệm vụ này tập trung vào việc thiết kế "bộ não" logic của hệ thống. Mục tiêu là xây dựng một quy trình (hoặc thuật toán) để lựa chọn tổ hợp điểm đến và lộ trình cuối cùng, dựa trên việc cân bằng nhiều yếu tố xung đột như: sở thích, thời gian/chi phí, và các điều kiện thực tế.

## 2. Phân Tích Lý Thuyết (Theory)

Logic của Task 5 là một bài toán **Ra quyết định Đa tiêu chí (Multi-Criteria Decision Making)**. Nó nhận đầu vào từ các module khác:

* **User Analysis:** Các ràng buộc cứng (constraints) như `max_budget` (ngân sách tối đa) và `max_time` (thời gian tối đa)
* **Ranking:** Một danh sách các địa điểm tiềm năng, mỗi địa điểm có `recommendation_score` (điểm khuyến nghị hoặc là điểm đánh giá)
* **Routing:** Dữ liệu về lộ trình cho một *tổ hợp* các điểm, bao gồm `total_travel_time` (tổng thời gian di chuyển) và `total_cost` (tổng chi phí chi trả)
* **Context:** Các cảnh báo (Alerts) hoặc yếu tố ảnh hưởng, ví dụ: `alert_level` (ví dụ: mức độ cảnh báo: 0 = bình thường, 1 = mưa,...)

### Thách thức 1: Chuẩn Hóa Dữ Liệu (Normalization)

Một vấn đề kỹ thuật lớn là các tiêu chí có thang đo khác nhau (ví dụ: điểm 0-100, thời gian 0-8 giờ, chi phí 0-1.000.000 VND). Chúng ta không thể cộng trừ trực tiếp.

**Giải pháp:** Phải sử dụng phương pháp chuẩn hóa (ví dụ: Min-Max Scaling) để đưa tất cả các giá trị về một thang điểm chung (ví dụ: 0 đến 1) trước khi áp dụng trọng số.
* Với các tiêu chí "càng cao càng tốt" (như điểm khuyến nghị):
    `Score_Norm = (Score - Min_Score) / (Max_Score - Min_Score)`
* Với các tiêu chí "càng thấp càng tốt" (như thời gian, chi phí):
    `Score_Norm = (Max_Value - Value) / (Max_Value - Min_Value)`

### Thách thức 2: Bùng nổ Tổ Hợp (Combinatorial Explosion)

Nếu Logic xếp hạng và khuyến nghị (Recommendation và Ranking) trả về 10 địa điểm, chúng ta không thể kiểm tra mọi tổ hợp lộ trình (ví dụ: 10! tổ hợp).

**Giải pháp:** Hệ thống phải định nghĩa một chiến lược. Ví dụ: "Chỉ xét các tổ hợp 3 điểm từ 5 địa điểm có điểm cao nhất". Hệ thống sẽ tạo các tổ hợp này (`[A, B, C]`, `[A, B, D]`,...) và lần lượt gọi khâu Thuật toán tối ưu lộ trình để lấy dữ liệu `total_time` và `total_cost` cho từng tổ hợp.

## 3. Cấu Trúc Dữ Liệu (Data Structures)

**Input (Đầu vào mô phỏng):**
```json
{
  "user_constraints": { "max_budget": 500, "max_time": 8 },
  "ranked_locations": [
    {"id": "loc_A", "name": "Bảo tàng", "recommend_score": 95},
    {"id": "loc_B", "name": "Hồ Gươm", "recommend_score": 90},
    {"id": "loc_C", "name": "Lăng Bác", "recommend_score": 88}
  ],
  "context_alerts": { "loc_B": "CROWDED" }
}
```

**Output (Đầu ra mô phỏng):**
```json

{
  "selected_itinerary": {
    "locations_ordered": ["loc_C", "loc_A"],
    "analytics": { "total_time": 3.5, "total_cost": 150 },
    "final_decision_score": 0.89,
    "explainability_tags": ["Phù hợp sở thích", "Tránh được địa điểm đông đúc"]
  }
}
```

## 4. Thiết Kế Logic (Mã Giả - Pseudocode)
Công thức tính điểm sẽ sử dụng các trọng số (weights)...

```pseudocode
// 1. Định nghĩa Trọng số (Sẽ được điều chỉnh sau khi kiểm thử)
w_recommend = 0.5 // Ưu tiên sự phù hợp sở thích
w_time = 0.3      // Ưu tiên thời gian di chuyển ngắn
w_cost = 0.2      // Ưu tiên chi phí thấp

// 2. Nhận đầu vào từ các module khác
user_constraints = GET_USER_INPUT() // Lấy {ngân sách tối đa, thời gian tối đa}
all_potential_routes = GET_GENERATED_ROUTES() // Lấy danh sách lộ trình (kèm điểm score, time, cost)
real_time_alerts = GET_CONTEXTUAL_ALERTS() // Lấy cảnh báo {ví dụ: "Hồ Gươm": "MƯA"}

// 3. Chuẩn hóa thang đo (Tìm min/max để so sánh công bằng)
(min_score, max_score) = FIND_SCORE_BOUNDS(all_potential_routes)
(min_time, max_time) = FIND_TIME_BOUNDS(all_potential_routes)
(min_cost, max_cost) = FIND_COST_BOUNDS(all_potential_routes)

best_itinerary = NULL
max_decision_score = -INFINITY

// 4. Duyệt qua từng lộ trình để chọn ra cái tốt nhất
FOR each itinerary IN all_potential_routes:
    
    // 4a. Kiểm tra Ràng buộc của Người dùng (Ràng buộc CỨNG)
    IF itinerary.cost > user_constraints.budget: 
        CONTINUE // Bỏ qua vì quá đắt
    IF itinerary.time > user_constraints.time: 
        CONTINUE // Bỏ qua vì quá lâu

    // 4b. Chuẩn hóa giá trị (đưa về thang 0-1)
    score_norm = NORMALIZE(itinerary.score, min_score, max_score)
    time_norm = NORMALIZE_INVERSE(itinerary.time, min_time, max_time) // Thời gian thấp = điểm cao
    cost_norm = NORMALIZE_INVERSE(itinerary.cost, min_cost, max_cost) // Chi phí thấp = điểm cao
    
    // 4c. Áp dụng Phạt (Dựa trên Cảnh báo)
    alert_penalty = 0
    FOR location IN itinerary.locations:
        IF location.receives_alert(real_time_alerts):
            alert_penalty = 0.5 // Phạt 50% điểm nếu dính cảnh báo
            BREAK // Chỉ phạt 1 lần cho mỗi lộ trình
            
    // 4d. Tính Điểm Quyết Định Cuối Cùng
    // (Điểm chuẩn hóa * Trọng số)
    final_score = (w_recommend * score_norm) + (w_time * time_norm) + (w_cost * cost_norm)
    
    // Áp dụng phạt
    final_score = final_score * (1 - alert_penalty)
    
    // 4e. Cập nhật kết quả tốt nhất
    IF final_score > max_decision_score:
        max_decision_score = final_score
        best_itinerary = itinerary

// 5. Trả về lộ trình tốt nhất
RETURN best_itinerary
```
## Giải Thích Logic Mã Giả (Decision Process)

Dưới đây là giải thích chi tiết về 5 bước hoạt động của mã giả "bộ não" quyết định, giúp các thành viên trong nhóm hiểu rõ luồng xử lý.

## a. ⚙️ Thiết Lập (Định nghĩa Trọng số)

* `w_recommend = 0.5` (ưu tiên sự phù hợp)
* `w_time = 0.3` (ưu tiên thời gian ngắn)
* `w_cost = 0.2` (ưu tiên chi phí thấp)

Đây là các **trọng số** thể hiện mức độ ưu tiên của hệ thống. Các con số này có thể được điều chỉnh lại sau khi kiểm thử để cho ra kết quả tốt hơn.

---

## b. 📥 Thu Thập Dữ Liệu (Nhận Đầu vào)

* **`user_constraints = GET_DATA(...)`**: Lấy các ràng buộc cứng từ người dùng (ví dụ: ngân sách tối đa, tổng thời gian cho phép).
* **`possible_itineraries = GENERATE_COMBINATIONS(...)`**: Lấy một danh sách các lộ trình tiềm năng. Mỗi lộ trình này đã được tính toán sẵn điểm khuyến nghị (phù hợp sở thích) và thông số đường đi (tổng thời gian, tổng chi phí).
* **`context_alerts = GET_DATA(...)`**: Lấy các cảnh báo theo thời gian thực (ví dụ: "Hồ Gươm: Mưa", "Phố Cổ: Đông đúc").

---

## c. 📏 Chuẩn Hóa Thang Đo

* **`(min_score, max_score) = FIND_BOUNDS(...)`**

Đây là bước kỹ thuật quan trọng. Nó tìm ra giá trị lớn nhất/nhỏ nhất của (score, time, cost) trong *tất cả* các lộ trình. Việc này là để "chuẩn hóa" dữ liệu, đảm bảo chúng ta đang so sánh các giá trị một cách công bằng (ví dụ: không thể lấy "điểm 100" trừ "5 giờ").

---

## d. 🧠 Lặp và Quyết Định (Duyệt qua Lộ trình)

Đây là logic chính, nó xem xét *từng* lộ trình tiềm năng một.

### Bước 1: Kiểm tra Ràng buộc CỨNG

* `IF itinerary.cost > user_constraints.budget: CONTINUE`
    > Nếu lộ trình này đắt hơn ngân sách của người dùng -> **Loại ngay**, bỏ qua, xét cái tiếp theo.
* Tương tự, nếu tốn thời gian hơn thời gian cho phép của người dùng -> **Loại ngay**.

### Bước 2: Chuẩn Hóa Giá trị

* Chuyển đổi điểm số, thời gian, và chi phí của lộ trình này về một thang điểm chung (từ 0 đến 1) bằng các hàm `NORMALIZE`.
* Lưu ý: `NORMALIZE_INVERSE` (đảo ngược) được dùng cho thời gian và chi phí, vì giá trị *càng thấp* thì điểm *càng cao* (tốt).

### Bước 3: Áp dụng Phạt

* Kiểm tra xem có địa điểm nào trong lộ trình này bị dính cảnh báo thời gian thực không.
* Nếu có (ví dụ: "Mưa") -> gán một "hình phạt" (`alert_penalty = 0.5`).

### Bước 4: Tính Điểm Quyết Định

* Đây là công thức cốt lõi. Nó lấy các điểm đã chuẩn hóa (0-1) ở bước 4b nhân với các trọng số (weights) ở bước 1.
* `final_score = final_score * (1 - alert_penalty)`: Nếu lộ trình bị phạt (0.5), điểm cuối cùng của nó sẽ bị **giảm đi 50%**.

### Bước 5: Cập nhật Kết quả

* So sánh điểm `final_score` của lộ trình này với điểm cao nhất (`max_decision_score`) đã tìm thấy trước đó.
* Nếu điểm này cao hơn -> lưu nó lại (`best_itinerary = itinerary`).

---

## 5. 📤 Trả Về Kết Quả (Đầu ra)

* **`RETURN best_itinerary`**

Sau khi vòng lặp (4) chạy qua tất cả các lộ trình, hệ thống trả về `best_itinerary` (lộ trình có điểm số cao nhất và thỏa mãn mọi điều kiện). Đây chính là gợi ý cuối cùng hiển thị cho người dùng.