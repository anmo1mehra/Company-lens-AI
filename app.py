import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from src.utils import is_url, normalize_url, sanitize_filename
from src.serper_search import find_official_website, gather_serper_insights
from src.crawler import CompanyCrawler
from src.openrouter_client import OpenRouterClient, DEFAULT_MODELS
from src.pdf_generator import generate_company_report_pdf
from src.discord_client import send_report_to_discord

st.set_page_config(
    page_title="Relu Consultancy - Company Intelligence",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0B0F19 !important;
        color: #E2E8F0 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1F2937 !important;
    }
    
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.1rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 2px;
    }
    .sidebar-subbrand {
        font-size: 0.75rem;
        letter-spacing: 1px;
        color: #64748B;
        text-transform: uppercase;
        margin-bottom: 15px;
    }
    
    .hero-container {
        text-align: center;
        padding: 50px 20px 30px 20px;
        max-width: 800px;
        margin: 0 auto;
    }
    .hero-tag {
        color: #D97706;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 15px;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        color: #F8FAFC;
        line-height: 1.1;
        margin-bottom: 15px;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #94A3B8;
        max-width: 600px;
        margin: 0 auto 30px auto;
        line-height: 1.5;
    }
    
    .pill-btn {
        background-color: #1E293B;
        border: 1px solid #334155;
        color: #CBD5E1;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 4px;
        cursor: pointer;
    }
    
    .report-card {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
    }
    .report-header-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #F8FAFC;
    }
    .report-header-url {
        font-size: 0.9rem;
        color: #D97706;
        margin-bottom: 20px;
    }
    .info-box {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 15px;
    }
    .info-box-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        color: #64748B;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }
    .info-box-val {
        font-size: 0.95rem;
        color: #F1F5F9;
    }
    
    .section-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        color: #D97706;
        letter-spacing: 1px;
        font-weight: 700;
        margin: 20px 0 10px 0;
    }
    
    .tag-pill {
        background-color: #1E293B;
        border: 1px solid #334155;
        color: #E2E8F0;
        padding: 6px 14px;
        border-radius: 6px;
        font-size: 0.85rem;
        display: inline-block;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    
    .comp-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .comp-name {
        font-weight: 700;
        color: #F8FAFC;
        font-size: 0.95rem;
    }
    .comp-site {
        font-size: 0.8rem;
        color: #60A5FA;
    }
    
    div.stButton > button {
        background-color: #F59E0B !important;
        color: #0F172A !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 6px !important;
    }
</style>
""", unsafe_allow_html=True)

if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None
if "discord_res" not in st.session_state:
    st.session_state.discord_res = None
if "preset_prompt" not in st.session_state:
    st.session_state.preset_prompt = ""

with st.sidebar:
    st.markdown('<div class="sidebar-brand">🔷 Relu Consultancy</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subbrand">COMPANY INTELLIGENCE</div>', unsafe_allow_html=True)
    
    if st.button("+ New Research", use_container_width=True):
        st.session_state.report_data = None
        st.session_state.pdf_path = None
        st.session_state.discord_res = None
        st.session_state.preset_prompt = ""
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab_api, tab_discord = st.tabs(["API", "DISCORD"])
    
    with tab_api:
        env_openrouter = os.getenv("OPENROUTER_API_KEY", "")
        env_serper = os.getenv("SERPER_API_KEY", "")
        
        openrouter_key = st.text_input("OPENROUTER API KEY", value=env_openrouter, type="password")
        serper_key = st.text_input("SERPER.DEV API KEY", value=env_serper, type="password")
        
        selected_model = st.selectbox(
            "AI MODEL",
            options=DEFAULT_MODELS,
            index=0
        )
        
        if st.button("Save Configuration", use_container_width=True):
            st.success("Configuration Saved ✓")

    with tab_discord:
        st.caption("After research completes, the report auto-sends to your configured channel.")
        discord_token = st.text_input("BOT TOKEN", value=os.getenv("DISCORD_BOT_TOKEN", ""), type="password")
        discord_channel = st.text_input("CHANNEL ID", value=os.getenv("DISCORD_CHANNEL_ID", ""))
        
        st.markdown("**APPLICANT DETAILS**")
        applicant_name = st.text_input("Full Name", value=os.getenv("APPLICANT_NAME", "ANMOL MEHRA"))
        applicant_email = st.text_input("Email Address", value=os.getenv("APPLICANT_EMAIL", ""))
        
        if st.button("Save Discord Config", use_container_width=True):
            st.success("Saved ✓")

    st.markdown("---")
    st.markdown("<div style='font-size:0.75rem; color:#64748B; font-weight:700;'>HOW IT WORKS</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.8rem; color:#94A3B8; margin-top:8px;'>
    <b style='color:#F59E0B'>1</b> Enter a company name or URL<br>
    <b style='color:#F59E0B'>2</b> Serper.dev searches and crawls it<br>
    <b style='color:#F59E0B'>3</b> OpenRouter AI generates insights<br>
    <b style='color:#F59E0B'>4</b> Download a professional PDF report
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='font-size:0.75rem; color:#64748B; margin-top:20px; font-weight:600;'>Created by ANMOL MEHRA</div>", unsafe_allow_html=True)

st.markdown("""
<div style='display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1F2937; padding-bottom:10px; margin-bottom:20px;'>
    <div style='font-size:1.1rem; font-weight:700; color:#F8FAFC;'>Company Research</div>
    <div style='background-color:#064E3B; color:#34D399; padding:4px 10px; border-radius:12px; font-size:0.75rem; font-weight:700;'>• LIVE</div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.report_data:
    st.markdown("""
    <div class="hero-container">
        <div class="hero-tag">AI-Powered Intelligence</div>
        <div class="hero-title">Know any company in minutes.</div>
        <div class="hero-subtitle">Enter a company name or website URL to get AI-powered insights, competitor analysis, pain points, and a professional PDF report.</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        if st.button("stripe.com", use_container_width=True):
            st.session_state.preset_prompt = "https://stripe.com"
    with col_p2:
        if st.button("Tesla", use_container_width=True):
            st.session_state.preset_prompt = "Tesla"
    with col_p3:
        if st.button("Microsoft", use_container_width=True):
            st.session_state.preset_prompt = "Microsoft"
    with col_p4:
        if st.button("Figma", use_container_width=True):
            st.session_state.preset_prompt = "Figma"
            
    st.markdown("<div style='text-align:center; font-size:0.8rem; color:#64748B; margin-top:40px;'>Configure API keys in the sidebar to get started</div>", unsafe_allow_html=True)

else:
    r_data = st.session_state.report_data
    p_path = st.session_state.pdf_path
    d_res = st.session_state.discord_res
    
    st.markdown(f"""
    <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
        <div>
            <div class="report-header-title">{r_data.get('company_name')}</div>
            <div class="report-header-url">{r_data.get('website')}</div>
        </div>
        <div style='background-color:#064E3B; color:#34D399; padding:6px 12px; border-radius:6px; font-size:0.75rem; font-weight:700;'>RESEARCH COMPLETE</div>
    </div>
    """, unsafe_allow_html=True)
    
    c_ph, c_addr = st.columns(2)
    with c_ph:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-box-label">PHONE</div>
            <div class="info-box-val">{r_data.get('phone_number')}</div>
        </div>
        """, unsafe_allow_html=True)
    with c_addr:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-box-label">ADDRESS</div>
            <div class="info-box-val">{r_data.get('address')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">PRODUCTS & SERVICES</div>', unsafe_allow_html=True)
    prods = r_data.get("products_services", [])
    if isinstance(prods, list) and prods:
        tags_html = "".join([f'<div class="tag-pill">{p}</div>' for p in prods])
        st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)
    else:
        st.write(prods or "Not found in available sources.")

    st.markdown('<div class="section-label">AI-GENERATED PAIN POINTS</div>', unsafe_allow_html=True)
    pains = r_data.get("pain_points", [])
    if isinstance(pains, list) and pains:
        for pt in pains:
            st.markdown(f"• {pt}")
    else:
        st.write(pains or "Not found in available sources.")

    st.markdown('<div class="section-label">COMPETITORS</div>', unsafe_allow_html=True)
    comps = r_data.get("competitors", [])
    if isinstance(comps, list) and comps:
        col_c1, col_c2, col_c3 = st.columns(3)
        for idx, comp in enumerate(comps):
            target_col = [col_c1, col_c2, col_c3][idx % 3]
            c_name = comp.get("name", "Competitor") if isinstance(comp, dict) else str(comp)
            c_site = comp.get("website", "") if isinstance(comp, dict) else ""
            with target_col:
                st.markdown(f"""
                <div class="comp-card">
                    <div class="comp-name">{c_name}</div>
                    <div class="comp-site">{c_site}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.write("Not found in available sources.")

    st.markdown("<br>", unsafe_allow_html=True)
    col_act1, col_act2 = st.columns([1, 4])
    with col_act1:
        if p_path and os.path.exists(p_path):
            with open(p_path, "rb") as f:
                st.download_button(
                    label="↓ Download PDF Report",
                    data=f.read(),
                    file_name=os.path.basename(p_path),
                    mime="application/pdf",
                    use_container_width=True
                )
    with col_act2:
        if d_res and d_res.get("success"):
            st.markdown("<div style='background-color:#064E3B; color:#34D399; display:inline-block; padding:8px 16px; border-radius:6px; font-weight:700; font-size:0.85rem;'>✓ Sent to Discord</div>", unsafe_allow_html=True)
        elif d_res and not d_res.get("success"):
            st.warning(f"Discord notice: {d_res.get('error')}")

st.markdown("<br><br>", unsafe_allow_html=True)
with st.form("research_form", clear_on_submit=False):
    col_in, col_btn = st.columns([5, 1])
    with col_in:
        default_val = st.session_state.preset_prompt if st.session_state.preset_prompt else ""
        user_input = st.text_input(
            "Company search query",
            value=default_val,
            placeholder="Enter a company name (e.g. Aurora Labs) or website URL (e.g. https://aurora.dev)...",
            label_visibility="collapsed"
        )
    with col_btn:
        submitted = st.form_submit_button("Research →", use_container_width=True)

st.markdown("<div style='text-align:center; font-size:0.8rem; color:#64748B; margin-top:20px; font-weight:600;'>CompanyLens AI • Created by ANMOL MEHRA</div>", unsafe_allow_html=True)

if submitted and user_input.strip():
    status_container = st.status("Analyzing company intelligence...", expanded=True)
    try:
        if not serper_key or not openrouter_key:
            status_container.update(label="API Keys Required", state="error", expanded=False)
            st.error("Please configure OPENROUTER_API_KEY and SERPER_API_KEY in the sidebar.")
            st.stop()

        status_container.write("1. Resolving official website URL...")
        if is_url(user_input):
            official_url = normalize_url(user_input)
            company_identifier = user_input
        else:
            company_identifier = user_input.strip()
            official_url = find_official_website(company_identifier, serper_key)
            if not official_url:
                official_url = f"https://{sanitize_filename(company_identifier).lower()}.com"

        status_container.write(f"Target site: `{official_url}`")

        status_container.write("2. Gathering Serper.dev search intelligence & competitor leads...")
        search_insights = gather_serper_insights(company_identifier, official_url, serper_key)

        status_container.write("3. Crawling website internal pages...")
        crawler = CompanyCrawler(start_url=official_url, max_pages=10)
        crawled_data = crawler.crawl()

        status_container.write(f"4. Synthesizing research with OpenRouter ({selected_model})...")
        ai_client = OpenRouterClient(api_key=openrouter_key)
        report_data = ai_client.generate_company_research(
            company_identifier=company_identifier,
            official_url=official_url,
            crawl_data=crawled_data,
            search_data=search_insights,
            model=selected_model
        )

        status_container.write("5. Generating downloadable PDF report...")
        safe_name = sanitize_filename(report_data.get("company_name", company_identifier))
        output_pdf_path = os.path.join("outputs", "reports", f"{safe_name}_report.pdf")
        generate_company_report_pdf(report_data, output_pdf_path)

        discord_result = None
        if discord_token and discord_channel:
            status_container.write("Uploading report to Discord channel...")
            discord_result = send_report_to_discord(
                bot_token=discord_token,
                channel_id=discord_channel,
                applicant_name=applicant_name,
                applicant_email=applicant_email,
                company_name=report_data.get("company_name", company_identifier),
                company_website=report_data.get("website", official_url),
                pdf_path=output_pdf_path
            )

        status_container.update(label="Research Complete!", state="complete", expanded=False)

        st.session_state.report_data = report_data
        st.session_state.pdf_path = output_pdf_path
        st.session_state.discord_res = discord_result
        st.rerun()

    except Exception as e:
        status_container.update(label="Research failed", state="error", expanded=True)
        st.error(f"Error: {str(e)}")
