import os

def append_endpoint():
    path = "v5/api/main.py"
    
    code_to_add = """
import uuid
from pydantic import BaseModel
import csv

class FeedbackRequest(BaseModel):
    image_b64: str
    original_diagnosis: str
    corrected_diagnosis: str
    age: str
    sex: str
    anatom_site: str

@app.post("/api/submit_feedback")
def submit_feedback(data: FeedbackRequest):
    try:
        # 1. Ensure hard_examples directory exists
        hard_examples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data_preparation", "hard_examples"))
        os.makedirs(hard_examples_dir, exist_ok=True)
        
        # 2. Save the image
        img_id = f"FEEDBACK_{uuid.uuid4().hex[:8]}"
        img_path = os.path.join(hard_examples_dir, f"{img_id}.jpg")
        
        # Strip the base64 header if present
        b64_str = data.image_b64
        if b64_str.startswith("data:image"):
            b64_str = b64_str.split(",")[1]
            
        img_data = base64.b64decode(b64_str)
        with open(img_path, "wb") as f:
            f.write(img_data)
            
        # 3. Append to CSV
        csv_path = os.path.abspath(os.path.join(hard_examples_dir, "..", "hard_examples_metadata.csv"))
        file_exists = os.path.exists(csv_path)
        
        with open(csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["image_id", "diagnosis", "age", "sex", "anatom_site"])
            writer.writerow([img_id, data.corrected_diagnosis.lower(), data.age, data.sex, data.anatom_site])
            
        return {"status": "success", "message": f"Saved {img_id} to replay buffer."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Feedback loop failed: {str(e)}")
"""
    with open(path, "a") as f:
        f.write(code_to_add)
    
    print("Feedback endpoint appended successfully!")

if __name__ == "__main__":
    append_endpoint()
