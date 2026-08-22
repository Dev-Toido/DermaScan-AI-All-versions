import re

path = 'v5/ui/src/app/page.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the Continuous Learning Feedback block using regex
ui_pattern = re.compile(r'\{\/\* Continuous Learning Feedback \*\/\}.*?<\/AnimatePresence>\s*<\/div>', re.DOTALL)

new_ui = """{/* Continuous Learning Feedback */}
                          <div className="mt-6 pt-5 border-t border-white/10">
                            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3 text-center">Clinical Verification</h4>
                            
                            <AnimatePresence>
                              {showThankYou ? (
                                <motion.div 
                                  initial={{ opacity: 0, scale: 0.9 }}
                                  animate={{ opacity: 1, scale: 1 }}
                                  exit={{ opacity: 0, scale: 0.9 }}
                                  className="bg-emerald-500/20 border border-emerald-500/30 rounded-lg p-4 text-center"
                                >
                                  <div className="text-emerald-400 font-bold mb-1">Thank You!</div>
                                  <div className="text-xs text-emerald-300">Your verification has been added to the Active Learning pipeline. Clearing scanner...</div>
                                </motion.div>
                              ) : (
                                <motion.div className="flex flex-col gap-3">
                                  <button 
                                    onClick={() => submitFeedback(true)}
                                    disabled={feedbackSubmitting}
                                    className="w-full bg-emerald-600/20 hover:bg-emerald-600/40 text-emerald-400 border border-emerald-500/30 py-2.5 rounded-lg font-bold text-sm transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                                  >
                                    ✅ Confirm Diagnosis
                                  </button>
                                  
                                  <button 
                                    onClick={() => setShowFeedback(!showFeedback)}
                                    className="w-full bg-red-600/20 hover:bg-red-600/40 text-red-400 border border-red-500/30 py-2.5 rounded-lg font-bold text-sm transition-all flex items-center justify-center gap-2"
                                  >
                                    ❌ Overrule AI
                                  </button>
                                </motion.div>
                              )}
                            </AnimatePresence>
                            
                            <AnimatePresence>
                              {showFeedback && !showThankYou && (
                                <motion.div 
                                  initial={{ opacity: 0, height: 0 }}
                                  animate={{ opacity: 1, height: 'auto' }}
                                  exit={{ opacity: 0, height: 0 }}
                                  className="mt-3 bg-black/40 p-3 rounded-lg border border-red-500/20 overflow-hidden"
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
                                    <option value="unk">Unknown</option>
                                  </select>
                                  
                                  <button 
                                    onClick={() => submitFeedback(false)}
                                    disabled={feedbackSubmitting}
                                    className="w-full bg-red-600 hover:bg-red-500 text-white py-2 rounded font-bold text-sm shadow-[0_0_15px_rgba(220,38,38,0.4)] disabled:opacity-50"
                                  >
                                    {feedbackSubmitting ? "Saving..." : "Submit to Replay Buffer"}
                                  </button>
                                </motion.div>
                              )}
                            </AnimatePresence>
                          </div>"""

content = ui_pattern.sub(new_ui, content)

# Check image size text
# user said "the image is of 380 right, but the docs says different why?"
content = content.replace('224', '380')
content = content.replace('224x224', '380x380')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("UI Updated!")
