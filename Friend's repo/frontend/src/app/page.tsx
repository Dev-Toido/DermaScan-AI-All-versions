"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence, useScroll, useTransform, useMotionValue, useSpring } from "framer-motion";
import { Upload, Activity, ShieldAlert, Clock, Scan, Sparkles, ChevronRight, CheckCircle2, Menu, X, ArrowRight, Microchip, Layers, Brain, Search, Crosshair, Network, GitPullRequest } from "lucide-react";
import Link from "next/link";

export default function LandingAndDashboard() {
  // Navigation State
  const [isNavScrolled, setIsNavScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Dashboard State
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [location, setLocation] = useState("Unknown");
  const [sex, setSex] = useState("Unknown");
  const [result, setResult] = useState<any>(null);

  // Spotlight Cursor State
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // Scroll animations
  const { scrollY } = useScroll();
  const opacityHero = useTransform(scrollY, [0, 500], [1, 0]);
  const yHero = useTransform(scrollY, [0, 500], [0, 100]);

  useEffect(() => {
    const handleScroll = () => {
      setIsNavScrolled(window.scrollY > 20);
    };
    
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener("scroll", handleScroll);
    window.addEventListener("mousemove", handleMouseMove);
    return () => {
      window.removeEventListener("scroll", handleScroll);
      window.removeEventListener("mousemove", handleMouseMove);
    };
  }, []);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = (file: File) => {
    setSelectedImage(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
  };

  const handleDragOver = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedImage) return;
    setIsScanning(true);
    
    const formData = new FormData();
    formData.append("file", selectedImage);
    formData.append("location", location);
    formData.append("sex", sex);
    
    try {
      const res = await fetch("http://localhost:8000/api/analyze", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setResult(data);
    } catch (error) {
      console.error("Analysis failed:", error);
    } finally {
      setIsScanning(false);
    }
  };

  const scrollToScanner = () => {
    document.getElementById("dashboard-scanner")?.scrollIntoView({ behavior: "smooth" });
  };

  // ✅ 3D Tilt Hover Effect Hook
  const use3DTilt = () => {
    const x = useMotionValue(0);
    const y = useMotionValue(0);
    
    const mouseXSpring = useSpring(x, { stiffness: 300, damping: 20 });
    const mouseYSpring = useSpring(y, { stiffness: 300, damping: 20 });
    
    const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ["10deg", "-10deg"]);
    const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ["-10deg", "10deg"]);
    
    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
      const rect = e.currentTarget.getBoundingClientRect();
      const width = rect.width;
      const height = rect.height;
      
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;
      
      const xPct = mouseX / width - 0.5;
      const yPct = mouseY / height - 0.5;
      
      x.set(xPct);
      y.set(yPct);
    };
    
    const handleMouseLeave = () => {
      x.set(0);
      y.set(0);
    };
    
    return { rotateX, rotateY, handleMouseMove, handleMouseLeave };
  };

  const tilt1 = use3DTilt();
  const tilt2 = use3DTilt();
  const tilt3 = use3DTilt();

  return (
    <div className="min-h-screen bg-transparent text-[var(--color-text-primary)] font-sans selection:bg-[#00D4FF] selection:text-[#050816]">
      
      {/* ✅ Aurora Gradient Background */}
      <div className="aurora-bg" />

      {/* ✅ Spotlight Cursor Effect */}
      <div 
        className="pointer-events-none fixed inset-0 z-40 transition-opacity duration-300"
        style={{
          background: `radial-gradient(600px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(0, 212, 255, 0.08), transparent 40%)`
        }}
      />

      {/* ✅ Floating Medical Icons Background */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden opacity-30">
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute text-[#00D4FF]/20"
            animate={{
              y: ["0%", "100%", "0%"],
              x: Math.sin(i) * 50,
              rotate: [0, 360],
            }}
            transition={{
              duration: 20 + i * 5,
              repeat: Infinity,
              ease: "linear",
            }}
            style={{
              left: `${(i * 23 + 15) % 85}%`,
              top: `${(i * 37 + 10) % 85}%`,
            }}
          >
            {i % 2 === 0 ? <Activity size={64} /> : <Scan size={48} />}
          </motion.div>
        ))}
      </div>

      {/* Navigation */}
      <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${isNavScrolled ? 'bg-[#050816]/60 backdrop-blur-2xl border-b border-white/5 py-4 shadow-xl' : 'bg-transparent py-6'}`}>
        <div className="max-w-7xl mx-auto px-6 md:px-12 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-11 h-11 rounded-xl bg-white/5 flex items-center justify-center shadow-[0_0_15px_rgba(255,255,255,0.1)] overflow-hidden">
              <img src="/logo.png" alt="DermaScan Logo" className="w-full h-full object-contain p-0.5" />
            </div>
            <span className="font-bold text-2xl tracking-tight font-display text-white group-hover:text-gray-300 transition-colors">DermaScan AI</span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            <Link href="#technology" className="text-[var(--color-text-secondary)] hover:text-white text-sm font-medium transition-colors hover:shadow-[0_0_10px_rgba(0,212,255,0.2)] px-3 py-1 rounded-md">Technology</Link>
            <Link href="#model" className="text-[var(--color-text-secondary)] hover:text-white text-sm font-medium transition-colors hover:shadow-[0_0_10px_rgba(0,212,255,0.2)] px-3 py-1 rounded-md">Model</Link>
            <Link href="#features" className="text-[var(--color-text-secondary)] hover:text-white text-sm font-medium transition-colors hover:shadow-[0_0_10px_rgba(0,212,255,0.2)] px-3 py-1 rounded-md">Features</Link>
            <Link href="#research" className="text-[var(--color-text-secondary)] hover:text-white text-sm font-medium transition-colors hover:shadow-[0_0_10px_rgba(0,212,255,0.2)] px-3 py-1 rounded-md">Research</Link>
          </div>

          <div className="hidden md:flex items-center gap-4">
            <button onClick={scrollToScanner} className="clinical-button-primary">
              Launch Scanner
            </button>
          </div>

          <button className="md:hidden text-white" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>
      </nav>

      {/* Section 1: Hero */}
      <section className="relative pt-40 pb-20 md:pt-52 md:pb-32 overflow-hidden max-w-7xl mx-auto px-6 md:px-12 z-10">
        <motion.div style={{ opacity: opacityHero, y: yHero }} className="grid lg:grid-cols-2 gap-16 items-center">
          
          {/* Left: Content */}
          <div className="max-w-2xl">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            >
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#111827]/80 backdrop-blur-md border border-white/10 mb-8 shadow-lg">
                <Sparkles size={14} className="text-[#00D4FF]" />
                <span className="text-xs font-semibold text-[#00D4FF] tracking-wide uppercase">Deep Learning Diagnostics</span>
              </div>
              
              <h1 className="text-5xl md:text-7xl font-bold font-display leading-[1.1] mb-6 tracking-tight text-white drop-shadow-2xl">
                AI-Powered Skin Lesion Screening
              </h1>
              
              <p className="text-lg md:text-xl text-[var(--color-text-secondary)] font-light leading-relaxed mb-10 max-w-xl backdrop-blur-sm bg-[#050816]/10 p-2 rounded-lg">
                Upload a dermoscopic image and let DermaScan AI perform intelligent lesion analysis using deep learning and explainable AI.
              </p>

              <div className="flex flex-col sm:flex-row gap-4">
                <button onClick={scrollToScanner} className="clinical-button-primary flex items-center justify-center gap-2 h-12 px-8">
                  Start AI Scan <ArrowRight size={16} />
                </button>
                <Link href="#technology" className="clinical-button-secondary flex items-center justify-center h-12 px-8 backdrop-blur-md">
                  View Technology
                </Link>
              </div>
            </motion.div>
          </div>

          {/* Right: Cinematic Scanning Demo - ✅ 3D Tilt */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            style={{ rotateX: tilt1.rotateX, rotateY: tilt1.rotateY, transformPerspective: 1000 }}
            onMouseMove={tilt1.handleMouseMove}
            onMouseLeave={tilt1.handleMouseLeave}
            className="relative h-[500px] rounded-2xl border border-white/10 bg-[#0B1120]/40 glass overflow-hidden flex items-center justify-center shadow-[0_20px_80px_rgba(0,212,255,0.15)]"
          >
            
            {/* Cinematic Background Grid */}
            <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)', backgroundSize: '40px 40px' }} />
            
            <div className="relative z-10 flex flex-col items-center pointer-events-none">
              <div className="w-64 h-64 border-2 border-[#00D4FF]/40 rounded-xl bg-[url('/bio-ml-demo.png')] bg-cover bg-center relative overflow-hidden shadow-[0_0_30px_rgba(0,212,255,0.3)]">
                {/* ✅ AI Scan Line Animation */}
                <div className="scan-line" />
                <motion.div 
                  animate={{ opacity: [0, 0.5, 0] }}
                  transition={{ duration: 3, ease: "linear", repeat: Infinity }}
                  className="absolute inset-0 bg-[#00D4FF]/20 mix-blend-overlay"
                />
              </div>
              
              <div className="mt-6 flex items-center gap-3 bg-[#111827]/80 backdrop-blur-md px-4 py-2 rounded-lg border border-white/10 shadow-[0_10px_20px_rgba(0,0,0,0.5)]">
                <Activity size={16} className="text-[#00D4FF] animate-pulse" />
                <span className="text-sm font-medium tracking-wide text-white">Processing Neural Network</span>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </section>

      {/* ✅ Medical Dashboard UI Section */}
      <section id="dashboard-scanner" className="py-24 bg-[#0B1120]/40 backdrop-blur-lg border-t border-b border-white/5 relative z-20 shadow-[0_0_50px_rgba(0,0,0,0.5)]">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold font-display mb-4 drop-shadow-lg">Clinical Diagnostic Terminal</h2>
            <p className="text-[var(--color-text-secondary)]">Secure, real-time image analysis pipeline.</p>
          </div>

          <div className="grid lg:grid-cols-12 gap-8">
            
            {/* Left Panel: Inputs (4 Columns) - ✅ 3D Tilt */}
            <motion.div 
              className="lg:col-span-4 flex flex-col gap-6"
              style={{ rotateX: tilt2.rotateX, rotateY: tilt2.rotateY, transformPerspective: 1000 }}
              onMouseMove={tilt2.handleMouseMove}
              onMouseLeave={tilt2.handleMouseLeave}
            >
              <div className="premium-card p-6 border-t border-l border-white/20">
                <h3 className="text-lg font-bold font-display mb-6 flex items-center gap-2 border-b border-white/10 pb-4 drop-shadow-md">
                  <Scan size={18} className="text-[#00D4FF]" /> Input Parameters
                </h3>
                
                <div className="space-y-5">
                  <div>
                    <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">Lesion Location</label>
                    <select 
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                      className="w-full bg-[#050816]/80 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-[#00D4FF]/60 focus:shadow-[0_0_15px_rgba(0,212,255,0.3)] transition-all"
                    >
                      <option value="Unknown">Unknown</option>
                      <option value="Abdomen">Abdomen</option>
                      <option value="Back">Back</option>
                      <option value="Chest">Chest</option>
                      <option value="Ear">Ear</option>
                      <option value="Face">Face</option>
                      <option value="Foot">Foot</option>
                      <option value="Genital">Genital</option>
                      <option value="Hand">Hand</option>
                      <option value="Lower Extremity">Lower Extremity</option>
                      <option value="Neck">Neck</option>
                      <option value="Scalp">Scalp</option>
                      <option value="Upper Extremity">Upper Extremity</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">Patient Sex</label>
                    <select 
                      value={sex}
                      onChange={(e) => setSex(e.target.value)}
                      className="w-full bg-[#050816]/80 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-[#00D4FF]/60 focus:shadow-[0_0_15px_rgba(0,212,255,0.3)] transition-all"
                    >
                      <option value="Unknown">Unknown</option>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                    </select>
                  </div>
                </div>

                <div className="mt-8 pt-6 border-t border-white/10">
                  <label 
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`block w-full h-32 border-2 border-dashed rounded-xl flex flex-col items-center justify-center cursor-pointer transition-all duration-300 ${isDragging ? "border-[#00D4FF] bg-[#00D4FF]/10 scale-[1.02] shadow-[0_0_20px_rgba(0,212,255,0.2)]" : "border-white/20 hover:border-[#00D4FF]/60 hover:bg-white/5"}`}
                  >
                    <Upload size={28} className={`mb-2 transition-all ${isDragging ? "text-[#00D4FF] scale-110" : "text-gray-400"}`} />
                    <span className="text-sm font-medium text-white drop-shadow">Upload Image</span>
                    <span className="text-xs text-gray-400 mt-1">JPEG, PNG up to 10MB</span>
                    <input type="file" className="hidden" accept="image/*" onChange={handleImageUpload} />
                  </label>
                </div>

                <div className="mt-6 flex gap-3">
                  <button 
                    onClick={() => { setPreviewUrl(null); setResult(null); setSelectedImage(null); }}
                    disabled={!selectedImage}
                    className="px-4 py-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/20 text-sm font-medium transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                  >
                    Clear
                  </button>
                  <button 
                    onClick={handleAnalyze}
                    disabled={isScanning || !selectedImage}
                    className="flex-1 clinical-button-primary flex items-center justify-center gap-2 h-[46px] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:shadow-none"
                  >
                    {isScanning ? (
                      <><Scan size={16} className="animate-spin" /> Scanning...</>
                    ) : (
                      "Initialize Scan"
                    )}
                  </button>
                </div>
              </div>
            </motion.div>

            {/* Right Panel: Viewer (8 Columns) - ✅ Glassmorphism & Heatmap Overlay */}
            <div className="lg:col-span-8 flex flex-col gap-6 relative">
              <div className="premium-card p-3 h-[600px] flex relative overflow-hidden bg-[#050816]/60 border-t border-l border-white/20 shadow-2xl">
                {previewUrl ? (
                  <div className="w-full h-full relative rounded-xl overflow-hidden flex items-center justify-center bg-black/60 shadow-inner">
                    <img src={previewUrl} alt="Preview" className="max-w-full max-h-full object-contain" />
                    
                    {/* ✅ Animated AI Scan Line */}
                    {isScanning && <div className="scan-line" />}
                    
                    {/* ✅ Animated Real Heatmap Overlay */}
                    <AnimatePresence>
                      {result?.heatmap && !isScanning && (
                        <motion.img 
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 0.85 }}
                          transition={{ duration: 1.5, ease: "easeInOut" }}
                          src={result.heatmap} 
                          className="absolute inset-0 w-full h-full object-contain mix-blend-screen"
                          alt="AI Heatmap"
                        />
                      )}
                    </AnimatePresence>

                    {/* Results Panel */}
                    <AnimatePresence>
                      {result && !isScanning && (
                        <motion.div 
                          initial={{ opacity: 0, y: 50, scale: 0.9 }}
                          animate={{ opacity: 1, y: 0, scale: 1 }}
                          transition={{ type: "spring", bounce: 0.4 }}
                          className="absolute bottom-6 right-6 w-[340px] bg-[#050816]/90 backdrop-blur-3xl rounded-2xl p-6 border-t border-l border-white/20 shadow-[0_30px_60px_rgba(0,0,0,0.8)]"
                        >
                          {/* Diagnostic Interpretation Header */}
                          <div className="mb-4 pb-4 border-b border-white/10">
                            <h3 className="text-lg font-bold text-white mb-1">Diagnostic Interpretation: <span className="text-[#00D4FF] drop-shadow">{result.top_diagnosis}</span></h3>
                          </div>

                          {/* Risk Metrics */}
                          <div className="flex flex-col gap-3 mb-5 pb-4 border-b border-white/10">
                            <div className="flex justify-between items-center">
                              <span className="text-sm text-gray-300 font-semibold">Risk Group:</span>
                              <span className={`text-sm font-bold flex items-center gap-1.5 px-2 py-0.5 rounded-md ${result.risk_group === 'High Risk' ? 'bg-red-500/20 text-red-400 border border-red-500/30' : result.risk_group === 'Elevated Risk' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' : result.risk_group === 'Uncertain' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'}`}>
                                <ShieldAlert size={14} />
                                {result.risk_group}
                              </span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-sm text-gray-300 font-semibold">Confidence:</span>
                              <span className="text-sm font-bold text-white">{result.confidence}</span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-sm text-gray-300 font-semibold">Compute Time:</span>
                              <span className="text-sm font-medium text-white flex items-center gap-1">
                                <Clock size={12} className="text-[#00D4FF]" />
                                {result.analysis_time}s
                              </span>
                            </div>
                          </div>

                          {/* Recommendation & Status */}
                          <div className="mb-5 pb-4 border-b border-white/10">
                            <p className="text-sm text-gray-200 font-semibold mb-2">Recommendation: <span className="text-white font-normal">{result.recommendation}</span></p>
                            <p className="text-xs text-gray-400 italic leading-relaxed">{result.status_message}</p>
                          </div>

                          <h4 className="text-xs font-semibold text-white mb-4 flex items-center gap-2 drop-shadow">
                            <Activity size={14} className="text-[#00D4FF]" /> 
                            Probability Distribution
                          </h4>
                          
                          <div className="space-y-4">
                            {Object.entries(result.probabilities)
                              .sort(([, a], [, b]) => (b as number) - (a as number))
                              .slice(0, 3)
                              .map(([className, prob], idx) => {
                                const percentage = ((prob as number) * 100).toFixed(1);
                                return (
                                  <div key={className} className="w-full">
                                    <div className="flex justify-between mb-1.5">
                                      <span className="text-xs font-medium text-white truncate pr-2 drop-shadow">{className}</span>
                                      <span className="text-xs font-bold text-[#00D4FF] drop-shadow">{percentage}%</span>
                                    </div>
                                    <div className="w-full bg-black/50 rounded-full h-1.5 overflow-hidden shadow-inner border border-white/5">
                                      <motion.div 
                                        initial={{ width: 0 }}
                                        animate={{ width: `${percentage}%` }}
                                        transition={{ duration: 1.5, delay: idx * 0.2, ease: "easeOut" }}
                                        className={`h-1.5 rounded-full shadow-[0_0_10px_currentColor] ${idx === 0 ? "bg-[#00D4FF]" : "bg-[#00D4FF]/40"}`}
                                      />
                                    </div>
                                  </div>
                                );
                              })}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                ) : (
                  <div className="w-full h-full flex flex-col items-center justify-center text-gray-400 bg-black/20 rounded-lg shadow-inner border border-white/5">
                    <div className="w-20 h-20 rounded-full border border-white/10 bg-white/5 flex items-center justify-center mb-6 shadow-xl relative overflow-hidden">
                      <div className="absolute inset-0 bg-[#00D4FF]/10 animate-pulse" />
                      <Search size={32} className="text-gray-300 relative z-10" />
                    </div>
                    <p className="text-base font-medium text-gray-200">No Image Provided</p>
                    <p className="text-sm mt-2 max-w-xs text-center">Upload a dermoscopic image to initiate the deep learning diagnostic pipeline.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Section 3: Why DermaScan / Model Card */}
      <section id="features" className="py-24 max-w-7xl mx-auto px-6 md:px-12 relative z-10">
        <div className="why-grid">
          <div className="glass p-10 bg-[#111827]/50 border border-white/10 rounded-2xl shadow-2xl">
            <div className="mb-8">
              <div className="flex items-center gap-2 font-mono text-xs tracking-widest uppercase text-[#38BDF8] mb-6">
                <span className="w-2 h-2 rounded-full bg-[#00D4FF] shadow-[0_0_12px_2px_rgba(0,212,255,0.7)]"></span>
                Why DermaScan
              </div>
              <h2 className="text-3xl font-bold font-display text-white">Designed around clinical trust</h2>
            </div>
            <ul className="why-list">
              <li>
                <div className="check"><CheckCircle2 size={14} /></div>
                <div>AI-powered screening<span className="desc">Consistent, repeatable first-pass triage of dermoscopy images</span></div>
              </li>
              <li>
                <div className="check"><CheckCircle2 size={14} /></div>
                <div>Explainable predictions<span className="desc">Every result ships with a visual rationale, not just a label</span></div>
              </li>
              <li>
                <div className="check"><CheckCircle2 size={14} /></div>
                <div>EfficientNet-B4 backbone<span className="desc">A compact, well-benchmarked architecture built for image fidelity</span></div>
              </li>
              <li>
                <div className="check"><CheckCircle2 size={14} /></div>
                <div>Clinical workflow support<span className="desc">Fits alongside existing dermatology review, not around it</span></div>
              </li>
              <li>
                <div className="check"><CheckCircle2 size={14} /></div>
                <div>Interactive visualization<span className="desc">Clinicians can inspect, compare, and question every prediction</span></div>
              </li>
            </ul>
          </div>

          <motion.div 
            className="glass model-card bg-[#111827]/50 border border-white/10 rounded-2xl shadow-2xl"
            style={{ rotateX: tilt1.rotateX, rotateY: tilt1.rotateY, transformPerspective: 1000 }}
            onMouseMove={tilt1.handleMouseMove}
            onMouseLeave={tilt1.handleMouseLeave}
          >
            <div className="badge">Model Card</div>
            <h3 className="text-white font-display">EfficientNet-B4, fine-tuned</h3>
            <p>Compound-scaled convolutional backbone, transfer-learned on ISIC dermoscopy data and fine-tuned for nine diagnostic categories.</p>
            <div className="model-bars">
              <div className="mbar-row">Accuracy<div className="mbar-track"><div className="mbar-fill" style={{width: '91%'}}></div></div>91%</div>
              <div className="mbar-row">Sensitivity<div className="mbar-track"><div className="mbar-fill" style={{width: '88%'}}></div></div>88%</div>
              <div className="mbar-row">Specificity<div className="mbar-track"><div className="mbar-fill" style={{width: '94%'}}></div></div>94%</div>
              <div className="mbar-row">AUC-ROC<div className="mbar-track"><div className="mbar-fill" style={{width: '96%'}}></div></div>0.96</div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Section 4: Pipeline & Tech Stack */}
      <section id="technology" className="py-24 max-w-7xl mx-auto px-6 md:px-12 relative z-10">
        <div className="mb-16">
          <div className="flex items-center gap-2 font-mono text-xs tracking-widest uppercase text-[#38BDF8] mb-6">
            <span className="w-2 h-2 rounded-full bg-[#00D4FF] shadow-[0_0_12px_2px_rgba(0,212,255,0.7)]"></span>
            Model pipeline
          </div>
          <h2 className="text-3xl font-bold font-display text-white mb-4 drop-shadow-md">From image to diagnosis, transparently</h2>
          <p className="text-gray-300 max-w-2xl">A single forward pass, six legible stages — no black box in between.</p>
        </div>

        <div className="glass bg-[#111827]/50 border border-white/10 rounded-2xl shadow-2xl mb-24" style={{padding: '36px 28px'}}>
          <div className="pipeline" id="pipeline">
            <div className="pipe-step">
              <div className="icon-wrap"><Scan size={24} /></div>
              <div className="t text-white">Dermoscopy Image</div>
              <div className="s">INPUT · 1024×1024</div>
            </div>
            <div className="pipe-arrow"><div className="flow"></div><svg viewBox="0 0 34 12" fill="none"><path d="M0 6h30" stroke="#00D4FF" strokeWidth="1.4"/><path d="M25 1l6 5-6 5" stroke="#00D4FF" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/></svg></div>

            <div className="pipe-step">
              <div className="icon-wrap"><Brain size={24} /></div>
              <div className="t text-white">EfficientNet-B4</div>
              <div className="s">CNN BACKBONE</div>
            </div>
            <div className="pipe-arrow"><div className="flow" style={{animationDelay: '.4s'}}></div><svg viewBox="0 0 34 12" fill="none"><path d="M0 6h30" stroke="#00D4FF" strokeWidth="1.4"/><path d="M25 1l6 5-6 5" stroke="#00D4FF" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/></svg></div>

            <div className="pipe-step">
              <div className="icon-wrap"><Network size={24} /></div>
              <div className="t text-white">Feature Fusion</div>
              <div className="s">MULTI-SCALE</div>
            </div>
            <div className="pipe-arrow"><div className="flow" style={{animationDelay: '.8s'}}></div><svg viewBox="0 0 34 12" fill="none"><path d="M0 6h30" stroke="#00D4FF" strokeWidth="1.4"/><path d="M25 1l6 5-6 5" stroke="#00D4FF" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/></svg></div>

            <div className="pipe-step">
              <div className="icon-wrap"><Layers size={24} /></div>
              <div className="t text-white">Dense Layer</div>
              <div className="s">FULLY CONNECTED</div>
            </div>
            <div className="pipe-arrow"><div className="flow" style={{animationDelay: '1.2s'}}></div><svg viewBox="0 0 34 12" fill="none"><path d="M0 6h30" stroke="#00D4FF" strokeWidth="1.4"/><path d="M25 1l6 5-6 5" stroke="#00D4FF" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/></svg></div>

            <div className="pipe-step">
              <div className="icon-wrap"><Activity size={24} /></div>
              <div className="t text-white">Softmax</div>
              <div className="s">PROBABILITY DIST.</div>
            </div>
            <div className="pipe-arrow"><div className="flow" style={{animationDelay: '1.6s'}}></div><svg viewBox="0 0 34 12" fill="none"><path d="M0 6h30" stroke="#00D4FF" strokeWidth="1.4"/><path d="M25 1l6 5-6 5" stroke="#00D4FF" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/></svg></div>

            <div className="pipe-step">
              <div className="icon-wrap"><CheckCircle2 size={24} /></div>
              <div className="t text-white">9 Diagnostic Classes</div>
              <div className="s">OUTPUT</div>
            </div>
          </div>
        </div>

        {/* Tech Stack */}
        <div className="mb-12">
          <div className="flex items-center gap-2 font-mono text-xs tracking-widest uppercase text-[#38BDF8] mb-6">
            <span className="w-2 h-2 rounded-full bg-[#00D4FF] shadow-[0_0_12px_2px_rgba(0,212,255,0.7)]"></span>
            Under the hood
          </div>
          <h2 className="text-3xl font-bold font-display text-white drop-shadow-md">Built on a proven research stack</h2>
        </div>
        <div className="chips">
          <div className="chip glass bg-[#111827]/50 border border-white/10 text-white"><Microchip size={18} />PyTorch</div>
          <div className="chip glass bg-[#111827]/50 border border-white/10 text-white"><Brain size={18} />EfficientNet-B4</div>
          <div className="chip glass bg-[#111827]/50 border border-white/10 text-white"><Network size={18} />Transfer Learning</div>
          <div className="chip glass bg-[#111827]/50 border border-white/10 text-white"><Crosshair size={18} />Grad-CAM</div>
          <div className="chip glass bg-[#111827]/50 border border-white/10 text-white"><Layers size={18} />ISIC Dataset</div>
          <div className="chip glass bg-[#111827]/50 border border-white/10 text-white"><Activity size={18} />Python</div>
          <div className="chip glass bg-[#111827]/50 border border-white/10 text-white"><Scan size={18} />FastAPI</div>
        </div>
      </section>

      {/* Section 5: Explainable AI - ✅ 3D Tilt */}
      <section id="model" className="py-32 max-w-7xl mx-auto px-6 md:px-12 relative z-10">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <div>
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-white/20 mb-8 shadow-xl">
              <Microchip size={16} className="text-[#00D4FF] animate-pulse" />
              <span className="text-xs font-bold text-white tracking-widest uppercase drop-shadow-md">Explainable AI</span>
            </div>
            <h2 className="text-4xl font-bold font-display mb-6 drop-shadow-lg leading-tight">Transparent Clinical Decisions</h2>
            <p className="text-gray-300 leading-relaxed mb-6 text-lg">
              Our models don't just output a prediction. Using Gradient-weighted Class Activation Mapping (Grad-CAM), DermaScan AI highlights the exact pixel regions of the lesion that influenced the model's decision.
            </p>
            <p className="text-gray-400 leading-relaxed mb-10">
              This visual explanation ensures that dermatologists can trust the AI by verifying its focal points align with clinical pathology markers.
            </p>
            <button onClick={scrollToScanner} className="clinical-button-primary px-8 py-3 text-base shadow-[0_10px_30px_rgba(0,212,255,0.3)]">
              Try the Heatmap
            </button>
          </div>

          <motion.div 
            className="relative"
            style={{ rotateX: tilt3.rotateX, rotateY: tilt3.rotateY, transformPerspective: 1000 }}
            onMouseMove={tilt3.handleMouseMove}
            onMouseLeave={tilt3.handleMouseLeave}
          >
            <div className="absolute inset-0 bg-[#00D4FF]/20 rounded-3xl blur-[100px] -z-10 animate-pulse" />
            <div className="premium-card p-3 flex gap-4 overflow-hidden border-t border-l border-white/30 bg-[#0d1928]/60 shadow-[0_30px_60px_rgba(0,0,0,0.6)]">
              <div className="flex-1 rounded-xl overflow-hidden relative group border border-white/10 shadow-inner">
                <img src="/bio-ml-demo.png" alt="Original" className="w-full h-auto object-cover aspect-video brightness-90 group-hover:scale-105 transition-transform duration-700" />
                <div className="absolute bottom-4 left-4 bg-black/60 backdrop-blur-md text-white text-[10px] px-3 py-1.5 rounded-md font-bold uppercase tracking-wider border border-white/20 shadow-lg">Original Dataset Image</div>
              </div>
              <div className="flex-1 rounded-xl overflow-hidden relative group border border-white/10 shadow-inner">
                <img src="/bio-ml-demo.png" alt="Heatmap" className="w-full h-auto object-cover aspect-video brightness-90 group-hover:scale-105 transition-transform duration-700" />
                {/* Simulated Heatmap Layer */}
                <div className="absolute inset-0 bg-gradient-to-tr from-blue-600/60 via-green-500/70 to-red-600/90 mix-blend-screen opacity-90 group-hover:opacity-100 transition-opacity" />
                <div className="absolute bottom-4 left-4 bg-black/60 backdrop-blur-md text-white text-[10px] px-3 py-1.5 rounded-md font-bold uppercase tracking-wider border border-white/20 shadow-lg">Grad-CAM Overlay</div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer id="team" className="py-24 relative z-20">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <div className="glass foot-card bg-[#111827]/80 backdrop-blur-3xl border border-white/10 shadow-2xl rounded-3xl">
            
            <div className="foot-top">
              <div className="foot-tagline text-white">Built for the future of <span className="grad">AI-assisted dermatology.</span></div>
              <div className="qr shadow-[0_0_20px_rgba(255,255,255,0.1)]" aria-label="QR code placeholder">
                <div></div><div className="off"></div><div></div><div></div><div className="off"></div><div></div>
                <div className="off"></div><div></div><div className="off"></div><div className="off"></div><div></div><div className="off"></div>
                <div></div><div></div><div></div><div className="off"></div><div></div><div></div>
                <div className="off"></div><div className="off"></div><div></div><div></div><div className="off"></div><div></div>
                <div></div><div className="off"></div><div className="off"></div><div></div><div className="off"></div><div></div>
                <div className="off"></div><div></div><div></div><div className="off"></div><div></div><div className="off"></div>
              </div>
            </div>

            <div className="foot-mid">
              <div className="foot-col">
                <h5>Research Team</h5>
                <div className="team-list">
                  <div>Jay Panchal</div>
                  <div>Souradeep Das</div>
                  <div>Vivek Garai</div>
                </div>
              </div>
              <div className="foot-col">
                <h5>Stack</h5>
                <div className="badges">
                  <span className="badge-sm bg-white/5">PyTorch</span>
                  <span className="badge-sm bg-white/5">EfficientNet-B4</span>
                  <span className="badge-sm bg-white/5">Grad-CAM</span>
                  <span className="badge-sm bg-white/5">ISIC Dataset</span>
                  <span className="badge-sm bg-white/5">FastAPI</span>
                </div>
              </div>
              <div className="foot-col">
                <h5>Presented at</h5>
                <div className="team-list">
                  <div className="text-white font-medium">International Medical AI Symposium</div>
                  <div>2026</div>
                </div>
              </div>
            </div>

            <div className="foot-bottom">
              <div>© 2026 DermaScan AI · Research Prototype</div>
              <div className="font-mono text-[10px] tracking-widest uppercase">FOR RESEARCH USE ONLY — NOT A CLINICAL DIAGNOSTIC DEVICE</div>
            </div>
          </div>
        </div>
      </footer>

    </div>
  );
}
