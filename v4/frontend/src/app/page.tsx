"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence, useScroll, useTransform, useMotionValue, useSpring } from "framer-motion";
import { Upload, Activity, ShieldAlert, Clock, Scan, Sparkles, CheckCircle2, Menu, X, ArrowRight, Microchip, Layers, Brain, Search, Crosshair, Network, AlertTriangle, FileText, Shield, Info, ChevronDown, GripVertical, ChevronRight } from "lucide-react";
import Link from "next/link";

// ── V3 Constants ────────────────────────────────────────────────────────────
const V3_SITES = [
  "Anterior torso",
  "Head/neck",
  "Lateral torso",
  "Lower extremity",
  "Oral/genital",
  "Palms/soles",
  "Posterior torso",
  "Upper extremity",
];

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ── Risk Badge Styling ──────────────────────────────────────────────────────
function getRiskStyles(riskGroup: string, riskColor: string) {
  switch (riskColor) {
    case "red":
      return "bg-red-500/20 text-red-400 border border-red-500/30";
    case "orange":
      return "bg-orange-500/20 text-orange-400 border border-orange-500/30";
    case "green":
      return "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
    case "yellow":
      return "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30";
    case "grey":
    default:
      return "bg-gray-500/20 text-gray-400 border border-gray-500/30";
  }
}

export default function LandingAndDashboard() {
  // Navigation State
  const [isNavScrolled, setIsNavScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Dashboard State
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [result, setResult] = useState<any>(null);

  // V4 State — V3 metadata inputs
  const [age, setAge] = useState(50);
  const [sex, setSex] = useState("Female");
  const [site, setSite] = useState("Anterior torso");
  const [demoMode, setDemoMode] = useState(false);

  // Spotlight Cursor State
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // Modal State
  const [activeModal, setActiveModal] = useState<{ title: string; content: React.ReactNode } | null>(null);
  const [activeTooltip, setActiveTooltip] = useState<string | null>(null);
  const [expandedFeature, setExpandedFeature] = useState<number | null>(null);
  
  // Custom synced cursor for Explainability
  const [heatmapCursor, setHeatmapCursor] = useState<{ x: number, y: number, show: boolean }>({ x: 0, y: 0, show: false });
  const [sliderValue, setSliderValue] = useState(50);

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

  // ── V4 Analysis Handler — calls FastAPI with V3 metadata ──────────────────
  const handleAnalyze = async () => {
    if (!selectedImage) return;
    setIsScanning(true);
    setResult(null);
    
    const formData = new FormData();
    formData.append("file", selectedImage);
    formData.append("age", age.toString());
    formData.append("sex", sex);
    formData.append("site", site);
    formData.append("demo_mode", demoMode.toString());
    
    try {
      const res = await fetch(`${API_BASE}/api/analyze`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Analysis failed");
      }
      const data = await res.json();
      setResult(data);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
      console.error("Analysis failed:", error);
      setResult({ error: error.message || "Failed to connect to the API. Is the backend running?" });
    } finally {
      setIsScanning(false);
    }
  };

  // ── PDF Download ──────────────────────────────────────────────────────────
  const handleDownloadPDF = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/download-report`);
      if (!res.ok) throw new Error("Report not available");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "DermaScan_V4_Clinical_Report.pdf";
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("PDF download failed:", error);
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
            <span className="font-bold text-2xl tracking-tight font-display text-white group-hover:text-gray-300 transition-colors">DermaScan AI <span className="text-[#00D4FF] text-lg font-medium">V4</span></span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            <Link href="#technology" className="text-[var(--color-text-secondary)] hover:text-white text-sm font-medium transition-colors hover:shadow-[0_0_10px_rgba(0,212,255,0.2)] px-3 py-1 rounded-md">Technology</Link>
            <Link href="#model" className="text-[var(--color-text-secondary)] hover:text-white text-sm font-medium transition-colors hover:shadow-[0_0_10px_rgba(0,212,255,0.2)] px-3 py-1 rounded-md">Model</Link>
            <Link href="#features" className="text-[var(--color-text-secondary)] hover:text-white text-sm font-medium transition-colors hover:shadow-[0_0_10px_rgba(0,212,255,0.2)] px-3 py-1 rounded-md">Features</Link>
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
                <span className="text-xs font-semibold text-[#00D4FF] tracking-wide uppercase">Multi-Modal Deep Learning</span>
              </div>
              
              <h1 className="text-5xl md:text-7xl font-bold font-display leading-[1.1] mb-6 tracking-tight text-white drop-shadow-2xl">
                AI-Powered Skin Lesion Screening
              </h1>
              
              <p className="text-lg md:text-xl text-[var(--color-text-secondary)] font-light leading-relaxed mb-10 max-w-xl backdrop-blur-sm bg-[#050816]/10 p-2 rounded-lg">
                Upload a dermoscopic image and let DermaScan AI V4 perform multi-modal analysis combining image features with clinical metadata — powered by explainable AI and clinical decision support.
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

          {/* Right: Cinematic Scanning Demo — ✅ 3D Tilt */}
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
                <span className="text-sm font-medium tracking-wide text-white">Multi-Modal Neural Network</span>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </section>

      {/* ✅ Medical Dashboard UI Section — V4 Enhanced */}
      <section id="dashboard-scanner" className="scroll-mt-24 py-24 bg-[#0B1120]/40 backdrop-blur-lg border-t border-b border-white/5 relative z-20 shadow-[0_0_50px_rgba(0,0,0,0.5)]">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          
          {/* Disclaimer Banner */}
          <div className="disclaimer-banner mb-8">
            ⚠️ ACADEMIC PROTOTYPE – Not for clinical use. This tool is designed to assist, not replace, a medical professional.
          </div>

          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold font-display mb-4 drop-shadow-lg">Clinical Diagnostic Terminal</h2>
            <p className="text-[var(--color-text-secondary)]">Secure, real-time multi-modal image analysis pipeline.</p>
          </div>

          <div className="grid lg:grid-cols-12 gap-8">
            
            {/* Left Panel: Inputs (4 Columns) — ✅ 3D Tilt + V4 metadata inputs */}
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
                  {/* V4: Age Input */}
                  <div>
                    <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">Patient Age</label>
                    <input
                      type="number"
                      value={age}
                      onChange={(e) => setAge(Math.max(0, Math.min(120, parseInt(e.target.value) || 0)))}
                      min={0}
                      max={120}
                      className="clinical-input w-full bg-[#050816]/80 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-[#00D4FF]/60 focus:shadow-[0_0_15px_rgba(0,212,255,0.3)] transition-all"
                    />
                  </div>

                  {/* Sex Selection */}
                  <div>
                    <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">Patient Sex</label>
                    <select 
                      value={sex}
                      onChange={(e) => setSex(e.target.value)}
                      className="w-full bg-[#050816]/80 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-[#00D4FF]/60 focus:shadow-[0_0_15px_rgba(0,212,255,0.3)] transition-all"
                    >
                      <option value="Female">Female</option>
                      <option value="Male">Male</option>
                    </select>
                  </div>

                  {/* V4: Anatomical Site — V3's 8 categories */}
                  <div>
                    <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">Anatomical Site</label>
                    <select 
                      value={site}
                      onChange={(e) => setSite(e.target.value)}
                      className="w-full bg-[#050816]/80 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-[#00D4FF]/60 focus:shadow-[0_0_15px_rgba(0,212,255,0.3)] transition-all"
                    >
                      {V3_SITES.map((s) => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Image Upload */}
                <div className="mt-8 pt-6 border-t border-white/10">
                  <label 
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`block w-full h-32 border-2 border-dashed rounded-xl flex flex-col items-center justify-center cursor-pointer transition-all duration-300 ${isDragging ? "border-[#00D4FF] bg-[#00D4FF]/10 scale-[1.02] shadow-[0_0_20px_rgba(0,212,255,0.2)]" : "border-white/20 hover:border-[#00D4FF]/60 hover:bg-white/5"}`}
                  >
                    <Upload size={28} className={`mb-2 transition-all ${isDragging ? "text-[#00D4FF] scale-110" : "text-gray-400"}`} />
                    <span className="text-sm font-medium text-white drop-shadow">Upload Lesion Image</span>
                    <span className="text-xs text-gray-400 mt-1">JPEG, PNG up to 10MB</span>
                    <input type="file" className="hidden" accept="image/*" onChange={handleImageUpload} />
                  </label>
                </div>

                {/* V4: Demo Mode Toggle */}
                <div className="mt-5 flex items-center justify-between px-1">
                  <div>
                    <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Demo Mode</span>
                    <p className="text-[10px] text-gray-500 mt-0.5">Lower threshold (0.5)</p>
                  </div>
                  <button
                    onClick={() => setDemoMode(!demoMode)}
                    className={`toggle-switch ${demoMode ? 'active' : ''}`}
                    aria-label="Toggle demo mode"
                  />
                </div>

                {/* Action Buttons */}
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
                      <><Scan size={16} className="animate-spin" /> Analyzing...</>
                    ) : (
                      "Initialize Scan"
                    )}
                  </button>
                </div>
              </div>
            </motion.div>

            {/* Right Panel: Viewer (8 Columns) — ✅ Glassmorphism & Heatmap Overlay */}
            <div className="lg:col-span-8 flex flex-col gap-6 relative">
              <div className="premium-card p-3 h-[600px] flex relative overflow-hidden bg-[#050816]/60 border-t border-l border-white/20 shadow-2xl">
                {previewUrl ? (
                  <div className="w-full h-full flex gap-4 transition-all duration-200 ease-in-out">
                    {/* Visual Canvas (Left) */}
                    <div className={`relative rounded-xl overflow-hidden flex items-center justify-center bg-black/60 shadow-inner transition-all duration-200 ease-in-out ${result && !result.error && !isScanning ? 'flex-1' : 'w-full h-full'}`}>
                      <img src={previewUrl} alt="Preview" className="max-w-full max-h-full object-contain" />
                      
                      {/* ✅ Animated AI Scan Line */}
                      {isScanning && <div className="scan-line" />}
                      
                      {/* ✅ Animated Real Heatmap Overlay from V3 Grad-CAM */}
                      <AnimatePresence>
                        {result?.heatmap && !isScanning && (
                          <motion.img 
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 0.85 }}
                            transition={{ duration: 1.5, ease: "easeInOut" }}
                            src={result.heatmap} 
                            className="absolute inset-0 w-full h-full object-contain mix-blend-screen"
                            alt="V3 Grad-CAM Heatmap"
                          />
                        )}
                      </AnimatePresence>

                      {/* Error Display */}
                      <AnimatePresence>
                        {result?.error && !isScanning && (
                          <motion.div 
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="absolute bottom-6 right-6 left-6 bg-red-900/80 backdrop-blur-xl rounded-2xl p-6 border border-red-500/30"
                          >
                            <div className="flex items-center gap-3 text-red-300">
                              <AlertTriangle size={20} />
                              <span className="text-sm font-medium">{result.error}</span>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>

                    {/* Diagnostic Metrics Panel (Right) */}
                    <AnimatePresence>
                      {result && !result.error && !isScanning && (
                        <motion.div 
                          initial={{ opacity: 0, x: 20, width: 0 }}
                          animate={{ opacity: 1, x: 0, width: 380 }}
                          exit={{ opacity: 0, width: 0 }}
                          transition={{ type: "spring", bounce: 0.4 }}
                          className="h-full overflow-y-auto bg-[#050816]/90 backdrop-blur-3xl rounded-2xl p-6 border border-white/20 shadow-[0_30px_60px_rgba(0,0,0,0.8)] shrink-0"
                        >
                          {/* Skin Lesion Warning */}
                          {result.skin_lesion_warning && (
                            <div className="skin-warning w-full mb-4">
                              <Shield size={14} />
                              <span>Image variance is low. This may not be a skin lesion.</span>
                            </div>
                          )}

                          {/* Diagnostic Interpretation Header */}
                          <div className="mb-4 pb-4 border-b border-white/10">
                            <h3 className="text-lg font-bold text-white mb-1">
                              Diagnostic Interpretation: <span className="text-[#00D4FF] drop-shadow">{result.top_diagnosis}</span>
                            </h3>
                            <span className="text-xs text-gray-300 font-mono">{result.top_abbreviation}</span>
                          </div>

                          {/* Safety Net Warning */}
                          {result.is_uncertain && (
                            <div className="safety-warning mb-4">
                              <AlertTriangle size={16} />
                              <span>Insufficient confidence — consult a dermatologist</span>
                            </div>
                          )}

                          {/* Risk Metrics */}
                          <div className="flex flex-col gap-3 mb-5 pb-4 border-b border-white/10">
                            <div className="flex justify-between items-center">
                              <span className="text-sm text-gray-200 font-semibold">Risk Group:</span>
                              <span className={`text-sm font-bold flex items-center gap-1.5 px-2 py-0.5 rounded-md ${getRiskStyles(result.risk_group, result.risk_color)}`}>
                                <ShieldAlert size={14} />
                                {result.risk_group}
                              </span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-sm text-gray-200 font-semibold">Confidence:</span>
                              <span className="text-sm font-bold text-white">{result.confidence}</span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-sm text-gray-200 font-semibold">Compute Time:</span>
                              <span className="text-sm font-medium text-white flex items-center gap-1">
                                <Clock size={12} className="text-[#00D4FF]" />
                                {result.analysis_time}s
                              </span>
                            </div>
                          </div>

                          {/* Recommendation & Status */}
                          <div className="mb-5 pb-4 border-b border-white/10">
                            <p className="text-sm text-gray-200 font-semibold mb-2">Recommendation: <span className="text-white font-normal">{result.recommendation}</span></p>
                            <p className="text-xs text-gray-300 italic leading-relaxed">{result.status_message}</p>
                          </div>

                          {/* ✅ V4: All 8 Class Probability Bars */}
                          <h4 className="text-xs font-semibold text-white mb-4 flex items-center gap-2 drop-shadow">
                            <Activity size={14} className="text-[#00D4FF]" /> 
                            Differential Diagnosis Probabilities
                          </h4>
                          
                          <div className="space-y-3">
                            {Object.entries(result.probabilities)
                              .sort(([, a], [, b]) => (b as number) - (a as number))
                              .map(([className, prob], idx) => {
                                const percentage = ((prob as number) * 100).toFixed(1);
                                const isTop = idx === 0;
                                return (
                                  <div key={className} className="w-full">
                                    <div className="flex justify-between mb-1.5">
                                      <span className="text-xs font-medium text-white truncate pr-2 drop-shadow">{className}</span>
                                      <span className={`text-xs font-bold drop-shadow ${isTop ? 'text-[#00D4FF]' : 'text-gray-300'}`}>{percentage}%</span>
                                    </div>
                                    <div className="w-full bg-black/50 rounded-full h-1.5 overflow-hidden shadow-inner border border-white/5">
                                      <motion.div 
                                        initial={{ width: 0 }}
                                        animate={{ width: `${percentage}%` }}
                                        transition={{ duration: 1.5, delay: idx * 0.1, ease: "easeOut" }}
                                        className={`h-1.5 rounded-full ${isTop ? "bg-[#00D4FF] shadow-[0_0_10px_#00D4FF]" : "bg-[#00D4FF]/30"}`}
                                      />
                                    </div>
                                  </div>
                                );
                              })}
                          </div>

                          {/* ✅ V4: PDF Download Button */}
                          {result.pdf_available && (
                            <button 
                              onClick={handleDownloadPDF}
                              className="download-button mt-5"
                            >
                              <FileText size={16} />
                              Download Clinical Report (PDF)
                            </button>
                          )}
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
                    <p className="text-sm mt-2 max-w-xs text-center">Upload a dermoscopic image to initiate the multi-modal diagnostic pipeline.</p>
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
                Why DermaScan V4
              </div>
              <h2 className="text-3xl font-bold font-display text-white">Designed around clinical trust</h2>
            </div>
            <div className="flex flex-col gap-4">
              {[
                { title: "Multi-modal analysis", hiddenText: "Combines visual scan data with patient details (age, sex, anatomical site) to dramatically boost diagnostic accuracy beyond standard image-only models." },
                { title: "Explainable predictions", hiddenText: "Highlights the exact pixel regions that influenced the AI, making the model's decision transparent, verifiable, and easy to interpret." },
                { title: "Clinical safety net", hiddenText: "Flags uncertain or low-confidence cases, automatically recommending a dermatologist review to ensure patient safety." },
                { title: "4-tier risk classification", hiddenText: "Categorizes lesions into four clear risk levels (from Benign to Malignant) with actionable, color-coded medical recommendations." },
                { title: "Clinical PDF reports", hiddenText: "Generates instant, downloadable medical reports containing the diagnosis, heatmaps, and patient data for easy clinical record-keeping." },
              ].map((feat, i) => (
                <div 
                  key={i}
                  onClick={() => setExpandedFeature(expandedFeature === i ? null : i)}
                  className="group flex flex-col p-4 rounded-xl border border-white/10 bg-white/5 hover:bg-[#00D4FF]/5 hover:border-[#00D4FF]/40 hover:shadow-[0_0_20px_rgba(0,212,255,0.15)] transition-all duration-300 cursor-pointer overflow-hidden"
                >
                  <div className="flex flex-row items-center justify-between w-full">
                    <div className="flex items-center gap-4">
                      <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-blue-600/20 to-[#00D4FF]/20 border border-[#00D4FF]/30 flex items-center justify-center text-[#00D4FF] group-hover:text-white group-hover:shadow-[0_0_15px_rgba(0,212,255,0.5)] transition-all">
                        <CheckCircle2 size={20} />
                      </div>
                      <h4 className="text-white font-semibold text-lg group-hover:text-[#00D4FF] transition-colors">{feat.title}</h4>
                    </div>
                    <ChevronDown size={20} className={`text-gray-400 group-hover:text-[#00D4FF] transition-transform duration-300 ${expandedFeature === i ? 'rotate-180' : ''}`} />
                  </div>
                  <AnimatePresence>
                    {expandedFeature === i && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3, ease: "easeInOut" }}
                      >
                        <p className="text-gray-300 text-sm leading-relaxed mt-4 pl-14 pr-4 pb-2">{feat.hiddenText}</p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ))}
            </div>
          </div>

          <motion.div 
            className="glass model-card bg-[#111827]/50 border border-white/10 rounded-2xl shadow-2xl"
            style={{ rotateX: tilt1.rotateX, rotateY: tilt1.rotateY, transformPerspective: 1000 }}
            onMouseMove={tilt1.handleMouseMove}
            onMouseLeave={tilt1.handleMouseLeave}
          >
            <div className="badge">Model Card — V3 Engine</div>
            <h3 className="text-white font-display">EfficientNet-B4, multi-modal</h3>
            <p>Compound-scaled convolutional backbone with metadata fusion, transfer-learned on ISIC dermoscopy data. 8 diagnostic categories with clinical risk mapping.</p>
            <div className="flex flex-col gap-6 mt-6">
              {/* Percentage Metrics (Accuracy) */}
              <div className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-300 font-medium">Accuracy (full test)</span>
                    <span className="text-[#00D4FF] font-mono font-semibold">65.7%</span>
                  </div>
                  <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden shadow-inner">
                    <div className="h-full bg-gradient-to-r from-blue-600 to-[#00D4FF] rounded-full shadow-[0_0_10px_rgba(0,212,255,0.5)]" style={{ width: '65.7%' }} />
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-300 font-medium">Accuracy (balanced)</span>
                    <span className="text-[#00D4FF] font-mono font-semibold">67.75%</span>
                  </div>
                  <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden shadow-inner">
                    <div className="h-full bg-gradient-to-r from-blue-600 to-[#00D4FF] rounded-full shadow-[0_0_10px_rgba(0,212,255,0.5)]" style={{ width: '67.75%' }} />
                  </div>
                </div>
              </div>
              
              {/* Categorical / Integer Metrics */}
              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-white/10">
                <div className="flex flex-col gap-1">
                  <span className="text-gray-400 text-xs uppercase tracking-wider font-semibold">Diagnostic Classes</span>
                  <span className="text-white font-mono text-lg font-bold">8</span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-gray-400 text-xs uppercase tracking-wider font-semibold">Input Modalities</span>
                  <div className="flex gap-2">
                    <span className="bg-[#00D4FF]/10 text-[#00D4FF] border border-[#00D4FF]/20 px-2.5 py-0.5 rounded-md text-xs font-mono font-bold">Image</span>
                    <span className="bg-[#00D4FF]/10 text-[#00D4FF] border border-[#00D4FF]/20 px-2.5 py-0.5 rounded-md text-xs font-mono font-bold">Metadata</span>
                  </div>
                </div>
              </div>
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
          <p className="text-gray-300 max-w-2xl">A single forward pass through a multi-modal network — image features fused with clinical metadata for context-aware predictions.</p>
        </div>

        <div className="glass bg-[#111827]/50 border border-white/10 rounded-2xl shadow-2xl mb-24" style={{padding: '36px 28px'}}>
          <div className="pipeline" id="pipeline">
            {[
              { 
                icon: Scan, title: "Dermoscopy Image", sub: "INPUT · 224×224", 
                modal: <><p className="mb-3 text-gray-300"><strong>Overview:</strong> The high-resolution, magnified starting picture of the skin lesion.</p><p className="text-gray-400"><strong>Technical Detail:</strong> Accepts raw image inputs, resizing them to 224x224 RGB tensors. The data pipeline applies standard normalization and center-cropping to prepare the visual matrix for the convolutional network.</p></>
              },
              { arrow: true },
              { 
                icon: Brain, title: "EfficientNet-B4", sub: "CNN BACKBONE", 
                modal: <><p className="mb-3 text-gray-300"><strong>Overview:</strong> The primary AI "brain" that scans the image for dangerous visual patterns, like irregular borders or uneven colors.</p><p className="text-gray-400"><strong>Technical Detail:</strong> A compound-scaled Convolutional Neural Network (CNN) that acts as the primary feature extractor, systematically balancing network depth, width, and resolution for maximum accuracy without extreme compute costs.</p></>
              },
              { arrow: true },
              { 
                icon: Network, title: "Metadata Fusion", sub: "AGE · SEX · SITE", 
                modal: <><p className="mb-3 text-gray-300"><strong>Overview:</strong> The step where the AI combines the picture with the patient’s age, sex, and where the mole is located on the body.</p><p className="text-gray-400"><strong>Technical Detail:</strong> A custom fusion layer that concatenates the flattened visual feature vectors from the CNN with the encoded categorical and numerical patient metadata, creating a unified context-aware tensor.</p></>
              },
              { arrow: true },
              { 
                icon: Layers, title: "Dense Classifier", sub: "FULLY CONNECTED", 
                modal: <><p className="mb-3 text-gray-300"><strong>Overview:</strong> The decision-making center that weighs all the visual and patient evidence to make a final call.</p><p className="text-gray-400"><strong>Technical Detail:</strong> A fully connected neural network stack utilizing ReLU activation and strategic Dropout layers to prevent overfitting, mapping the fused high-dimensional data down to the final diagnostic outputs.</p></>
              },
              { arrow: true },
              { 
                icon: Activity, title: "Softmax", sub: "PROBABILITY DIST.", 
                modal: <><p className="mb-3 text-gray-300"><strong>Overview:</strong> The calculator that converts the AI's raw thoughts into easy-to-read percentages (e.g., 85% Melanoma, 15% Benign).</p><p className="text-gray-400"><strong>Technical Detail:</strong> The final activation function that normalizes the raw output logits into a probability distribution that sums exactly to 1.0 (100%) across all possible classes.</p></>
              },
              { arrow: true },
              { 
                icon: CheckCircle2, title: "8 Diagnostic Classes", sub: "+ CLINICAL MAPPING", 
                modal: <><p className="mb-3 text-gray-300"><strong>Overview:</strong> The final output placing the lesion into one of eight distinct medical categories, ranging from completely harmless to high-risk cancers.</p><p className="text-gray-400"><strong>Technical Detail:</strong> Maps the maximum probability to one of the ISIC dataset classes: Melanoma, Melanocytic Nevus, Basal Cell Carcinoma, Actinic Keratosis, Benign Keratosis, Dermatofibroma, Vascular Lesion, or Squamous Cell Carcinoma.</p></>
              }
            ].map((step, idx) => {
              if (step.arrow) {
                return (
                  <div key={idx} className="pipe-arrow relative flex items-center justify-center w-8 px-2 text-[#00D4FF]/30">
                    <ChevronRight size={24} />
                  </div>
                );
              }
              const Icon = step.icon!;
              return (
                <div 
                  key={idx} 
                  onClick={() => setActiveModal({ title: step.title!, content: step.modal! })}
                  className="pipe-step group cursor-pointer hover:scale-[1.05] transition-transform duration-200"
                >
                  <motion.div 
                    className="icon-wrap group-hover:bg-[#00D4FF]/20 group-hover:border-[#00D4FF]/60 group-hover:shadow-[0_0_20px_rgba(0,212,255,0.5)] transition-all"
                    animate={{
                      boxShadow: ["0 0 0px transparent", "0 0 15px rgba(0,212,255,0.6)", "0 0 0px transparent"],
                      borderColor: ["rgba(255,255,255,0.1)", "rgba(0,212,255,0.6)", "rgba(255,255,255,0.1)"],
                      backgroundColor: ["rgba(17,24,39,0.5)", "rgba(0,212,255,0.15)", "rgba(17,24,39,0.5)"]
                    }}
                    transition={{
                      duration: 2.5,
                      repeat: Infinity,
                      delay: (idx / 2) * 0.4,
                      ease: "easeInOut"
                    }}
                  >
                    <Icon size={24} className="group-hover:animate-pulse group-hover:text-white" />
                  </motion.div>
                  <div className="t text-white group-hover:text-[#00D4FF] transition-colors">{step.title}</div>
                  <div className="s group-hover:text-gray-300 transition-colors">{step.sub}</div>
                </div>
              );
            })}
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
          {[
            { icon: Microchip, label: "TensorFlow/Keras", tip: "Deep learning framework used to train and export the primary classification model." },
            { icon: Brain, label: "EfficientNet-B4", tip: "State-of-the-art CNN architecture balancing accuracy and computational efficiency." },
            { icon: Network, label: "Multi-Modal Fusion", tip: "Custom architecture combining image feature vectors with patient demographics." },
            { icon: Crosshair, label: "Grad-CAM", tip: "Gradient-weighted Class Activation Mapping for visual model explainability." },
            { icon: Layers, label: "ISIC Dataset", tip: "Trained on the International Skin Imaging Collaboration archive." },
            { icon: Activity, label: "Python + FastAPI", tip: "High-performance asynchronous backend API serving the model." },
            { icon: Scan, label: "Next.js + React", tip: "Modern React framework for the interactive, server-rendered frontend." }
          ].map((chip, idx) => {
            const Icon = chip.icon;
            return (
              <div 
                key={idx} 
                className="chip glass bg-[#111827]/50 border border-white/10 text-white cursor-pointer hover:border-[#00D4FF]/40 hover:shadow-[0_10px_30px_-8px_rgba(0,212,255,0.4)] relative group"
                onMouseEnter={() => setActiveTooltip(chip.label)}
                onMouseLeave={() => setActiveTooltip(null)}
              >
                <Icon size={18} className="group-hover:text-[#00D4FF] transition-colors" />
                {chip.label}
                <AnimatePresence>
                  {activeTooltip === chip.label && (
                    <motion.div 
                      initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }} transition={{ duration: 0.15 }}
                      className="absolute bottom-full mb-3 left-1/2 -translate-x-1/2 w-48 p-3 bg-[#0B1120] border border-[#00D4FF]/40 rounded-xl shadow-[0_10px_30px_rgba(0,0,0,0.5)] text-xs text-gray-200 text-center z-50 pointer-events-none"
                    >
                      {chip.tip}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            );
          })}
        </div>
      </section>

      {/* Section 5: Explainable AI — Before/After Slider */}
      <section id="model" className="py-32 max-w-7xl mx-auto px-6 md:px-12 relative z-10">
        <div className="flex flex-col gap-10">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-white/20 mb-8 shadow-xl">
              <Microchip size={16} className="text-[#00D4FF] animate-pulse" />
              <span className="text-xs font-bold text-white tracking-widest uppercase drop-shadow-md">Explainable AI</span>
            </div>
            <h2 className="text-4xl font-bold font-display mb-6 drop-shadow-lg leading-tight">Transparent Clinical Decisions</h2>
            <p className="text-gray-300 leading-relaxed mb-6 text-lg">
              Our model doesn&apos;t just output a prediction. Using Gradient-weighted Class Activation Mapping (Grad-CAM) on the <code className="text-[#00D4FF] bg-white/5 px-1.5 py-0.5 rounded text-sm">top_conv</code> layer, DermaScan AI V4 highlights the exact pixel regions that influenced the model&apos;s decision.
            </p>
            <p className="text-gray-400 leading-relaxed mb-10">
              Combined with multi-modal metadata fusion (age, sex, anatomical site), the model provides context-aware predictions with a clinical safety net that flags uncertain cases for dermatologist review.
            </p>
            <button onClick={scrollToScanner} className="clinical-button-primary px-8 py-3 text-base shadow-[0_10px_30px_rgba(0,212,255,0.3)]">
              Try the Heatmap
            </button>
          </div>

          <motion.div 
            className="relative w-full max-w-4xl mx-auto aspect-video rounded-2xl overflow-hidden border border-white/30 bg-[#0d1928] shadow-[0_30px_60px_rgba(0,0,0,0.6)] group"
          >
            {/* Bottom Layer: Original Image */}
            <div className="absolute inset-0">
              <img src="/demo_original.jpg" alt="Original" className="w-full h-full object-cover pointer-events-none" />
              <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-md text-white text-[10px] px-3 py-1.5 rounded-md font-bold uppercase tracking-wider border border-white/20 shadow-lg pointer-events-none z-10">Original Image</div>
            </div>

            {/* Top Layer: Heatmap */}
            <div 
              className="absolute inset-0 z-10 pointer-events-none"
              style={{ clipPath: `inset(0 ${100 - sliderValue}% 0 0)` }}
            >
              <img src="/demo_heatmap.jpg" alt="Heatmap" className="w-full h-full object-cover" />
              <div className="absolute top-4 right-4 bg-[#00D4FF]/20 text-[#00D4FF] backdrop-blur-md text-[10px] px-3 py-1.5 rounded-md font-bold uppercase tracking-wider border border-[#00D4FF]/40 shadow-[0_0_15px_rgba(0,212,255,0.3)] z-10">Grad-CAM Overlay</div>
            </div>

            {/* Slider Handle UI */}
            <div 
              className="absolute top-0 bottom-0 z-20 w-1 bg-white flex items-center justify-center pointer-events-none shadow-[0_0_10px_rgba(0,0,0,0.8)]"
              style={{ left: `${sliderValue}%`, transform: 'translateX(-50%)' }}
            >
              <div className="w-10 h-10 bg-white text-[#0B1120] rounded-full flex items-center justify-center shadow-[0_0_20px_rgba(0,0,0,0.5)]">
                <GripVertical size={20} />
              </div>
            </div>

            {/* Invisible Range Input */}
            <input 
              type="range"
              min="0"
              max="100"
              value={sliderValue}
              onChange={(e) => setSliderValue(Number(e.target.value))}
              className="absolute inset-0 w-full h-full opacity-0 z-30 cursor-ew-resize m-0 p-0"
            />
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
                  <span className="badge-sm bg-white/5">TensorFlow/Keras</span>
                  <span className="badge-sm bg-white/5">EfficientNet-B4</span>
                  <span className="badge-sm bg-white/5">Grad-CAM</span>
                  <span className="badge-sm bg-white/5">ISIC Dataset</span>
                  <span className="badge-sm bg-white/5">FastAPI</span>
                  <span className="badge-sm bg-white/5">Next.js</span>
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
              <div>© 2026 DermaScan AI V4 · Research Prototype</div>
              <div className="font-mono text-[10px] tracking-widest uppercase">FOR RESEARCH USE ONLY — NOT A CLINICAL DIAGNOSTIC DEVICE</div>
            </div>
          </div>
        </div>
      </footer>

      {/* Global Interactive Modal */}
      <AnimatePresence>
        {activeModal && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }}
            className="fixed inset-0 z-[100] flex items-center justify-center bg-[#050816]/80 backdrop-blur-md p-4"
            onClick={() => setActiveModal(null)}
          >
            <motion.div 
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-[#0B1120] border border-[#00D4FF]/30 shadow-[0_0_50px_rgba(0,212,255,0.15)] rounded-2xl max-w-lg w-full p-8 relative overflow-hidden"
            >
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-[#00D4FF] to-blue-600" />
              <button 
                onClick={() => setActiveModal(null)}
                className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors bg-white/5 rounded-full p-1.5 hover:bg-white/10"
              >
                <X size={20} />
              </button>
              <h3 className="text-2xl font-bold font-display text-white mb-4 pr-8">{activeModal.title}</h3>
              <div className="text-gray-300 leading-relaxed text-base">{activeModal.content}</div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}
