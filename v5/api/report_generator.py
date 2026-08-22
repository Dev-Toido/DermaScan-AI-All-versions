import os
import uuid
from fpdf import FPDF

# Ensure reports directory exists
REPORTS_DIR = "/tmp/dermascan_v5_reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_clinical_report(result_dict, image_path=None, heatmap_path=None):
    """
    Generates a PDF clinical report and returns a unique UUID path.
    """
    report_id = str(uuid.uuid4())
    pdf_path = os.path.join(REPORTS_DIR, f"{report_id}.pdf")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, txt="DermaScan AI V5 - Clinical Report", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, txt=f"Report ID: {report_id}", ln=True)
    pdf.ln(5)
    
    # Overview
    pdf.set_font("Arial", size=12)
    pdf.cell(190, 8, txt=f"Primary Diagnosis: {result_dict['top_diagnosis']}", ln=True)
    pdf.cell(190, 8, txt=f"Malignancy Risk Index: {result_dict['risk_index']} ({result_dict['malignancy_score']:.2%})", ln=True)
    pdf.cell(190, 8, txt=f"Recommendation: {result_dict['recommendation']}", ln=True)
    pdf.ln(5)
    
    # Images
    y_img = pdf.get_y()
    if image_path and os.path.exists(image_path):
        pdf.image(image_path, x=10, y=y_img, w=85)
    if heatmap_path and os.path.exists(heatmap_path):
        pdf.image(heatmap_path, x=105, y=y_img, w=85)
        
    pdf.set_y(y_img + 90)
    
    # Disclaimer
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 10, txt="WARNING: ACADEMIC PROTOTYPE - Not for clinical use. This tool is designed to assist, not replace, a medical professional.")
    pdf.ln(5)
    
    # DDx Probabilities
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, txt="Clinical DDx Probabilities:", ln=True)
    pdf.set_font("Arial", size=11)
    
    sorted_ddx = sorted(result_dict['all_ddx'].items(), key=lambda x: x[1], reverse=True)
    for cls_name, prob in sorted_ddx:
        pdf.cell(190, 6, txt=f"  {cls_name}: {prob:.2%}", ln=True)
        
    pdf.ln(5)
    
    # Etiology Probabilities
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, txt="Etiology (Family) Probabilities:", ln=True)
    pdf.set_font("Arial", size=11)
    
    sorted_eti = sorted(result_dict['all_etiology'].items(), key=lambda x: x[1], reverse=True)
    for cls_name, prob in sorted_eti:
        pdf.cell(190, 6, txt=f"  {cls_name}: {prob:.2%}", ln=True)
        
    # Save PDF
    pdf.output(pdf_path)
    
    return report_id, pdf_path
