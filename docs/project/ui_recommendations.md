# UI/UX Recommendations for DermaScan AI V3

## Design Philosophy
To present DermaScan AI V3 as a competition-ready clinical tool, the interface must evoke trust, precision, and modernity. We recommend adopting a **Glassmorphism** design language coupled with **Material Design 3 (MD3)** elements. This provides a sleek, translucent hierarchy that focuses attention on the medical images and diagnostic outputs without feeling heavy or cluttered.

## Recommended Changes

### 1. Intake Form Precision
- **Age Input**: Replace the current `st.sidebar.slider` with `st.sidebar.number_input`. 
  - *Reasoning*: Sliders imply estimates. Clinical intake requires precision.
  - *Implementation*: `st.sidebar.number_input("Patient Age", min_value=0, max_value=120, value=50, step=1)`
- **Sex Selection**: Replace the lowercase list with a standard dropdown.
  - *Implementation*: `st.sidebar.selectbox("Sex", ["Female", "Male"])`. Update backend logic to map "Female" to 1.0 and "Male" to 0.0.
- **Anatomical Site**: Clean up the raw internal keys to a professional display list.
  - *Implementation*: Use a selectbox with properly cased display names: `["Anterior torso", "Head/neck", "Lateral torso", "Lower extremity", "Oral/genital", "Palms/soles", "Posterior torso", "Upper extremity"]`. The backend must map these back to `site_anterior torso`, etc.

### 2. "Demo Mode" Toggle
- **Feature**: Add a checkbox `st.sidebar.checkbox("Demo Mode", value=False)` with a help tooltip: *"Lowers uncertainty threshold to 0.5 for presentation purposes."*
- *Reasoning*: The current 0.6 confidence threshold for the safety net is great for clinical safety but can lead to uncompelling live demos if the model outputs 0.58 on a test image. This toggle allows presenters to manually bypass the strict clinical threshold for showcase purposes while keeping it active by default.

### 3. Visual Layout & Alignment
- **Preprocessed Image Display**: Currently, the raw uploaded image is shown next to the Grad-CAM overlay. This causes visual mismatch because Grad-CAM is mapped to the 380x380 input tensor.
  - *Recommendation*: Display the *resized* (380x380) image in `col1` and the Grad-CAM overlay (also 380x380) in `col2`. This guarantees perfect 1:1 visual alignment, making the explainability feature significantly more trustworthy.
- **Animations**: Introduce subtle Lottie animations and ensure buttons use gradient backgrounds with hover transformations to feel highly responsive.

## Conclusion
Implementing these UI/UX recommendations will transform the prototype from an engineering script into a polished, professional medical suite ready for panel review.
