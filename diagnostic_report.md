# Diagnostic Report: DermaScan AI V3

## Executive Summary
This report identifies critical UI, performance, and robustness issues in the current DermaScan AI V3 application. Resolving these issues is necessary to transition the prototype into a competition-ready clinical suite.

## Identified Issues

### 1. UI & Layout Awkwardness
- **Age Input**: Currently uses `st.sidebar.slider("Age", 0, 100, 50)`. A slider is imprecise and awkward for medical intake forms.
- **Sex Input**: Uses `["male", "female", "unknown"]`. This does not match standard clinical capitalization ("Female", "Male") and introduces an unnecessary "unknown" option which the model simply falls back to Female (1.0) internally anyway.
- **Anatomical Site**: Uses a list that matches the model's internal keys but with some casing inconsistencies. The internal keys (`site_anterior torso`, `site_head/neck`, etc.) need to be properly mapped from a clean UI display list (e.g., "Anterior Torso", "Head/Neck") rather than exposing the raw internal representation.
- **Disclaimer Banner**: The current banner (`⚠️ ACADEMIC PROTOTYPE...`) is styled as a large, obtrusive block. It should be visible but elegantly integrated so it doesn't detract from the premium feel.

### 2. Grad-CAM & Image Alignment
- **Mismatch**: The UI currently displays the *raw uploaded image* alongside the Grad-CAM overlay. Since the Grad-CAM is generated from the 224x224 preprocessed tensor and then resized back to the raw image size (or vice versa), there can be aspect ratio stretching. 
- **Fix**: The UI must display the *preprocessed* 224x224 image directly next to the 224x224 Grad-CAM output. This ensures 1:1 pixel alignment of the heatmap to the visual features the model actually "saw".

### 3. Inference Performance
- **Slow First Inference**: TensorFlow's XLA JIT compilation (`tf.config.optimizer.set_jit(True)`) compiles the execution graph on the *first* forward pass. This causes a significant delay (often 5-15 seconds) when analyzing the very first patient image, breaking the illusion of a fast, responsive app.
- **Fix**: We must implement a "pre-warming" routine immediately after model loading, passing a dummy zero-tensor through the model to trigger the compilation before the user interacts with the app.

### 4. Safety Net Over-Sensitivity
- **Problem**: The clinical mapper uses a rigid confidence threshold (0.6). If the model is <0.6, it outputs "Uncertain". While clinically safe, for a live presentation demo, this can result in the app failing to show its capabilities if demo images happen to yield 0.55 confidence.
- **Fix**: Implement a "Demo Mode" toggle in the sidebar that lowers the safety threshold to 0.5, allowing the model to make predictions on slightly harder images during the presentation without compromising the hardcoded clinical safety net for real-world use.

## Next Steps
Proceed with UI/UX recommendations and implementation of the Performance pre-warming scripts.
