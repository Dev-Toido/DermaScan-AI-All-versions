# DermaScan AI V4: Detailed Architecture and System Report

## 1. Executive Summary
DermaScan AI V4 represents a major architectural paradigm shift from the V3 monolithic Streamlit application to a decoupled, scalable, modern web stack. By separating the user interface from the heavy machine learning inference logic, V4 achieves higher performance, better maintainability, and greater flexibility for cloud deployment.

## 2. Architectural Overview
The V4 architecture is divided into two primary components:
- **Frontend**: A modern web interface built with **Next.js** (React).
- **Backend**: A high-performance REST API built with **FastAPI** (Python).

### 2.1 Next.js Frontend
- **Port**: Runs on `http://localhost:3000`.
- **Responsibilities**: 
  - Handles the user interface, patient metadata intake form, and image uploads.
  - Communicates with the FastAPI backend via RESTful endpoints.
  - Implements the new "Glassmorphism" and Material Design 3 UI concepts for a premium clinical feel.
- **Advantages**: Client-side rendering and static generation capabilities improve perceived load times. It provides a more robust foundation for complex UI state management compared to Streamlit.

### 2.2 FastAPI Backend
- **Port**: Runs on `http://localhost:8000`.
- **Responsibilities**:
  - Serves the multi-modal AI model (`dermascan_phase1_best.keras`), preserving the stable "brain" from the V2 architecture.
  - Processes incoming images and metadata, runs inference, and generates Grad-CAM heatmaps.
  - Returns structured JSON responses to the frontend.
- **Performance Optimizations**: FastAPI's asynchronous capabilities allow it to handle multiple concurrent inference requests more efficiently than Streamlit's synchronous blocking model. 
- **API Documentation**: Auto-generated Swagger UI available at `http://localhost:8000/docs`.

## 3. Model Integration
The underlying AI model is actually powered by the highly stable "brain" from the V2 architecture (`dermascan_phase1_best.keras`), ensuring consistent and robust diagnostic results.
- **Input Tensors**: The model expects two distinct inputs: `vision_input` and `tabular_input`.
- **Vision Processing**: Extracts visual features from dermoscopic images resized to `224x224`.
- **Tabular Metadata**: Processes biological markers with dynamic normalization utilizing `train_bridged.csv`. Age is scaled by the dataset mean and standard deviation, sex is mapped to binary (`1.0` for Female), and anatomical site is mapped via dynamic one-hot encoding corresponding to dataset columns.
- **Label Mapping**: Target classes are dynamically inferred via factorization of the `train_bridged.csv` diagnosis column, guaranteeing that label indexing seamlessly matches model outputs.
- **Inference Pipeline**: The backend fuses the preprocessed image array and tabular tensor for inference, extracting probabilistic differential diagnoses for skin lesions.

## 4. Run Sequence and Orchestration
The V4 system is orchestrated via the `run_v4.sh` script, which handles the following tasks seamlessly:
1. Environment setup (Python venv, Node.js environment).
2. Frontend dependency installation (`npm install`) and production build generation (`npm run build`) to conserve memory.
3. Spawning the FastAPI backend as a background process.
4. Launching the Next.js frontend.
5. Providing graceful shutdown for both processes via `SIGINT` (Ctrl+C).

## 5. Deployment Strategy
Unlike V3 which is ideally suited for Streamlit Community Cloud, V4 requires a distributed deployment strategy:
- **Frontend**: Can be deployed to **Vercel** or **Netlify** for optimized global edge delivery.
- **Backend**: Should be deployed to a containerized platform with sufficient memory to load the Keras model (e.g., Render, AWS ECS, Google Cloud Run, or a dedicated VPS).

## 6. Conclusion
DermaScan AI V4 successfully elevates the project from a research prototype to a production-ready application framework. Its decoupled nature paves the way for future enhancements such as database integration for patient records, user authentication, and advanced reporting features, while maintaining the rigorous clinical explainability required of a medical AI tool.
