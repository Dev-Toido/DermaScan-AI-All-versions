// DermaScan AI V3 - Main JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // Mobile Menu Toggle
    const mobileBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileIcon = document.getElementById('mobile-menu-icon');
    const mobileLinks = document.querySelectorAll('.mobile-nav-link');

    if (mobileBtn && mobileMenu && mobileIcon) {
        mobileBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
            if (mobileMenu.classList.contains('hidden')) {
                mobileIcon.classList.remove('ph-x');
                mobileIcon.classList.add('ph-list');
            } else {
                mobileIcon.classList.remove('ph-list');
                mobileIcon.classList.add('ph-x');
            }
        });

        mobileLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.add('hidden');
                mobileIcon.classList.remove('ph-x');
                mobileIcon.classList.add('ph-list');
            });
        });
    }

    // Initialize AOS Animation Library
    AOS.init({
        once: true,
        offset: 50,
        duration: 800,
        easing: 'ease-out-cubic',
    });

    // Initialize Particles.js (if library loaded)
    if (window.particlesJS) {
        particlesJS('particles-js', {
            "particles": {
                "number": { "value": 40, "density": { "enable": true, "value_area": 800 } },
                "color": { "value": "#14b8a6" },
                "shape": { "type": "circle" },
                "opacity": { "value": 0.3, "random": true },
                "size": { "value": 3, "random": true },
                "line_linked": { "enable": true, "distance": 150, "color": "#14b8a6", "opacity": 0.2, "width": 1 },
                "move": { "enable": true, "speed": 1, "direction": "none", "random": true, "out_mode": "out" }
            },
            "interactivity": {
                "detect_on": "canvas",
                "events": { "onhover": { "enable": true, "mode": "grab" }, "onclick": { "enable": false }, "resize": true },
                "modes": { "grab": { "distance": 140, "line_linked": { "opacity": 0.5 } } }
            },
            "retina_detect": true
        });
    }

    // Load content dynamically
    fetch('content.json')
        .then(response => response.json())
        .then(data => {
            populateContent(data);
        })
        .catch(err => console.error("Error loading content:", err));
});

function populateContent(data) {
    // Hero
    if(document.getElementById('hero-title')) document.getElementById('hero-title').innerText = data.hero.title;
    if(document.getElementById('hero-subtitle')) document.getElementById('hero-subtitle').innerText = data.hero.subtitle;

    // Problem
    if(document.getElementById('problem-heading')) document.getElementById('problem-heading').innerText = data.problem.heading;
    if(document.getElementById('problem-text')) document.getElementById('problem-text').innerText = data.problem.text;
    
    const statsContainer = document.getElementById('stats-container');
    if (statsContainer && data.problem.stats) {
        data.problem.stats.forEach((stat, idx) => {
            statsContainer.innerHTML += `
                <div class="glass-card p-8 rounded-2xl text-center" data-aos="fade-up" data-aos-delay="${idx * 150}">
                    <div class="text-5xl font-bold text-accent mb-2">${stat.number}</div>
                    <div class="text-slate-400 text-lg">${stat.label}</div>
                </div>
            `;
        });
    }

    // Features (Interactive Modals)
    const featuresContainer = document.getElementById('features-container');
    if (featuresContainer && data.features) {
        // We want a more compact grid for 10 items. e.g., 5 columns on large screens, 3 on md, 1 on small.
        featuresContainer.className = "grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6";
        featuresContainer.innerHTML = "";
        
        data.features.forEach((feature, idx) => {
            const card = document.createElement('div');
            card.className = "glass-card p-6 rounded-2xl cursor-pointer hover:-translate-y-2 hover:shadow-[0_10px_30px_rgba(20,184,166,0.3)] transition-all duration-300 flex flex-col items-center text-center";
            card.setAttribute('data-aos', 'fade-up');
            card.setAttribute('data-aos-delay', (idx * 50).toString());
            
            card.innerHTML = `
                <i class="${feature.icon} text-4xl text-accent mb-4"></i>
                <h3 class="text-sm font-bold mb-2 leading-tight">${feature.title}</h3>
                <p class="text-xs text-slate-400">${feature.teaser}</p>
            `;
            
            card.addEventListener('click', () => openModal(feature));
            featuresContainer.appendChild(card);
        });
    }

    // Footer
    if(document.getElementById('footer-disclaimer')) document.getElementById('footer-disclaimer').innerText = data.footer.disclaimer;
}

// Modal Logic
const modal = document.getElementById('feature-modal');
const modalBackdrop = document.getElementById('modal-backdrop');
const modalContent = document.getElementById('modal-content');
const modalClose = document.getElementById('modal-close');
const modalIcon = document.getElementById('modal-icon');
const modalTitle = document.getElementById('modal-title');
const modalText = document.getElementById('modal-text');
const modalVisualContainer = document.getElementById('modal-visual-container');
let chartInstance = null;

function openModal(feature) {
    // Populate text
    modalIcon.className = `${feature.icon} text-4xl text-accent`;
    modalTitle.innerText = feature.title;
    modalText.innerText = feature.text;
    
    // Clear previous visual
    modalVisualContainer.innerHTML = '';
    if (chartInstance) {
        chartInstance.destroy();
        chartInstance = null;
    }
    
    // Generate Visual based on type
    generateVisual(feature.visual_type, modalVisualContainer);
    
    // Show Modal
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    document.body.classList.add('modal-open'); // prevent background scroll
    
    // Animate in
    setTimeout(() => {
        modalBackdrop.classList.remove('opacity-0');
        modalBackdrop.classList.add('opacity-100');
        modalContent.classList.remove('scale-95', 'opacity-0');
        modalContent.classList.add('scale-100', 'opacity-100');
    }, 10);
}

function closeModal() {
    // Animate out
    modalBackdrop.classList.remove('opacity-100');
    modalBackdrop.classList.add('opacity-0');
    modalContent.classList.remove('scale-100', 'opacity-100');
    modalContent.classList.add('scale-95', 'opacity-0');
    
    setTimeout(() => {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.classList.remove('modal-open');
        modalVisualContainer.innerHTML = '';
        if (chartInstance) {
            chartInstance.destroy();
            chartInstance = null;
        }
    }, 300);
}

if(modalClose) modalClose.addEventListener('click', closeModal);
if(modalBackdrop) modalBackdrop.addEventListener('click', closeModal);
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
        closeModal();
    }
});

function generateVisual(type, container) {
    if (type === 'diagram_multimodal') {
        container.innerHTML = `
            <div class="flex items-center gap-4 text-center">
                <div class="glass-card p-4 rounded-xl border-blue-500 border animate-pulse"><i class="ph ph-image text-3xl text-blue-400"></i><div class="text-xs mt-2">Image</div></div>
                <i class="ph ph-arrow-right text-2xl text-slate-500"></i>
                <div class="glass-card p-6 rounded-full border-accent border flex items-center justify-center bg-accent/20">
                    <i class="ph-fill ph-cpu text-4xl text-accent"></i>
                </div>
                <i class="ph ph-arrow-left text-2xl text-slate-500"></i>
                <div class="glass-card p-4 rounded-xl border-purple-500 border animate-pulse"><i class="ph ph-file-text text-3xl text-purple-400"></i><div class="text-xs mt-2">Metadata</div></div>
            </div>
            <div class="w-full text-center mt-4">
                <i class="ph ph-arrow-down text-2xl text-slate-500"></i>
                <div class="font-bold text-accent mt-2">Diagnosis</div>
            </div>
        `;
    } else if (type === 'diagram_network') {
        container.innerHTML = `
            <div class="flex flex-col items-center">
                <i class="ph-light ph-graph text-7xl text-accent mb-4"></i>
                <div class="flex gap-2">
                    <div class="h-16 w-4 bg-slate-700 rounded-full"></div>
                    <div class="h-20 w-4 bg-slate-600 rounded-full"></div>
                    <div class="h-24 w-4 bg-slate-500 rounded-full"></div>
                    <div class="h-12 w-4 bg-accent rounded-full"></div>
                </div>
                <p class="mt-4 text-sm font-mono text-slate-400">1792-D Feature Vector</p>
            </div>
        `;
    } else if (type === 'slider_gradcam') {
        container.innerHTML = `
            <div class="gradcam-container" id="gradcam-container">
                <img src="https://images.unsplash.com/photo-1612204070659-99436fcb9933?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80" class="gradcam-original" alt="Original">
                <img src="https://images.unsplash.com/photo-1612204070659-99436fcb9933?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80" class="gradcam-overlay" id="gradcam-overlay" alt="Grad-CAM" style="filter: sepia(1) hue-rotate(300deg) saturate(5);">
                <input type="range" min="0" max="100" value="50" class="gradcam-slider" id="gradcam-slider">
            </div>
            <p class="text-xs text-slate-400 mt-4 text-center">Drag slider to compare</p>
        `;
        const slider = document.getElementById('gradcam-slider');
        const overlay = document.getElementById('gradcam-overlay');
        slider.addEventListener('input', (e) => {
            overlay.style.width = `${e.target.value}%`;
        });
    } else if (type === 'risk_bar') {
        container.innerHTML = `
            <div class="w-full max-w-lg px-4 flex flex-col items-center">
                <div class="risk-bar-container mb-4 w-full">
                    <div class="risk-segment risk-benign" id="rb-benign">Benign</div>
                    <div class="risk-segment risk-pre" id="rb-pre">Pre-Malig</div>
                    <div class="risk-segment risk-malignant" id="rb-mal">Malignant</div>
                </div>
                <div class="flex justify-between w-full text-xs text-slate-400 px-2">
                    <span>NV, BKL, DF, VASC</span>
                    <span>AK</span>
                    <span>MEL, BCC, SCC</span>
                </div>
            </div>
        `;
        // Animate bar
        setTimeout(() => {
            if(document.getElementById('rb-benign')) document.getElementById('rb-benign').style.width = '33.3%';
            if(document.getElementById('rb-pre')) document.getElementById('rb-pre').style.width = '33.3%';
            if(document.getElementById('rb-mal')) document.getElementById('rb-mal').style.width = '33.3%';
        }, 100);
    } else if (type === 'gauge_speedometer') {
        container.innerHTML = `
            <div class="flex flex-col items-center pt-8">
                <div class="gauge-container">
                    <div class="gauge-arc"></div>
                    <div class="gauge-arc gauge-arc-active" id="gauge-active" style="transform: rotate(-45deg);"></div>
                    <div class="gauge-needle" id="gauge-needle" style="transform: rotate(-90deg);"></div>
                </div>
                <div class="text-3xl font-bold mt-4" id="gauge-text">0%</div>
                <div class="text-xs text-slate-400 mt-2 flex gap-4">
                    <span class="text-red-400">Uncertain (<60%)</span>
                    <span class="text-green-400">Confident (≥60%)</span>
                </div>
            </div>
        `;
        setTimeout(() => {
            const needle = document.getElementById('gauge-needle');
            const active = document.getElementById('gauge-active');
            const text = document.getElementById('gauge-text');
            if (needle && active && text) {
                // Simulate 85% confidence
                const val = 85;
                needle.style.transform = `rotate(${-90 + (val/100)*180}deg)`;
                active.style.transform = `rotate(${-45 + (val/100)*180}deg)`;
                let current = 0;
                const int = setInterval(() => {
                    if (current >= val) clearInterval(int);
                    else {
                        current++;
                        text.innerText = current + '%';
                        text.style.color = current >= 60 ? '#4ade80' : '#ef4444';
                    }
                }, 10);
            }
        }, 300);
    } else if (type === 'offline_icon') {
        container.innerHTML = `
            <div class="relative inline-block">
                <i class="ph-light ph-laptop text-8xl text-slate-300"></i>
                <div class="absolute -top-2 -right-2 bg-green-500 rounded-full p-1 shadow-[0_0_15px_rgba(34,197,94,0.6)]">
                    <i class="ph-bold ph-check text-white text-xl"></i>
                </div>
                <div class="absolute -bottom-2 -left-2 bg-red-500 rounded-full p-1 opacity-50">
                    <i class="ph-bold ph-wifi-slash text-white text-xl"></i>
                </div>
            </div>
        `;
    } else if (type === 'pdf_mockup') {
        container.innerHTML = `
            <div class="bg-white rounded w-48 h-64 p-4 shadow-2xl relative overflow-hidden transform hover:scale-105 transition-transform flex flex-col items-center">
                <div class="w-full h-2 bg-blue-900 mb-4"></div>
                <div class="w-2/3 h-2 bg-slate-300 mb-2 self-start"></div>
                <div class="w-1/2 h-2 bg-slate-300 mb-6 self-start"></div>
                
                <div class="flex gap-2 w-full mb-4">
                    <div class="w-1/2 h-16 bg-slate-200"></div>
                    <div class="w-1/2 h-16 bg-slate-200"></div>
                </div>
                
                <div class="w-full h-1 bg-slate-200 mb-1"></div>
                <div class="w-full h-1 bg-slate-200 mb-1"></div>
                <div class="w-3/4 h-1 bg-slate-200 mb-4 self-start"></div>
                
                <i class="ph-fill ph-check-circle text-green-500 text-3xl mt-auto"></i>
            </div>
        `;
    } else if (type === 'form_sliders') {
        container.innerHTML = `
            <div class="flex flex-col gap-4 w-full max-w-xs p-6 bg-slate-800 rounded-xl">
                <div class="flex justify-between items-center">
                    <span class="text-sm font-bold">Age</span>
                    <span class="text-xs bg-slate-700 px-2 rounded">52</span>
                </div>
                <div class="w-full h-2 bg-slate-600 rounded">
                    <div class="w-1/2 h-full bg-accent rounded"></div>
                </div>
                
                <div class="flex justify-between items-center mt-2">
                    <span class="text-sm font-bold">Sex</span>
                    <span class="text-xs bg-slate-700 px-2 rounded">Female</span>
                </div>
                
                <div class="flex justify-between items-center mt-2">
                    <span class="text-sm font-bold">Site</span>
                    <span class="text-xs bg-slate-700 px-2 rounded">Torso</span>
                </div>
            </div>
        `;
    } else if (type === 'toggle_switch') {
        container.innerHTML = `
            <div class="flex flex-col items-center gap-4">
                <div class="toggle-switch" id="demo-toggle">
                    <div class="toggle-circle"></div>
                </div>
                <div id="demo-status" class="text-sm font-bold text-slate-400">Clinical Mode (Threshold 60%)</div>
            </div>
        `;
        setTimeout(() => {
            const toggle = document.getElementById('demo-toggle');
            const status = document.getElementById('demo-status');
            if(toggle) {
                toggle.addEventListener('click', () => {
                    toggle.classList.toggle('active');
                    if (toggle.classList.contains('active')) {
                        status.innerText = "Demo Mode (Threshold 50%)";
                        status.className = "text-sm font-bold text-accent";
                    } else {
                        status.innerText = "Clinical Mode (Threshold 60%)";
                        status.className = "text-sm font-bold text-slate-400";
                    }
                });
            }
        }, 100);
    } else if (type === 'performance_chart') {
        container.innerHTML = `<canvas id="perfChart" style="max-height: 250px;"></canvas>`;
        setTimeout(() => {
            const ctx = document.getElementById('perfChart').getContext('2d');
            chartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Overall Accuracy', 'Malignant Sensitivity', 'Vascular Recall', 'Safety Net Trigger'],
                    datasets: [{
                        label: 'Metrics (%)',
                        data: [65.7, 85, 97, 100],
                        backgroundColor: ['#14b8a6', '#ef4444', '#3b82f6', '#f59e0b'],
                        borderWidth: 0,
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            grid: { color: 'rgba(255,255,255,0.1)' },
                            ticks: { color: '#94a3b8' }
                        },
                        x: {
                            grid: { display: false },
                            ticks: { color: '#94a3b8' }
                        }
                    }
                }
            });
        }, 100);
    }
}

