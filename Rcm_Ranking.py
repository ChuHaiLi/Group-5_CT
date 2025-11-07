import json
import math

# 1. Load data
with open("data/sample_places.json") as f:
    places = json.load(f)

# 2. User profile
user = {
    "preferences": ["museum", "park"],
    "budget": 50,
    "location": (10.776, 106.700)
}

# 3. Distance score
def distance_score(place, user):
    dx = place["lat"] - user["location"][0]
    dy = place["lon"] - user["location"][1]
    dist = math.sqrt(dx*dx + dy*dy)
    return max(0, 1 - dist/10)  # normalize 0-1

# 4. Compute composite score
def compute_score(place, user):
    w_pref, w_dist, w_rating, w_trend = 0.4, 0.25, 0.25, 0.1
    preference_score = 1 if any(tag in user["preferences"] for tag in place["tags"]) else 0
    score = (w_pref*preference_score + 
             w_dist*distance_score(place, user) + 
             w_rating*place["rating"]/5 + 
             w_trend*place.get("trend_score", 0))
    return score

for place in places:
    place["composite_score"] = compute_score(place, user)

# 5. Sort & top 5
top_places = sorted(places, key=lambda x: x["composite_score"], reverse=True)[:5]

# 6. Print with explain tags
for p in top_places:
    explain_tags = []
    if any(tag in user["preferences"] for tag in p["tags"]):
        explain_tags.append("Matches preference")
    if p["rating"] >= 4:
        explain_tags.append("High rating")
    print(p["name"], p["composite_score"], explain_tags)
