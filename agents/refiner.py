import copy

def refine_ad_data(ad_data: dict, updates: dict) -> dict:
    """
    평가 에이전트가 제안한 업데이트 내용을 바탕으로 원본 데이터를 안전하게 수정합니다.
    """
    new_data = copy.deepcopy(ad_data)
    
    storyboard_updates = updates.get("storyboard_updates", [])
    
    for update in storyboard_updates:
        idx = update.get("index")
        new_color = update.get("color")
        
        if idx is not None and 0 <= idx < len(new_data["storyboard"]):
            if new_color:
                new_data["storyboard"][idx]["color"] = new_color
                print(f"[Refiner] {idx+1}번째 씬의 폰트 색상을 '{new_color}'로 업데이트했습니다.")
                
    return new_data
