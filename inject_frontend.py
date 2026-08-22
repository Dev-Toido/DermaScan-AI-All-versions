import os

def inject_frontend():
    path = "v5/ui/src/app/page.tsx"
    
    with open(path, "r") as f:
        content = f.read()
    
    # 1. Inject state
    state_injection = """  const [result, setResult] = useState<any>(null);

  // Feedback State
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackDiagnosis, setFeedbackDiagnosis] = useState("mel");
  const [feedbackSubmitting, setFeedbackSubmitting] = useState(false);"""
    
    content = content.replace("  const [result, setResult] = useState<any>(null);", state_injection)
    
    # 2. Inject submitFeedback function
    func_injection = """  const handleAnalyze = async () => {
"""
    
    submit_func = """  const submitFeedback = async () => {
    if (!result || !result.cropped_image) return;
    setFeedbackSubmitting(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/submit_feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          image_b64: result.cropped_image,
          original_diagnosis: result.top_diagnosis,
          corrected_diagnosis: feedbackDiagnosis,
          age: "unknown",
          sex: "unknown",
          anatom_site: "unknown"
        })
      });
      if (res.ok) {
        alert("Correction saved! This edge-case will be heavily penalized in the next training epoch.");
        setShowFeedback(false);
      } else {
        alert("Failed to submit feedback.");
      }
    } catch (err) {
      console.error(err);
      alert("Error submitting feedback.");
    }
    setFeedbackSubmitting(false);
  };

  const handleAnalyze = async () => {
"""
    content = content.replace(func_injection, submit_func)
    
    # 3. Inject UI
    ui_injection = """                              <FileText size={16} />
                              Download Clinical Report (PDF)
                            </button>
                          )}
"""
    
    feedback_ui = """                              <FileText size={16} />
                              Download Clinical Report (PDF)
                            </button>
                          )}

                          {/* Continuous Learning Feedback */}
                          <div className="mt-4 pt-4 border-t border-white/10">
                            <button 
                              onClick={() => setShowFeedback(!showFeedback)}
                              className="text-xs text-gray-400 hover:text-[#00D4FF] transition-colors underline flex items-center justify-center w-full"
                            >
                              Diagnosis Incorrect? Submit Correction
                            </button>
                            
                            <AnimatePresence>
                              {showFeedback && (
                                <motion.div 
                                  initial={{ opacity: 0, height: 0 }}
                                  animate={{ opacity: 1, height: 'auto' }}
                                  exit={{ opacity: 0, height: 0 }}
                                  className="mt-3 bg-black/40 p-3 rounded-lg border border-white/5 overflow-hidden"
                                >
                                  <label className="block text-xs text-gray-300 mb-2">Select True Diagnosis:</label>
                                  <select 
                                    value={feedbackDiagnosis}
                                    onChange={(e) => setFeedbackDiagnosis(e.target.value)}
                                    className="w-full bg-[#0B1120] border border-white/10 rounded px-2 py-1.5 text-sm text-white mb-3"
                                  >
                                    <option value="mel">Melanoma (MEL)</option>
                                    <option value="nv">Nevus (NV)</option>
                                    <option value="bcc">Basal Cell Carcinoma (BCC)</option>
                                    <option value="ak">Actinic Keratosis (AK)</option>
                                    <option value="bkl">Benign Keratosis (BKL)</option>
                                    <option value="df">Dermatofibroma (DF)</option>
                                    <option value="vasc">Vascular Lesion (VASC)</option>
                                    <option value="scc">Squamous Cell Carcinoma (SCC)</option>
                                  </select>
                                  <button 
                                    onClick={submitFeedback}
                                    disabled={feedbackSubmitting}
                                    className="w-full py-2 bg-gradient-to-r from-blue-600 to-[#00D4FF] hover:from-blue-500 hover:to-cyan-400 text-white rounded text-xs font-bold transition-all disabled:opacity-50"
                                  >
                                    {feedbackSubmitting ? 'Submitting...' : 'Submit to Replay Buffer'}
                                  </button>
                                </motion.div>
                              )}
                            </AnimatePresence>
                          </div>
"""
    content = content.replace(ui_injection, feedback_ui)
    
    with open(path, "w") as f:
        f.write(content)
        
    print("Frontend injected successfully!")

if __name__ == "__main__":
    inject_frontend()
