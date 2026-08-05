# DermaScan AI V3 - Marketing Website Design Brief

## 1. Overview & Objectives
To present DermaScan AI V3 as a world-class, competition-ready clinical suite. The website must build **clinical trust** while communicating **high-tech innovation**. It will serve as the primary marketing touchpoint for judges, clinicians, and potential investors.

## 2. Target Audience
- **Primary:** Competition Judges & Medical AI Reviewers (looking for accuracy, safety, innovation).
- **Secondary:** Dermatologists & Clinicians (looking for reliability, workflow integration).

## 3. Visual Identity
- **Aesthetic:** Modern, premium medical-AI aesthetic blending Glassmorphism (translucent cards, blur effects) with Material Design 3 (clean layout, crisp shadows).
- **Color Palette:**
  - **Primary:** Deep Medical Blue (`#0f172a` to `#1e293b`) for the background to convey high-tech sophistication.
  - **Accent:** Vibrant Teal/Accent Green (`#14b8a6` / `#10b981`) for buttons and clinical success indicators.
  - **Typography & UI:** Crisp White (`#ffffff`) for primary text, Slate (`#94a3b8`) for secondary text.
- **Typography:** **Inter** (sans-serif) for all text. Weights: 300 for body, 500 for buttons, 700 for headers.

## 4. Single-Page Layout Structure (Scroll Navigation)

1. **Hero Section**
   - **Visual:** High-impact, dark gradient background with subtle particles (via `particles.js` or CSS).
   - **Content:** Headline ("AI-Powered Skin Lesion Screening"), Subtitle ("Explainable. Safe. Clinician-first."), CTA ("View Live Demo").
   
2. **The Problem**
   - **Content:** The global shortage of dermatologists and the cost of late diagnosis.
   - **Visual:** Clean metric cards (e.g., "1 in 100,000", "10,000+ deaths").

3. **The Solution (How it Works)**
   - **Content:** Explaining the Multi-Modal fusion (Image + Metadata).
   - **Visual:** An interactive concept animation showing a dermoscopic image and a medical chart fusing into a unified prediction vector.

4. **Features & Safety**
   - **Content:** Focus on Explainability (Grad-CAM) and the Clinical Safety Net.
   - **Visual:** Glassmorphism cards with Lottie animations (or crisp SVGs) for each feature.

5. **Live Demo**
   - **Content:** "Experience the AI".
   - **Visual:** A high-quality video demo (simulated via an embedded video/GIF) or a prominent button to launch the local Streamlit application in a new tab.

6. **Performance & Validation**
   - **Content:** Model metrics, dataset details (ISIC 2019), and bias mitigation.
   - **Visual:** Clean, data-driven charts or metric highlights.

7. **Footer**
   - **Content:** Academic disclaimers ("Not for clinical use without human supervision"), Links to GitHub/Contact.

## 5. Technical Stack
- **Framework:** Vanilla HTML5, CSS3, JavaScript (No heavy frameworks for speed and portability).
- **Styling:** Tailwind CSS (via CDN) for rapid, responsive UI development.
- **Animations:** AOS (Animate on Scroll) for scroll-triggered reveals.
- **Interactivity:** Custom JavaScript for the multi-modal fusion animation and tab switching.
