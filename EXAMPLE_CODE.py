import math

# --- Mục 1: Định nghĩa Trọng số (Sẽ được điều chỉnh sau khi kiểm thử) ---
WEIGHTS = {
    "recommendation": 0.5,
    "time": 0.3,
    "cost": 0.2
}

# --- Mục 2: Các hàm chuẩn hóa (Normalization) ---

def normalize(value, min_val, max_val):
    """Chuẩn hóa Min-Max: càng cao càng tốt (0-1)."""
    if max_val == min_val:
        return 1.0 # Tránh chia cho 0
    return (value - min_val) / (max_val - min_val)

def normalize_inverse(value, min_val, max_val):
    """Chuẩn hóa Min-Max Đảo: càng thấp càng tốt (0-1)."""
    if max_val == min_val:
        return 1.0
    return (max_val - value) / (max_val - min_val)

# --- Mục 3: Hàm Logic chính (Decision Process) ---

def select_final_itinerary(possible_itineraries, user_constraints, context_alerts):
    """
    Hàm logic chính: Tích hợp và ra quyết định.
    Chọn ra lộ trình tốt nhất dựa trên điểm số đã chuẩn hóa và các ràng buộc.
    """
    
    best_itinerary = None
    max_decision_score = -float('inf')

    # 3a. Tìm Min-Max để chuẩn hóa (Rất quan trọng)
    scores = [it["avg_rec_score"] for it in possible_itineraries]
    times = [it["total_time"] for it in possible_itineraries]
    costs = [it["total_cost"] for it in possible_itineraries]
    
    # Xử lý trường hợp chỉ có 1 lộ trình (tránh chia cho 0)
    min_score, max_score = min(scores), max(scores)
    min_time, max_time = min(times), max(times)
    min_cost, max_cost = min(costs), max(costs)

    print("--- BẮT ĐẦU QUY TRÌNH QUYẾT ĐỊNH ---")
    
    for itinerary in possible_itineraries:
        
        # 3b. Kiểm tra Ràng buộc CỨNG (từ người dùng)
        if itinerary["total_cost"] > user_constraints.get("max_budget", 99999):
            print(f"Loại Lộ trình '{itinerary['id']}': Vượt ngân sách.")
            continue
        if itinerary["total_time"] > user_constraints.get("max_time", 99):
            print(f"Loại Lộ trình '{itinerary['id']}': Vượt thời gian.")
            continue
            
        # 3c. Chuẩn hóa giá trị
        score_norm = normalize(itinerary["avg_rec_score"], min_score, max_score)
        time_norm = normalize_inverse(itinerary["total_time"], min_time, max_time)
        cost_norm = normalize_inverse(itinerary["total_cost"], min_cost, max_cost)
        
        # 3d. Xử lý Cảnh báo (từ module ngữ cảnh)
        alert_penalty = 0.0 # Không phạt
        for location in itinerary.get("locations", []):
            if location in context_alerts:
                print(f"(!) Lộ trình '{itinerary['id']}' dính cảnh báo: {context_alerts[location]}")
                alert_penalty = 0.5 # Giảm 50% điểm
                break
                
        # 3e. Tính Điểm Quyết Định Cuối Cùng
        decision_score = (WEIGHTS["recommendation"] * score_norm) + \
                         (WEIGHTS["time"] * time_norm) + \
                         (WEIGHTS["cost"] * cost_norm)
        
        # Áp dụng phạt
        final_score = decision_score * (1 - alert_penalty)
        
        print(f"...Đang xét Lộ trình '{itinerary['id']}': Score={final_score:.2f}")

        # 3f. Cập nhật lựa chọn tốt nhất
        if final_score > max_decision_score:
            max_decision_score = final_score
            best_itinerary = itinerary
            best_itinerary["final_decision_score"] = final_score

    # 4. Trả về đầu ra cuối cùng
    print("--- KẾT THÚC QUY TRÌNH ---")
    return best_itinerary

# --- Mục 4: Ví dụ cách sử dụng (Mô phỏng) ---
if __name__ == "__main__":
    
    # Dữ liệu mô phỏng từ các Task khác
    TASKS_3_4_OUTPUT = [
        {"id": "A (Văn hóa)", "locations": ["Bảo tàng", "Hồ Gươm"], "avg_rec_score": 90, "total_time": 4, "total_cost": 200},
        {"id": "B (Tiết kiệm)", "locations": ["Lăng Bác", "Chùa Một Cột"], "avg_rec_score": 85, "total_time": 3, "total_cost": 100},
        {"id": "C (Nhiều điểm)", "locations": ["Hồ Tây", "Phủ Tây Hồ", "Cà phê"], "avg_rec_score": 95, "total_time": 5, "total_cost": 300},
    ]
    
    # Ràng buộc từ Người dùng
    USER_INPUT = {"max_budget": 250, "max_time": 4}
    
    # Cảnh báo từ Module Ngữ Cảnh
    ALERT_INPUT = {"Hồ Tây": "RAIN"} # Báo Hồ Tây có mưa

    # Chạy logic Quyết định
    final_choice = select_final_itinerary(TASKS_3_4_OUTPUT, USER_INPUT, ALERT_INPUT)

    if final_choice:
        print(f"\n==> LỘ TRÌNH ĐƯỢC CHỌN: **{final_choice['id']}** (Điểm: {final_choice['final_decision_score']:.2f})")
    else:
        print("\n==> Không tìm thấy lộ trình nào phù hợp.")

# Kết quả mong đợi:
# Lộ trình 'C' bị loại vì mưa (penalty) VÀ vượt ngân sách/thời gian.
# Lộ trình 'A' bị loại vì vượt thời gian.
# Lộ trình 'B' được chọn vì thỏa mãn mọi điều kiện.