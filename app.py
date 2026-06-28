import streamlit as st
import time
import importlib
import os
import backend
import components

# Reload helper modules once per browser session so Streamlit picks up
# any new functions added while the server is already running.
if "_modules_loaded" not in st.session_state:
    importlib.reload(backend)
    importlib.reload(components)
    st.session_state._modules_loaded = True

# Page config (enforcing Inter font, wide layout, hidden sidebar)
st.set_page_config(
    page_title="AI Resume Optimizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom premium styles
components.load_css("style.css")

# --- SESSION STATE INITIALIZATION ---
if "analysis_stage" not in st.session_state:
    st.session_state.analysis_stage = "upload"
# Load persisted API key from config.json — survives page refreshes
if "api_key" not in st.session_state:
    st.session_state.api_key = backend.load_config().get("user_api_key", "")
if "file_name" not in st.session_state:
    st.session_state.file_name = None
if "file_bytes" not in st.session_state:
    st.session_state.file_bytes = None
if "file_size" not in st.session_state:
    st.session_state.file_size = 0
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "metadata" not in st.session_state:
    st.session_state.metadata = None
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "job_desc" not in st.session_state:
    st.session_state.job_desc = ""
if "optimized_resume" not in st.session_state:
    st.session_state.optimized_resume = None
if "history" not in st.session_state:
    st.session_state.history = []
if "quota_exceeded" not in st.session_state:
    st.session_state.quota_exceeded = False

# Helper: reusable quota-exceeded banner
def show_quota_banner():
    st.markdown(components.clean_html("""
    <div style="background:#FEF2F2; border:1px solid #FCA5A5; border-radius:12px; padding:14px 20px; margin-bottom:20px; display:flex; align-items:flex-start; gap:12px;">
    <span style="font-size:22px; line-height:1.2;">🚨</span>
    <div>
    <span style="font-weight:700; color:#DC2626; font-size:14px;">Built-in API quota reached</span>
    <span style="font-size:13px; color:#7F1D1D; display:block; margin-top:4px;">The shared API key has hit its usage limit. Please add your own free Gemini API key in <a href="?page=settings" target="_self" style="color:#DC2626; font-weight:700;">Settings</a> to continue with real AI features. It only takes 30 seconds.</span>
    </div>
    </div>
    """), unsafe_allow_html=True)

# --- ROUTING VIA QUERY PARAMETERS ---
query_params = st.query_params
active_page = query_params.get("page", "home")

# Render custom navbar
components.render_navbar(active_page=active_page)



# ----------------- HOME / OPTIMIZER PAGE -----------------
if active_page == "home":
    # Guard: if file was cleared externally, reset stage to upload
    if st.session_state.file_name is None and st.session_state.analysis_stage not in ("upload",):
        st.session_state.analysis_stage = "upload"
    
    # STAGE 1: UPLOAD STATE
    if st.session_state.analysis_stage == "upload":
        # Handle query parameter trigger from navbar "Get Started" button
        if st.query_params.get("get_started") == "true":
            st.session_state.show_uploader = True
            # Clear parameter to prevent loop
            st.query_params.pop("get_started", None)

        # ─── FOLD 1: HERO SECTION ───
        col_hero_left, col_hero_right = st.columns([1.2, 1])
        
        with col_hero_left:
            st.markdown(components.clean_html("""
            <div style="display:flex; flex-direction:column; justify-content:center; height:100%; padding:20px 0; text-align:left;">
                <span class="badge-ai" style="width:fit-content; margin-bottom:20px; font-weight:700; background-color:#EFF6FF; color:#0066FF; border: 1px solid #DBEAFE; padding: 6px 14px; border-radius: 9999px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;">✨ NEW: GPT-4O POWERED ANALYSIS</span>
                <h1 class="hero-title" style="text-align:left; font-size:48px; line-height:1.15; margin-bottom:20px; letter-spacing:-0.03em; font-weight:800; color:#1F2937;">
                    Land your dream job with <span style="color:#0066FF;">AI-powered</span> resume precision.
                </h1>
                <p class="hero-subtitle" style="text-align:left; margin:0 0 32px 0; max-width:540px; font-size:16px; line-height:1.7; color:#64748B;">
                    Our intelligent platform analyzes your resume against industry standards, injects missing high-impact keywords, and optimizes your layout to guarantee a 95%+ ATS compatibility score.
                </p>
            </div>
            """), unsafe_allow_html=True)
            
            # Action Buttons Row
            btn_col1, btn_col2 = st.columns([1.1, 1])
            with btn_col1:
                # Custom button via Streamlit
                if st.button("Get Started for Free", type="primary", use_container_width=True, key="hero_get_started"):
                    st.session_state.show_uploader = True
                    st.rerun()
            with btn_col2:
                if st.button("💬 Watch Demo", type="secondary", use_container_width=True, key="hero_watch_demo"):
                    st.toast("⚡ Demo video coming soon!")
                    
            st.markdown(components.clean_html("""
            <p style="font-size:12px; color:#94A3B8; margin-top:14px; margin-bottom:0;">No credit card required • Free trial for 30 days</p>
            """), unsafe_allow_html=True)
            
        with col_hero_right:
            if st.session_state.get("show_uploader", False):
                # The Active File Uploader Box
                st.markdown('<div class="home-page" style="padding: 10px 0; position:relative;">', unsafe_allow_html=True)
                if st.button("← Back to Preview", type="secondary", key="back_to_preview_uploader"):
                    st.session_state.show_uploader = False
                    st.rerun()
                
                uploaded_file = st.file_uploader(
                    "Upload Resume",
                    type=["pdf", "docx"],
                    label_visibility="collapsed",
                    key="resume_uploader"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                # The Beautiful HTML/CSS Mockup Preview Card from the mockup design
                st.markdown(components.clean_html("""
                <div style="display:flex; justify-content:center; align-items:center; height:100%; padding:20px 0;">
                    <div class="mockup-container">
                        <div class="mockup-badge-top">
                            <span class="dot-blue"></span> Keyword Optimized
                        </div>
                        <div class="mockup-badge-bottom">
                            <span class="check-green">✓</span> ATS Score: <strong>98/100</strong>
                        </div>
                        <div class="mockup-split">
                            <div class="mockup-pane">
                                <div class="pane-header" style="display:flex; align-items:center; gap:8px;">
                                    <div class="pane-avatar"></div>
                                    <div style="flex:1; display:flex; flex-direction:column; gap:4px;">
                                        <div class="pane-line short"></div>
                                        <div class="pane-line medium"></div>
                                    </div>
                                </div>
                                <div class="pane-body" style="display:flex; flex-direction:column; gap:6px; margin-top:8px;">
                                    <div class="pane-line long"></div>
                                    <div class="pane-line long red-strike"></div>
                                    <div class="pane-line medium"></div>
                                    <div class="pane-line long"></div>
                                </div>
                            </div>
                            <div class="mockup-pane">
                                <div class="pane-header" style="display:flex; align-items:center; gap:8px;">
                                    <div class="pane-avatar" style="background:#DBEAFE;"></div>
                                    <div style="flex:1; display:flex; flex-direction:column; gap:4px;">
                                        <div class="pane-line short" style="background:#93C5FD;"></div>
                                        <div class="pane-line medium"></div>
                                    </div>
                                </div>
                                <div class="pane-body" style="display:flex; flex-direction:column; gap:6px; margin-top:8px;">
                                    <div class="pane-line long"></div>
                                    <div class="pane-line long green-highlight"></div>
                                    <div class="pane-line medium"></div>
                                    <div class="pane-line long" style="background:#EFF6FF;"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """), unsafe_allow_html=True)
                
                # Link to open uploader
                col_trig, _ = st.columns([1.5, 1])
                with col_trig:
                    if st.button("⚡ Click here to upload your resume", type="secondary", key="trigger_uploader_link"):
                        st.session_state.show_uploader = True
                        st.rerun()

        # Handle file upload trigger
        if st.session_state.get("show_uploader", False) and 'uploaded_file' in locals() and uploaded_file is not None:
            # Sync uploaded file into session state
            if st.session_state.file_name != uploaded_file.name:
                file_bytes = uploaded_file.read()
                st.session_state.file_bytes = file_bytes
                st.session_state.file_name = uploaded_file.name
                st.session_state.file_size = len(file_bytes)
                st.session_state.resume_text = backend.parse_resume(file_bytes, uploaded_file.name)
                st.session_state.metadata = backend.extract_metadata(
                    st.session_state.resume_text,
                    uploaded_file.name,
                    st.session_state.file_size
                )
                st.session_state.analysis_stage = "preview"
                st.rerun()

        # ─── FOLD 2: STATISTICS STRIP ───
        st.markdown('<div style="height:48px;"></div>', unsafe_allow_html=True)
        st.markdown(components.clean_html("""
        <div class="stats-strip">
            <div class="stat-item">
                <div style="font-size:32px; font-weight:800; color:#0066FF;">95%</div>
                <div style="font-size:12px; color:#64748B; font-weight:600; text-transform:uppercase; margin-top:4px;">Candidate Success Rate</div>
            </div>
            <div class="stat-item">
                <div style="font-size:32px; font-weight:800; color:#1F2937;">10k+</div>
                <div style="font-size:12px; color:#64748B; font-weight:600; text-transform:uppercase; margin-top:4px;">Resumes Optimized</div>
            </div>
            <div class="stat-item">
                <div style="font-size:32px; font-weight:800; color:#1F2937;">1.5M</div>
                <div style="font-size:12px; color:#64748B; font-weight:600; text-transform:uppercase; margin-top:4px;">Job Leads Found</div>
            </div>
            <div class="stat-item-last">
                <div style="font-size:11px; color:#94A3B8; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:8px;">Trusted by Candidates at</div>
                <div style="display:flex; justify-content:center; gap:12px; align-items:center; flex-wrap:wrap;">
                    <span style="font-size:12px; font-weight:700; color:#64748B;">Google</span>
                    <span style="font-size:12px; font-weight:700; color:#64748B;">Meta</span>
                    <span style="font-size:12px; font-weight:700; color:#64748B;">Amazon</span>
                </div>
            </div>
        </div>
        """), unsafe_allow_html=True)

        # ─── FOLD 3: FEATURES GRID (ENGINEERED FOR SUCCESS) ───
        st.markdown('<div style="height:64px;"></div>', unsafe_allow_html=True)
        st.markdown(components.clean_html("""
        <div style="text-align:center; max-width:600px; margin:0 auto 40px auto;">
            <h2 style="font-size:28px; font-weight:800; color:#1F2937; margin-bottom:12px; letter-spacing:-0.02em;">Engineered for Success</h2>
            <p style="font-size:14.5px; color:#64748B; line-height:1.6;">Our specialized AI models are trained on thousands of successful hires across the tech and finance industries.</p>
        </div>
        """), unsafe_allow_html=True)
        
        feat_col1, feat_col2, feat_col3 = st.columns(3)
        with feat_col1:
            st.markdown(components.clean_html("""
            <div class="feature-card">
                <div class="feature-icon-wrapper">⚙️</div>
                <h3 style="font-size:16px; font-weight:700; color:#1F2937; margin:0 0 8px 0;">ATS Optimization</h3>
                <p style="font-size:13px; color:#64748B; line-height:1.6; margin:0;">Beat the bots with structured formats that applicant tracking systems love. We ensure your data is always readable and relevant.</p>
            </div>
            """), unsafe_allow_html=True)
        with feat_col2:
            st.markdown(components.clean_html("""
            <div class="feature-card">
                <div class="feature-icon-wrapper">🔑</div>
                <h3 style="font-size:16px; font-weight:700; color:#1F2937; margin:0 0 8px 0;">Smart Keyword Injection</h3>
                <p style="font-size:13px; color:#64748B; line-height:1.6; margin:0;">Our AI cross-references your resume with job descriptions to automatically suggest and place the most critical missing skills.</p>
            </div>
            """), unsafe_allow_html=True)
        with feat_col3:
            st.markdown(components.clean_html("""
            <div class="feature-card">
                <div class="feature-icon-wrapper">📈</div>
                <h3 style="font-size:16px; font-weight:700; color:#1F2937; margin:0 0 8px 0;">Quantifiable Impact</h3>
                <p style="font-size:13px; color:#64748B; line-height:1.6; margin:0;">We turn generic job duties into powerful achievements using our formulaic approach to impact-based resume writing.</p>
            </div>
            """), unsafe_allow_html=True)

        # ─── FOLD 4: HOW IT WORKS ───
        st.markdown('<div style="height:64px;"></div>', unsafe_allow_html=True)
        how_col_left, how_col_right = st.columns([1, 1.8])
        with how_col_left:
            st.markdown(components.clean_html("""
            <div style="display:flex; flex-direction:column; justify-content:center; height:100%; text-align:left;">
                <h2 style="font-size:28px; font-weight:800; color:#1F2937; margin-bottom:16px; letter-spacing:-0.02em; line-height:1.2;">Perfect your resume in 3 easy steps</h2>
                <p style="font-size:14.5px; color:#64748B; line-height:1.6; margin:0 0 24px 0;">Simple, transparent, and built for professionals who value their time.</p>
                <a href="#hero_get_started" style="color:#0066FF; font-size:14px; font-weight:700; text-decoration:none;">Learn about our algorithm →</a>
            </div>
            """), unsafe_allow_html=True)
        with how_col_right:
            step_col1, step_col2, step_col3 = st.columns(3)
            with step_col1:
                st.markdown(components.clean_html("""
                <div class="feature-card" style="border:1px solid #E2E8F0;">
                    <div class="step-number-badge">1</div>
                    <h3 style="font-size:15px; font-weight:700; color:#1F2937; margin:0 0 8px 0;">Upload</h3>
                    <p style="font-size:12.5px; color:#64748B; line-height:1.5; margin:0;">Drag and drop your current PDF or Word resume. Our parser handles everything.</p>
                </div>
                """), unsafe_allow_html=True)
            with step_col2:
                st.markdown(components.clean_html("""
                <div class="feature-card" style="border:1px solid #E2E8F0;">
                    <div class="step-number-badge">2</div>
                    <h3 style="font-size:15px; font-weight:700; color:#1F2937; margin:0 0 8px 0;">Analyze</h3>
                    <p style="font-size:12.5px; color:#64748B; line-height:1.5; margin:0;">Our AI runs 50+ health checks against top-tier industry benchmarks.</p>
                </div>
                """), unsafe_allow_html=True)
            with step_col3:
                st.markdown(components.clean_html("""
                <div class="feature-card" style="border:1px solid #E2E8F0;">
                    <div class="step-number-badge">3</div>
                    <h3 style="font-size:15px; font-weight:700; color:#1F2937; margin:0 0 8px 0;">Perfect</h3>
                    <p style="font-size:12.5px; color:#64748B; line-height:1.5; margin:0;">Apply one-click suggestions and download your optimized, ready-to-send resume.</p>
                </div>
                """), unsafe_allow_html=True)

        # ─── FOLD 5: CALL TO ACTION (CTA) ───
        st.markdown('<div style="height:64px;"></div>', unsafe_allow_html=True)
        st.markdown(components.clean_html("""
        <div class="cta-box">
            <h2 style="font-size:32px; font-weight:800; color:#FFFFFF; margin-bottom:16px; letter-spacing:-0.02em;">Ready to secure your next interview?</h2>
            <p style="font-size:15px; color:#E0F2FE; max-width:540px; margin:0 auto 24px auto; line-height:1.6;">Join over 10,000 professionals who have leveled up their careers with AI Resume Optimizer. Start for free today.</p>
            <div style="display:flex; justify-content:center; gap:16px; flex-wrap:wrap; margin-top:16px;">
                <a href="?page=home&get_started=true" class="cta-btn-white" target="_self">Get Started for Free</a>
                <a href="?page=home&get_started=true" class="cta-btn-outline" target="_self">View Sample Resumes</a>
            </div>
        </div>
        """), unsafe_allow_html=True)

        st.markdown('<div style="height:48px;"></div>', unsafe_allow_html=True)


    # STAGE 2: PREVIEW STATE
    elif st.session_state.analysis_stage == "preview":
        metadata = st.session_state.metadata
        
        st.markdown('<h1 class="section-title" style="width:100%; text-align:left; margin-bottom:16px;">Resume Preview</h1>', unsafe_allow_html=True)
        
        # 2-Column Responsive Layout
        col_preview, col_metadata = st.columns([1, 2])
        
        with col_preview:
            # Sidebar resume summary details
            st.markdown(components.clean_html(f"""
            <div class="resume-thumbnail">
                <div style="font-size: 64px;">📄</div>
                <div style="font-weight: 700; font-size: 16px; text-align: center; word-break: break-all; padding: 0 16px;">{metadata['filename']}</div>
                <div style="font-size: 12px; color: #64748B;">{metadata['size']} • {metadata['pages']} page(s)</div>
            </div>
            """), unsafe_allow_html=True)
            
            st.markdown(components.clean_html("""
            <div class="card" style="margin-top: 24px;">
                <div class="card-title" style="margin-bottom: 8px;">Upload Status</div>
                <span class="chip chip-success" style="width: fit-content;">✓ File loaded successfully</span>
            </div>
            """), unsafe_allow_html=True)
            
        with col_metadata:
            # Extracted Sections & Skills Card
            sections_html = "".join(f'<span class="chip chip-success" style="background-color:#DCFCE7; color:#16A34A; margin-right:8px; margin-bottom:8px;">{sec}</span>' for sec in metadata['sections'])
            skills_html = "".join(f'<span class="chip" style="background-color:#E2E8F0; color:#475569; margin-right:8px; margin-bottom:8px;">{skill}</span>' for skill in metadata['skills'])
            
            st.markdown(components.clean_html(f"""
            <div class="card" style="margin-bottom: 24px;">
                <div class="card-title">Extracted Layout Sections</div>
                <div class="tag-container" style="margin-top: 8px; margin-bottom: 16px;">
                    {sections_html if sections_html else '<span class="chip chip-error">No standard sections detected</span>'}
                </div>
                <div class="card-title">Detected Professional Skills</div>
                <div class="tag-container" style="margin-top: 8px;">
                    {skills_html if skills_html else '<span class="chip chip-warning">No skills detected</span>'}
                </div>
            </div>
            """), unsafe_allow_html=True)
            
            # Target Job Description Text Area (Optional)
            with st.container(border=True):
                st.markdown('<div class="card-title" style="margin-bottom: 8px;">Target Job Description (Optional)</div>', unsafe_allow_html=True)
                
                # Store JD input directly in session state
                job_desc = st.text_area(
                    "Paste the target job description to run a tailored ATS match analysis.",
                    value=st.session_state.job_desc,
                    placeholder="Paste the job description or role requirements here...",
                    label_visibility="collapsed",
                    key="jd_input_widget"
                )
                st.session_state.job_desc = job_desc
            
            # Action Buttons
            col_act1, col_act2 = st.columns(2)
            with col_act1:
                if st.button("Analyze Resume", type="primary", use_container_width=True):
                    st.session_state.analysis_stage = "loading"
                    st.rerun()
            with col_act2:
                if st.button("Cancel & Clear", type="secondary", use_container_width=True):
                    # Reset variables
                    st.session_state.analysis_stage = "upload"
                    st.session_state.file_bytes = None
                    st.session_state.file_name = None
                    st.session_state.file_size = 0
                    st.session_state.resume_text = ""
                    st.session_state.metadata = None
                    st.session_state.analysis_results = None
                    st.session_state.job_desc = ""
                    st.rerun()

    # STAGE 3: LOADING STATE
    elif st.session_state.analysis_stage == "loading":
        st.markdown('<h1 class="hero-title" style="margin-bottom: 16px;">Analyzing your resume...</h1>', unsafe_allow_html=True)
        st.markdown('<p class="hero-subtitle" style="margin-bottom: 32px;">Please wait while our AI scans your layout, checks keywords, and runs calculations.</p>', unsafe_allow_html=True)
        
        # Placeholder for dynamic status message updates
        status_box = st.empty()
        components.render_skeleton_loader()
        
        # Simulation step sequences
        stages = [
            "Analyzing Resume File Structure...",
            "Extracting Core Sections & Details...",
            "Matching Skills against Industry Guidelines...",
            "Running ATS Algorithmic Analysis...",
            "Generating Personalized AI Suggestions..."
        ]
        
        for idx, stage in enumerate(stages):
            status_box.markdown(f'<div style="text-align:center; font-weight:600; font-size:16px; color:#2563EB; margin-bottom:24px;">🔄 {stage}</div>', unsafe_allow_html=True)
            time.sleep(0.8)
            
        # Run calculation — always use the active key (default or user's own)
        active_key = backend.get_active_api_key()
        results = backend.analyze_resume_gemini(
            st.session_state.resume_text,
            st.session_state.metadata,
            st.session_state.job_desc,
            active_key
        )

        # Detect quota exceeded on built-in key
        if results.get("quota_exceeded") and backend.is_using_default_key():
            st.session_state.quota_exceeded = True
            
        st.session_state.analysis_results = results
        st.session_state.analysis_stage = "results"
        # Save to session history
        st.session_state.history.append({
            "file_name": st.session_state.file_name,
            "size": st.session_state.metadata.get("size", "N/A"),
            "pages": st.session_state.metadata.get("pages", 1),
            "ats_score": results.get("ats_score", "N/A"),
            "mode": "Gemini AI" if st.session_state.api_key else "Demo Mode",
        })
        st.rerun()

    # STAGE 4: RESULTS STATE
    elif st.session_state.analysis_stage == "results":
        results = st.session_state.analysis_results
        
        # Guard: redirect to upload if results were lost (e.g. page refresh mid-analysis)
        if not results:
            st.session_state.analysis_stage = "upload"
            st.rerun()

        # Quota exceeded banner (built-in key ran out)
        if st.session_state.quota_exceeded and backend.is_using_default_key():
            show_quota_banner()
        # Show demo mode notice only if no key at all and no quota issue
        elif not backend.get_active_api_key():
            st.markdown(components.clean_html("""
            <div style="background:#FFF7ED; border:1px solid #FED7AA; border-radius:12px; padding:12px 20px; margin-bottom:24px; display:flex; align-items:center; gap:12px;">
            <span style="font-size:20px;">⚡</span>
            <div>
            <span style="font-weight:700; color:#C2410C; font-size:14px;">Demo Mode — Simulated Results</span>
            <span style="font-size:13px; color:#92400E; display:block; margin-top:2px;">No Gemini API key is set. Add your key in <a href="?page=settings" target="_self" style="color:#C2410C; font-weight:600;">Settings</a> to run a real AI analysis.</span>
            </div>
            </div>
            """), unsafe_allow_html=True)
        
        st.markdown('<h1 class="section-title" style="width:100%; text-align:left; margin-bottom:8px;">Analysis Results</h1>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#64748B; font-size:16px; width:100%; margin-bottom:32px;">{results["summary"]}</p>', unsafe_allow_html=True)
        
        # 4-Column Grid layout using Streamlit columns
        grid_col1, grid_col2, grid_col3, grid_col4 = st.columns(4)
        
        with grid_col1:
            # ATS Score Card
            circ_html = components.render_circular_progress(results["ats_score"], results["status_color"])
            st.markdown(components.clean_html(f"""
            <div class="card" style="align-items: center; justify-content: center; min-height: 280px;">
                <div class="card-title" style="text-align: center;">ATS Score</div>
                {circ_html}
                <div style="font-size: 12px; color: #64748B; font-weight: 500; text-align: center; margin-top: 8px;">Target: 80+ for optimal clearance</div>
            </div>
            """), unsafe_allow_html=True)
            
        with grid_col2:
            # Match Breakdown Card
            breakdown_lines = ""
            for item in results["breakdown"]:
                breakdown_lines += components.render_linear_progress(f"{item['icon']} {item['category']}", item["score"], results["status_color"])
            
            st.markdown(components.clean_html(f"""
            <div class="card" style="min-height: 280px; justify-content: flex-start; gap: 8px;">
                <div class="card-title" style="margin-bottom: 8px;">Match Breakdown</div>
                {breakdown_lines}
            </div>
            """), unsafe_allow_html=True)
            
        with grid_col3:
            # Found Keywords Card
            keywords_html = "".join(f'<span class="chip" style="background-color:#E0F2FE; color:#0369A1; margin-right:8px; margin-bottom:8px;">{kw}</span>' for kw in results["found_keywords"])
            st.markdown(components.clean_html(f"""
            <div class="card" style="min-height: 280px; justify-content: flex-start;">
                <div class="card-title">Found Keywords</div>
                <p style="font-size: 13px; color:#64748B; margin: 0 0 12px 0;">Keywords successfully detected matching target industries:</p>
                <div class="tag-container">
                    {keywords_html if keywords_html else '<span class="chip chip-warning">No match keywords detected</span>'}
                </div>
            </div>
            """), unsafe_allow_html=True)
            
        with grid_col4:
            # Missing Skills Card
            missing_html = "".join(f'<span class="chip chip-error" style="margin-right:8px; margin-bottom:8px;">{sk}</span>' for sk in results["missing_skills"])
            st.markdown(components.clean_html(f"""
            <div class="card" style="min-height: 280px; justify-content: flex-start;">
                <div class="card-title">Missing Keywords</div>
                <p style="font-size: 13px; color:#64748B; margin: 0 0 12px 0;">Add these skills to your resume to increase your match percentage:</p>
                <div class="tag-container">
                    {missing_html if missing_html else '<span class="chip chip-success">✓ Perfect match! No missing skills</span>'}
                </div>
            </div>
            """), unsafe_allow_html=True)
            
        # AI Suggestions Card
        suggestions_list = "".join(f'<li style="font-size:14px; color:#1F2937; margin-bottom:12px; line-height:1.5;">{sug}</li>' for sug in results["suggestions"])
        st.markdown(components.clean_html(f"""
        <div class="card" style="margin-top: 32px; width: 100%;">
            <div class="card-title">✨ AI Optimization Suggestions</div>
            <ul style="margin: 0; padding-left: 20px;">
                {suggestions_list}
            </ul>
        </div>
        """), unsafe_allow_html=True)
        
        # Recommended Actions Card
        actions_rows = ""
        for act in results["recommended_actions"]:
            actions_rows += f"""
            <tr style="border-bottom: 1px solid #E2E8F0;">
                <td style="padding: 12px 16px; font-weight: 600; font-size:14px;">{act['action']}</td>
                <td style="padding: 12px 16px;"><span class="chip chip-info">{act['difficulty']}</span></td>
                <td style="padding: 12px 16px;"><span class="chip chip-success" style="background-color:#DCFCE7; color:#16A34A;">{act['impact']}</span></td>
            </tr>
            """
            
        st.markdown(components.clean_html(f"""
        <div class="card" style="margin-top: 32px; width: 100%;">
            <div class="card-title">📋 Recommended Actions</div>
            <table style="width: 100%; border-collapse: collapse; text-align: left; margin-top: 8px;">
                <thead>
                    <tr style="border-bottom: 2px solid #CBD5E1; color: #64748B; font-weight: 600; font-size:12px;">
                        <th style="padding: 8px 16px;">Action Required</th>
                        <th style="padding: 8px 16px;">Difficulty</th>
                        <th style="padding: 8px 16px;">Impact</th>
                    </tr>
                </thead>
                <tbody>
                    {actions_rows}
                </tbody>
            </table>
        </div>
        """), unsafe_allow_html=True)
        
        # Action Buttons footer — with visible spacer
        st.markdown('<div style="height: 32px;"></div>', unsafe_allow_html=True)
        col_res1, col_res2, col_res3 = st.columns(3)
        
        with col_res1:
            if st.button("Optimize Resume", type="primary", use_container_width=True):
                # Reuse cached result if already generated for this resume
                if st.session_state.optimized_resume:
                    st.session_state.analysis_stage = "optimize"
                else:
                    st.session_state.analysis_stage = "generating"
                st.rerun()
                
        with col_res2:
            if st.button("Generate Cover Letter", type="secondary", use_container_width=True):
                st.query_params["page"] = "cover_letter"
                st.rerun()
                
        with col_res3:
            if st.button("Upload Another Resume", type="secondary", use_container_width=True):
                st.session_state.analysis_stage = "upload"
                st.session_state.file_bytes = None
                st.session_state.file_name = None
                st.session_state.file_size = 0
                st.session_state.resume_text = ""
                st.session_state.metadata = None
                st.session_state.analysis_results = None
                st.session_state.optimized_resume = None
                st.session_state.job_desc = ""
                st.rerun()

    # STAGE 5a: GENERATING OPTIMIZED RESUME
    elif st.session_state.analysis_stage == "generating":
        st.markdown('<h1 class="hero-title" style="margin-bottom:16px;">Optimizing your resume...</h1>', unsafe_allow_html=True)
        st.markdown('<p class="hero-subtitle" style="margin-bottom:32px;">Gemini is rewriting your resume with stronger phrasing, injected keywords, and ATS-optimized formatting.</p>', unsafe_allow_html=True)

        status_box = st.empty()
        components.render_skeleton_loader()

        gen_stages = [
            "Reading resume structure and extracting content...",
            "Analyzing target job description for keyword gaps...",
            "Rewriting bullet points with action-verb strength...",
            "Injecting missing keywords naturally into context...",
            "Formatting and finalizing optimized document..."
        ]
        for stage in gen_stages:
            status_box.markdown(
                f'<div style="text-align:center; font-weight:600; font-size:16px; color:#2563EB; margin-bottom:24px;">🔄 {stage}</div>',
                unsafe_allow_html=True
            )
            time.sleep(0.7)

        # Run actual generation using the active key
        active_key = backend.get_active_api_key()
        optimized = backend.generate_optimized_resume_gemini(
            st.session_state.resume_text,
            st.session_state.metadata,
            st.session_state.job_desc,
            active_key
        )
        if optimized.get("quota_exceeded") and backend.is_using_default_key():
            st.session_state.quota_exceeded = True

        st.session_state.optimized_resume = optimized
        st.session_state.analysis_stage = "optimize"
        st.rerun()

    # STAGE 5b: SHOW OPTIMIZED RESUME
    elif st.session_state.analysis_stage == "optimize":
        # Guard: if resume was cleared, go back to generating
        if not st.session_state.optimized_resume:
            st.session_state.analysis_stage = "generating"
            st.rerun()

        components.render_ai_resume(st.session_state.optimized_resume)
        
        # Native Streamlit action controls (HTML onclick buttons are sandboxed by Streamlit)
        st.markdown('<div style="height: 32px; border-top: 1px solid #E2E8F0; margin-top: 40px;"></div>', unsafe_allow_html=True)
        col_opt1, col_opt2, col_opt3, col_opt4 = st.columns([1, 1, 1, 1])
        with col_opt1:
            if st.button("✍ Edit Manually", type="secondary", use_container_width=True):
                st.toast("✍ Manual editing mode — coming soon!")
        with col_opt2:
            try:
                # Generate PDF bytes dynamically from optimized resume data
                pdf_bytes = backend.generate_optimized_resume_pdf(st.session_state.optimized_resume)
                original_name = st.session_state.file_name or "Resume.pdf"
                base_name = os.path.splitext(original_name)[0]
                pdf_filename = f"Optimized_{base_name}.pdf"
                
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name=pdf_filename,
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.button("📥 Export PDF", type="secondary", disabled=True, use_container_width=True)
                st.error(f"Failed to generate PDF: {e}")
        with col_opt3:
            if st.button("✓ Apply All Changes", type="primary", use_container_width=True):
                st.success("✓ All optimization changes applied!")
                time.sleep(1)
                st.session_state.analysis_stage = "results"
                st.rerun()
        with col_opt4:
            if st.button("🔄 Re-generate", type="secondary", use_container_width=True):
                st.session_state.optimized_resume = None
                st.session_state.analysis_stage = "generating"
                st.rerun()

        st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
        if st.button("← Back to Report", type="secondary", use_container_width=True):
            st.session_state.analysis_stage = "results"
            st.rerun()

# ----------------- COVER LETTER PAGE -----------------
elif active_page == "cover_letter":
    st.markdown('<h1 class="section-title" style="width:100%; text-align:left; margin-bottom:16px;">📝 Cover Letter Generator</h1>', unsafe_allow_html=True)
    
    if not st.session_state.file_name:
        st.markdown(components.clean_html("""
        <div style="max-width: 600px; margin: 40px auto; width: 100%;">
            <div class="card" style="align-items: center; justify-content: center; min-height: 240px; padding: 40px 24px; text-align: center;">
                <div style="font-size: 48px; margin-bottom: 12px;">📄</div>
                <div class="card-title" style="font-size: 20px; margin-bottom: 8px;">No Resume Uploaded</div>
                <p style="color:#64748B; font-size:14.5px; line-height:1.6; margin-bottom: 20px;">Please upload your resume on the Home page first to generate a tailored cover letter.</p>
                <a href="?page=home" class="login-btn" style="text-decoration:none;" target="_self">Go to Home</a>
            </div>
        </div>
        """), unsafe_allow_html=True)
    else:
        with st.container(border=True):
            st.markdown(f'<div class="card-title">Generate Cover Letter for: {st.session_state.file_name}</div>', unsafe_allow_html=True)
            st.markdown('<p style="font-size:14px; color:#64748B; margin: 0 0 16px 0;">Paste the target job description below. The AI will extract the key competencies and frame an engaging cover letter aligning your resume history with this role.</p>', unsafe_allow_html=True)
            
            # Show target job description (default to the home page input if it exists)
            target_jd = st.text_area(
                "Paste Job Description",
                value=st.session_state.job_desc,
                placeholder="Paste target job requirements here...",
                label_visibility="collapsed",
                key="cl_jd_input"
            )
            st.session_state.job_desc = target_jd
            
            if st.button("Generate Tailored Cover Letter", type="primary"):
                with st.spinner("Generating cover letter with AI..."):
                    active_key = backend.get_active_api_key()
                    result = backend.generate_cover_letter_gemini(
                        st.session_state.resume_text,
                        st.session_state.metadata,
                        target_jd,
                        active_key
                    )
                    cl_text = result["text"]
                    if result.get("quota_exceeded") and backend.is_using_default_key():
                        st.session_state.quota_exceeded = True
                        cl_text += "\n\n─────────────────────────────\n🚨 Quota reached — template used. Add your API key in Settings for a real personalised letter."
                    st.session_state.generated_cl = cl_text
                    
            if "generated_cl" in st.session_state:
                st.markdown('<hr style="border: 0; border-top: 1px solid #CBD5E1; margin: 24px 0;" />', unsafe_allow_html=True)
                st.markdown('<div class="card-title">Generated Cover Letter</div>', unsafe_allow_html=True)
                st.text_area(
                    "Copy your cover letter:",
                    value=st.session_state.generated_cl,
                    height=300,
                    label_visibility="collapsed"
                )
                st.button("Reset Cover Letter", type="secondary", on_click=lambda: st.session_state.pop("generated_cl", None))

# ----------------- HISTORY PAGE -----------------
elif active_page == "history":
    st.markdown('<h1 class="section-title" style="width:100%; text-align:left; margin-bottom:16px;">🕒 History</h1>', unsafe_allow_html=True)

    history = st.session_state.get("history", [])
    if history:
        for i, entry in enumerate(reversed(history)):
            mode_color = "#DCFCE7" if entry.get("mode") == "Gemini AI" else "#FFF7ED"
            mode_text = "#16A34A" if entry.get("mode") == "Gemini AI" else "#C2410C"
            st.markdown(components.clean_html(f"""
            <div class="card" style="width: 100%; margin-bottom: 16px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
            <div style="font-weight:600; font-size:16px; color:#1F2937;">{entry.get('file_name', 'Resume')}</div>
            <div style="font-size:12px; color:#64748B; margin-top:4px;">Size: {entry.get('size', 'N/A')} • Pages: {entry.get('pages', 'N/A')}</div>
            </div>
            <div style="display:flex; gap:12px; align-items:center; flex-wrap:wrap;">
            <span class="chip" style="background:{mode_color}; color:{mode_text};">{entry.get('mode', 'Demo Mode')}</span>
            <span class="chip chip-success">ATS Score: {entry.get('ats_score', 'N/A')}</span>
            </div>
            </div>
            </div>
            """), unsafe_allow_html=True)
    else:
        st.markdown(components.clean_html("""
        <div class="card" style="align-items: center; justify-content: center; min-height: 240px;">
        <div style="font-size: 48px; margin-bottom: 8px;">🕒</div>
        <div class="card-title">No History Yet</div>
        <p style="color:#64748B; font-size:14px; text-align:center;">Analyze a resume to start building your history.</p>
        <a href="?page=home" class="login-btn" style="text-decoration:none; margin-top:12px;" target="_self">Upload Resume Now</a>
        </div>
        """), unsafe_allow_html=True)

# ----------------- SETTINGS PAGE -----------------
elif active_page == "settings":
    st.markdown('<h1 class="section-title" style="width:100%; text-align:left; margin-bottom:16px;">⚙ Settings</h1>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div class="card-title">Gemini API Key Integration</div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:14px; color:#64748B; margin: 0 0 16px 0;">Add your own Gemini API key for unlimited real AI analysis. The app uses a shared built-in key by default — your custom key is saved permanently and survives page refreshes.</p>', unsafe_allow_html=True)

        # Show current key source status
        if backend.is_using_default_key():
            key_status_html = '<span class="chip chip-info" style="margin-bottom:12px; display:inline-block;">⚡ Using built-in shared key</span>'
        else:
            key_status_html = '<span class="chip chip-success" style="margin-bottom:12px; display:inline-block;">✓ Using your personal API key</span>'
        st.markdown(key_status_html, unsafe_allow_html=True)

        api_key_input = st.text_input(
            "Enter Google Gemini API Key",
            value=st.session_state.api_key,
            type="password",
            placeholder="AIzaSy...",
            key="api_key_input_widget"
        )

        col_set1, col_set2, col_set3 = st.columns([1, 1, 2])
        with col_set1:
            if st.button("Save Key", type="primary", use_container_width=True):
                st.session_state.api_key = api_key_input
                backend.save_config({"user_api_key": api_key_input})
                st.session_state.quota_exceeded = False  # reset quota flag
                st.success("✓ API Key saved securely for this machine.")
                st.rerun()
        with col_set2:
            if st.button("Test Connection", type="secondary", use_container_width=True):
                test_key = api_key_input or backend.get_active_api_key()
                with st.spinner("Testing connection..."):
                    result = backend.validate_api_key(test_key)
                if result["valid"]:
                    st.success(result["message"])
                else:
                    st.error(result["message"])
        with col_set3:
            if st.session_state.api_key:
                st.markdown('<span class="chip chip-success" style="height:38px; line-height:38px; padding: 0 16px; font-weight:600;">✓ Active: Your Personal Key</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="chip chip-info" style="height:38px; line-height:38px; padding: 0 16px; font-weight:600;">⚡ Using built-in shared key</span>', unsafe_allow_html=True)

        # Clear key option
        if st.session_state.api_key:
            st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
            if st.button("Clear Personal Key (revert to built-in)", type="secondary"):
                st.session_state.api_key = ""
                backend.save_config({"user_api_key": ""})
                st.session_state.quota_exceeded = False
                st.success("✓ Cleared the saved personal key.")
                st.rerun()

    st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="card-title">How to get a Gemini API Key</div>', unsafe_allow_html=True)
        st.markdown(components.clean_html("""
        <ol style="font-size:14px; color:#374151; line-height:2; padding-left:20px; margin:8px 0 0 0;">
        <li>Visit <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color:#2563EB; font-weight:600;">Google AI Studio</a> and sign in with your Google account.</li>
        <li>Click <strong>"Create API Key"</strong> and copy the generated key.</li>
        <li>Paste it into the field above and click <strong>Save Key</strong>.</li>
        <li>Click <strong>Test Connection</strong> to verify it works.</li>
        </ol>
        """), unsafe_allow_html=True)

elif active_page == "login":
    col_space1, col_login, col_space2 = st.columns([1, 1.2, 1])
    with col_login:
        with st.container(border=True):
            st.markdown('<div class="document-illustration" style="text-align:center; margin-bottom: 12px;">📄</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-title" style="text-align:center; font-size:22px; margin-bottom:6px;">Sign in to your account</div>', unsafe_allow_html=True)
            st.markdown('<p style="text-align:center; font-size:12px; color:#94A3B8; margin:0 0 20px 0;">Demo only — authentication not yet active</p>', unsafe_allow_html=True)

            st.text_input("Email address", placeholder="name@company.com")
            st.text_input("Password", type="password", placeholder="••••••••")

            if st.button("Sign In", type="primary", use_container_width=True):
                st.success("✓ Signed in successfully (Demo mode)")
                st.query_params["page"] = "home"
                st.rerun()

            st.markdown('<p style="font-size:12px; color:#64748B; text-align:center; margin:16px 0 0 0;">Authentication features coming soon.</p>', unsafe_allow_html=True)


# --- RENDER GLOBAL FOOTER ---
components.render_footer()

