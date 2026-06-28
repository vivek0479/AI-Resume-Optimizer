import streamlit as st
import html

def clean_html(html_str: str) -> str:
    """
    Removes leading whitespace from each line of an HTML string 
    to prevent Markdown parsers from treating it as an indented code block.
    """
    return "\n".join(line.strip() for line in html_str.split("\n"))

def load_css(file_name="style.css"):
    """
    Loads and injects style.css into the Streamlit app.
    """
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_navbar(active_page="home"):
    """
    Renders the custom premium 72px navigation bar.
    Using query params for native page routing.
    """
    # Create HTML structure for the navbar
    navbar_html = f"""
<div class="navbar-wrapper">
<div class="navbar">
<a href="?page=home" class="navbar-logo" target="_self">
📄 <span>AI Resume Optimizer</span>
</a>
<div class="navbar-menu">
<a href="?page=home" class="nav-item {"active" if active_page == "home" else ""}" target="_self">🏠 Home</a>
<a href="?page=cover_letter" class="nav-item {"active" if active_page == "cover_letter" else ""}" target="_self">📝 Cover Letter</a>
<a href="?page=history" class="nav-item {"active" if active_page == "history" else ""}" target="_self">🕒 History</a>
<a href="?page=settings" class="nav-item {"active" if active_page == "settings" else ""}" target="_self">⚙ Settings</a>
</div>
<div class="navbar-actions">
<a href="?page=login" class="login-btn" target="_self">Login</a>
</div>
</div>
</div>
"""
    st.markdown(clean_html(navbar_html), unsafe_allow_html=True)

def render_circular_progress(percentage, status_color="#2563EB"):
    """
    Renders a premium SVG circular progress indicator.
    """
    # SVG circle circumference for r=40 is 2 * pi * 40 ≈ 251.2
    circumference = 251.2
    offset = circumference * (1 - (percentage / 100.0))
    
    html = f"""
    <div class="circular-progress">
        <svg viewBox="0 0 100 100">
            <circle class="bg-circle" cx="50" cy="50" r="40" />
            <circle class="fg-circle" cx="50" cy="50" r="40" 
                    style="stroke-dasharray: {circumference}; stroke-dashoffset: {offset}; stroke: {status_color};" />
        </svg>
        <div class="circular-progress-text">{percentage}</div>
    </div>
    """
    return clean_html(html)

def render_linear_progress(label, percentage, color="#2563EB"):
    """
    Renders a clean linear progress bar.
    """
    html = f"""
    <div style="margin-bottom: 16px;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
            <span style="font-weight: 500; font-size: 14px; color: #1F2937;">{label}</span>
            <span style="font-weight: 600; font-size: 14px; color: {color};">{percentage}%</span>
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: {percentage}%; background-color: {color};"></div>
        </div>
    </div>
    """
    return clean_html(html)

def render_skeleton_loader():
    """
    Renders professional animated skeleton loaders for the analysis phase.
    """
    html = """
    <div class="card" style="width: 100%; max-width: 780px; margin: 0 auto; gap: 20px;">
        <div class="skeleton-loader">
            <div class="skeleton-item" style="height: 32px; width: 40%;"></div>
            <div class="skeleton-item" style="height: 16px; width: 90%;"></div>
            <div class="skeleton-item" style="height: 16px; width: 75%;"></div>
        </div>
        <hr style="border: 0; border-top: 1px solid #E2E8F0; margin: 0;" />
        <div class="skeleton-loader">
            <div class="skeleton-item" style="height: 24px; width: 25%;"></div>
            <div class="skeleton-item" style="height: 16px; width: 80%;"></div>
            <div class="skeleton-item" style="height: 16px; width: 85%;"></div>
            <div class="skeleton-item" style="height: 16px; width: 60%;"></div>
        </div>
    </div>
    """
    st.markdown(clean_html(html), unsafe_allow_html=True)

def render_ai_resume(resume_data: dict):
    """
    Renders the AI-generated optimized resume as a premium document sheet.
    Takes the structured dict from generate_optimized_resume_gemini/mock.
    """
    source = resume_data.get("source", "mock")
    badge_label = "✨ Gemini AI Optimized" if source == "gemini" else "⚡ AI Optimized (Demo Mode)"
    badge_color = "#EFF6FF" if source == "gemini" else "#FFF7ED"
    badge_border = "#DBEAFE" if source == "gemini" else "#FED7AA"
    badge_text_color = "#2563EB" if source == "gemini" else "#C2410C"

    error_html = ""
    if resume_data.get("error"):
        error_html = f'<div style="background:#FEF2F2; border:1px solid #FCA5A5; border-radius:8px; padding:12px 16px; margin-bottom:16px; font-size:13px; color:#DC2626;">⚠ Gemini error — showing demo optimization: {resume_data["error"]}</div>'

    # ---- Header ----
    name = html.escape(resume_data.get("name", "Your Name"))
    contact = html.escape(resume_data.get("contact", ""))

    # ---- Summary ----
    summary = html.escape(resume_data.get("summary", ""))

    # ---- Experience bullets ----
    exp_html = ""
    for job in resume_data.get("experience", []):
        bullets_html = ""
        for b in job.get("bullets", []):
            btype = b.get("type", "original")
            annotation = html.escape(b.get("annotation", ""))
            text = html.escape(b.get("text", ""))
            if btype == "rephrased":
                bullet_class = "resume-highlight-blue"
                prefix = f'<span style="font-size:11px; font-weight:700; color:#1D4ED8; text-transform:uppercase; letter-spacing:0.04em;">✏ Rephrased</span><br>' if annotation else ""
            elif btype == "injected":
                bullet_class = "resume-highlight-green"
                prefix = f'<span style="font-size:11px; font-weight:700; color:#15803D; text-transform:uppercase; letter-spacing:0.04em;">+ {annotation}</span><br>' if annotation else ""
            else:
                bullet_class = ""
                prefix = ""

            if bullet_class:
                bullets_html += f'<li class="resume-bullet-item {bullet_class}">{prefix}{text}</li>'
            else:
                bullets_html += f'<li class="resume-bullet-item">{text}</li>'

        exp_html += f"""
<div class="resume-job">
<div class="resume-job-header">
<span class="resume-job-title">{html.escape(job.get("title", ""))}</span>
<span class="resume-job-date">{html.escape(job.get("dates", ""))}</span>
</div>
<div class="resume-job-company">{html.escape(job.get("company", ""))}</div>
<ul class="resume-bullets">{bullets_html}</ul>
</div>"""

    # ---- Skills ----
    skills_html = ""
    for cat in resume_data.get("skills", {}).get("categories", []):
        cat_name = html.escape(cat.get("name", ""))
        highlighted = cat.get("highlighted", [])
        items_html = "".join(
            f'<span class="chip skill-tag-active">{html.escape(item)}</span>' if item in highlighted
            else f'<span class="chip" style="background-color:#F1F5F9; color:#475569; border:1px solid #E2E8F0;">{html.escape(item)}</span>'
            for item in cat.get("items", [])
        )
        skills_html += f"""
<div class="skills-grid">
<span class="skills-category">{cat_name}</span>
<div class="skills-list">{items_html}</div>
</div>"""

    # ---- Education ----
    edu_html = ""
    for edu in resume_data.get("education", []):
        edu_html += f"""
<div class="resume-job">
<div class="resume-job-header">
<span class="resume-job-title">{html.escape(edu.get("degree", ""))}</span>
<span class="resume-job-date">{html.escape(edu.get("dates", ""))}</span>
</div>
<div class="resume-job-company" style="color:#4B5563;">{html.escape(edu.get("institution", ""))}</div>
</div>"""

    # ---- Changes sidebar ----
    changes = resume_data.get("changes_summary", [])
    changes_html = "".join(
        f'<div style="display:flex; gap:8px; align-items:flex-start; margin-bottom:10px;"><span style="color:#2563EB; font-size:16px; line-height:1.2;">›</span><span style="font-size:13px; color:#374151; line-height:1.5;">{html.escape(c)}</span></div>'
        for c in changes
    )

    resume_html = f"""
{error_html}
<div style="text-align:center; margin-bottom:12px;">
<span style="display:inline-flex; align-items:center; background-color:{badge_color}; color:{badge_text_color}; border:1px solid {badge_border}; padding:6px 16px; border-radius:9999px; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.05em;">{badge_label}</span>
</div>
<h1 class="hero-title" style="margin-bottom:6px;">Optimized Resume</h1>
<p class="hero-subtitle" style="margin-bottom:36px;">AI has improved keyword density, impact phrasing, and layout hierarchy.</p>
<div class="optimize-layout">
<div class="annotation-bar">
<div style="position:sticky; top:100px;">
<div style="font-size:11px; font-weight:700; color:#2563EB; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:12px;">Changes Made</div>
{changes_html}
<div style="margin-top:24px; border-top:1px solid #E2E8F0; padding-top:16px;">
<div style="display:flex; align-items:center; gap:6px; margin-bottom:8px;"><span style="width:12px; height:12px; background:#EFF6FF; border-left:3px solid #2563EB; display:inline-block; border-radius:1px;"></span><span style="font-size:11px; color:#64748B;">Rephrased</span></div>
<div style="display:flex; align-items:center; gap:6px;"><span style="width:12px; height:12px; background:#F0FDF4; border-left:3px solid #16A34A; display:inline-block; border-radius:1px;"></span><span style="font-size:11px; color:#64748B;">Keyword Added</span></div>
</div>
</div>
</div>
<div class="resume-sheet">
<div class="resume-header">
<div class="resume-name">{name}</div>
<div class="resume-contact">{contact}</div>
</div>
<div class="resume-section">
<h3 class="resume-section-title">Professional Summary</h3>
<div class="resume-summary-box">{summary}</div>
</div>
<div class="resume-section">
<h3 class="resume-section-title">Work Experience</h3>
{exp_html}
</div>
<div class="resume-section">
<h3 class="resume-section-title">Expertise &amp; Skills</h3>
<div style="display:flex; flex-direction:column; gap:12px;">{skills_html}</div>
</div>
<div class="resume-section">
<h3 class="resume-section-title">Education</h3>
{edu_html}
</div>
</div>
</div>
"""
    st.markdown(clean_html(resume_html), unsafe_allow_html=True)



def render_optimized_resume():
    """
    Renders the high-fidelity Optimized Resume document layout, 
    matching the Senior Product Designer at Google preview sheet.
    """
    html = """
    <div class="badge-ai-container" style="text-align: center; width: 100%;">
        <span class="badge-ai">✨ AI Optimization Ready</span>
    </div>
    
    <h1 class="hero-title" style="margin-bottom: 8px;">Optimized Resume</h1>
    <p class="hero-subtitle" style="margin-bottom: 48px;">
        Refined for the <strong>Senior Product Designer</strong> role at Google. AI has improved keyword density, impact phrasing, and layout hierarchy.
    </p>
    
    <div class="optimize-layout">
        <!-- Annotation Bar column -->
        <div class="annotation-bar">
            <div class="annotation-item" style="top: 140px;">
                <div class="annotation-label">Refinement</div>
                <div class="annotation-text">"Rephrased for higher impact and action-verb strength."</div>
            </div>
            
            <div class="annotation-item" style="top: 380px;">
                <div class="annotation-label">Refinement</div>
                <div class="annotation-text">"Aligned with Google's design system scaling guidelines."</div>
            </div>
            
            <div class="annotation-item" style="top: 550px;">
                <div class="annotation-label">Keyword Injection</div>
                <div class="annotation-text">"Injected Figma and Dovetail tools linked with user studies."</div>
            </div>
        </div>
        
        <!-- Document Sheet column -->
        <div class="resume-sheet">
            <div class="resume-header">
                <div class="resume-name">Jordan Smith</div>
                <div class="resume-contact">
                    San Francisco, CA &nbsp;•&nbsp; 
                    <a href="mailto:jordan.smith@design.com">jordan.smith@design.com</a> &nbsp;•&nbsp; 
                    +1 (555) 012-3456 &nbsp;•&nbsp; 
                    <a href="https://portfolio.jordan.design" target="_blank">portfolio.jordan.design</a>
                </div>
            </div>
            
            <!-- Professional Summary -->
            <div class="resume-section">
                <h3 class="resume-section-title">Professional Summary</h3>
                <div class="resume-summary-box">
                    Senior Product Designer with 8+ years of experience specialized in crafting high-impact digital ecosystems and scalable design systems. Proven track record of <strong>increasing conversion rates by 22%</strong> through data-driven UI/UX iterations and cross-functional leadership in Agile environments.
                </div>
            </div>
            
            <!-- Work Experience -->
            <div class="resume-section">
                <h3 class="resume-section-title">Work Experience</h3>
                
                <!-- Job 1 -->
                <div class="resume-job">
                    <div class="resume-job-header">
                        <span class="resume-job-title">Lead Product Designer</span>
                        <span class="resume-job-date">2020 – Present</span>
                    </div>
                    <div class="resume-job-company">Linear Systems • San Francisco, CA</div>
                    <ul class="resume-bullets">
                        <li class="resume-bullet-item">Spearheaded the complete redesign of the core enterprise dashboard, resulting in a 40% reduction in user task completion time.</li>
                        <li class="resume-bullet-item resume-highlight-blue">
                            <strong>AI Re-phrased:</strong> Directed design systems architecture, improving designer output by 15% and establishing a new internal workflow baseline.
                        </li>
                        <li class="resume-bullet-item">Mentored a team of 6 junior and mid-level designers, fostering a culture of rapid prototyping and user-centric problem solving.</li>
                    </ul>
                </div>
                
                <!-- Job 2 -->
                <div class="resume-job">
                    <div class="resume-job-header">
                        <span class="resume-job-title">Senior Interaction Designer</span>
                        <span class="resume-job-date">2017 – 2020</span>
                    </div>
                    <div class="resume-job-company">FinTech Global • New York, NY</div>
                    <ul class="resume-bullets">
                        <li class="resume-bullet-item">Developed a comprehensive Design System (FinUI) used across 12 product squads, ensuring 100% brand consistency and reducing development hand-off time by 30%.</li>
                        <li class="resume-bullet-item resume-highlight-green">
                            <strong>Added Keyword:</strong> Orchestrated cross-platform user research studies using <strong>Figma</strong> and <strong>Dovetail</strong> to validate navigation patterns for over 2M active users.
                        </li>
                    </ul>
                </div>
            </div>
            
            <!-- Expertise & Skills -->
            <div class="resume-section">
                <h3 class="resume-section-title">Expertise & Skills</h3>
                <div style="display:flex; flex-direction:column; gap:12px;">
                    <div class="skills-grid">
                        <span class="skills-category">Design</span>
                        <div class="skills-list">
                            <span class="chip" style="background-color:#F1F5F9; color:#475569; border:1px solid #E2E8F0;">Product Strategy</span>
                            <span class="chip" style="background-color:#F1F5F9; color:#475569; border:1px solid #E2E8F0;">Design Systems</span>
                            <span class="chip skill-tag-active">Prototyping</span>
                            <span class="chip" style="background-color:#F1F5F9; color:#475569; border:1px solid #E2E8F0;">User Research</span>
                        </div>
                    </div>
                    
                    <div class="skills-grid">
                        <span class="skills-category">Technical</span>
                        <div class="skills-list">
                            <span class="chip" style="background-color:#F1F5F9; color:#475569; border:1px solid #E2E8F0;">Figma</span>
                            <span class="chip" style="background-color:#F1F5F9; color:#475569; border:1px solid #E2E8F0;">React/CSS</span>
                            <span class="chip" style="background-color:#F1F5F9; color:#475569; border:1px solid #E2E8F0;">Adobe Suite</span>
                            <span class="chip skill-tag-active">AI Prompting</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Education -->
            <div class="resume-section">
                <h3 class="resume-section-title">Education</h3>
                <div class="resume-job">
                    <div class="resume-job-header">
                        <span class="resume-job-title">BFA in Communication Design</span>
                        <span class="resume-job-date">May 2016</span>
                    </div>
                    <div class="resume-job-company" style="color:#4B5563;">Parsons School of Design</div>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(clean_html(html), unsafe_allow_html=True)


def render_footer():
    """
    Renders a premium global footer with feedback links, social media SVGs,
    and a 'Made with ❤️ by Vivekananda' credit.
    """
    footer_html = """
    <div class="footer-wrapper">
        <div class="footer-divider"></div>
        <div class="footer-container">
            <div class="footer-left">
                <span class="footer-brand">📄 AI Resume Optimizer</span>
                <p class="footer-tagline">Secure, private, AI-powered career growth platform.</p>
            </div>
            <div class="footer-middle">
                Made with <span style="color: #EF4444; animation: heart-pulse 1.2s infinite; display: inline-block;">❤️</span> by <span style="font-weight: 700; color: #1F2937;">Vivekananda</span>
            </div>
            <div class="footer-right">
                <a href="mailto:vivekananda@example.com?subject=AI Resume Optimizer Feedback" class="footer-link">💬 Feedback &amp; Support</a>
                <div class="footer-socials">
                    <a href="https://github.com" target="_blank" aria-label="GitHub" style="color: #4B5563 !important;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.579.688.481C19.137 20.162 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
                        </svg>
                    </a>
                    <a href="https://linkedin.com" target="_blank" aria-label="LinkedIn" style="color: #0A66C2 !important;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.779-1.75-1.75s.784-1.75 1.75-1.75 1.75.779 1.75 1.75-.784 1.75-1.75 1.75zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                        </svg>
                    </a>
                </div>
            </div>
        </div>
        <div class="footer-security-row">
            🔒 Fully Sandboxed. API keys are managed exclusively on the server side and never sent to the client browser.
        </div>
    </div>
    """
    st.markdown(clean_html(footer_html), unsafe_allow_html=True)

