# app.py - AI Red Team Assistant Full Version

from llm_engine import RedTeamAssistant
from report_gen import generate_report
import os
import json
import streamlit as st
from groq import Groq

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Red Team Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': "AI Red Team Assistant - Hackathon Prototype\nAuthor: Ammara Khan"}
)

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def load_mitre_data():
    try:
        with open('mitre_attack.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("⚠️ mitre_attack.json not found. Please upload it.")
        return None

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.title("🛡️ AI Red Team Assistant")
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "🔍 OSINT Generator", "📊 MITRE Techniques"]
)
st.sidebar.markdown("---")

api_key = os.environ.get("GROQ_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Enter Groq API Key", type="password", placeholder="gsk_...")

st.sidebar.caption("🛡️ For ethical & educational use only")

# ─────────────────────────────────────────────
# HOME PAGE
# ─────────────────────────────────────────────
if page == "🏠 Home":
    st.title("🛡️ AI Red Team Assistant – Phase 1: Scoping & Recon Planning")
    st.write("Enter a target below to generate Recon checklist and final playbook.")

    target = st.text_input("🎯 Enter Target (e.g., example.com)")

    if st.button("Save Target"):
        if target.strip():
            st.session_state["target"] = target.strip()
            st.success(f"✅ Target saved: {target.strip()}")
        else:
            st.warning("⚠️ Please enter a target.")

    if st.button("🚀 Generate Recon Plan"):
        if not target:
            st.warning("Please enter a target first.")
        else:
            assistant = RedTeamAssistant()
            assistant.generate_recon_plan(target)
            st.success("✅ Recon JSON Generated Successfully!")

    if st.button("📄 Generate Final Playbook"):
        try:
            report = generate_report()
            st.text(report)
            st.download_button(
                label="Download Playbook",
                data=report,
                file_name="final_playbook.txt",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"Error generating report: {e}")

# ─────────────────────────────────────────────
# MITRE TECHNIQUES PAGE
# ─────────────────────────────────────────────
elif page == "📊 MITRE Techniques":
    st.title("📊 MITRE ATT&CK Techniques")

    mitre_data = load_mitre_data()
    if mitre_data:
        techniques = [
            item for item in mitre_data.get('objects', [])
            if item.get('type') == 'attack-pattern'
        ]

        if techniques:
            st.info(f"Total Techniques Loaded: {len(techniques)}")
            search_query = st.text_input("🔍 Search Techniques (optional)", "")

            for t in techniques:
                name = t.get('name', 'Unknown')
                desc = t.get('description', 'No description available.')
                ext_refs = t.get('external_references', [])
                tech_id = next(
                    (r.get('external_id', 'N/A') for r in ext_refs if 'external_id' in r),
                    'N/A'
                )

                if search_query.lower() in name.lower() or search_query.lower() in desc.lower() or not search_query:
                    with st.expander(f"**{tech_id} → {name}**", expanded=False):
                        st.markdown(f"**ID:** {tech_id}")
                        st.markdown(f"**Name:** {name}")
                        st.markdown(f"**Description:** {desc}")
        else:
            st.warning("No attack-pattern objects found in the JSON.")
    else:
        st.error("⚠️ MITRE ATT&CK JSON could not be loaded. Please upload 'mitre_attack.json'.")

# ─────────────────────────────────────────────
# OSINT GENERATOR PAGE
# ─────────────────────────────────────────────
elif page == "🔍 OSINT Generator":
    st.title("🔍 AI Red Team Assistant – Phase 2: OSINT Query Generator")

    target = st.session_state.get("target", "")
    if not target:
        target = st.text_area(
            "🎯 Describe Your Target",
            placeholder="e.g. 'TechCorp Inc, domain: techcorp.com, industry: fintech, headquartered in New York'",
            height=120
        )

    st.markdown("#### 🔧 Query Options")
    include_google   = st.checkbox("Google Dorks", value=True)
    include_shodan   = st.checkbox("Shodan Queries", value=True)
    include_linkedin = st.checkbox("LinkedIn Boolean", value=True)
    include_harvester = st.checkbox("theHarvester Commands", value=True)
    num_queries = st.slider("Queries per category", 3, 8, 5)

    generate_btn = st.button("🚀 Generate OSINT Queries")

    if generate_btn:
        if not api_key:
            st.error("⚠️ No API key found. Please set GROQ_API_KEY or enter manually in sidebar.")
        elif not target.strip():
            st.warning("⚠️ Please describe your target first.")
        else:
            categories = []
            if include_google:    categories.append(f"{num_queries} Google Dork queries")
            if include_shodan:    categories.append(f"{num_queries} Shodan search queries")
            if include_linkedin:  categories.append(f"{num_queries} LinkedIn Boolean search strings")
            if include_harvester: categories.append(f"{num_queries} theHarvester CLI commands")

            prompt = f"""
You are a professional OSINT researcher and ethical penetration tester.
Target description: "{target}"

Generate the following for this target (for ethical, authorized testing only):
{chr(10).join(f"- {c}" for c in categories)}

Format your response with clear section headers like:
## Google Dorks
## Shodan Queries
## LinkedIn Boolean Searches
## theHarvester Commands

For each query, put it inside a code block so it's easy to copy.
Add a one-line comment above each query explaining what it finds.
Be specific to the target described. Do NOT use generic placeholders.
"""
            with st.spinner("🤖 Generating OSINT queries with Groq AI..."):
                try:
                    client = Groq(api_key=api_key)
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=2048,
                        temperature=0.4
                    )
                    result = response.choices[0].message.content

                    st.success("✅ Queries generated successfully!")
                    st.markdown("---")
                    st.markdown("## 📋 Generated OSINT Queries")

                    sections = result.split("##")
                    for section in sections:
                        if section.strip():
                            lines = section.strip().split("\n")
                            title = lines[0].strip()
                            body = "\n".join(lines[1:]).strip()
                            icon_map = {
                                "Google": "🔎", "Shodan": "🌐",
                                "LinkedIn": "👥", "Harvester": "🧰"
                            }
                            icon = next((v for k, v in icon_map.items() if k.lower() in title.lower()), "📌")
                            with st.expander(f"{icon} {title}", expanded=True):
                                st.markdown(body)

                    st.markdown("---")
                    st.download_button(
                        label="📥 Download All Queries as .txt",
                        data=result,
                        file_name="osint_queries.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center; color:gray; font-size:0.85em;">'
    '🛡️ AI Red Team Assistant · Built for ethical hacking & cybersecurity education only'
    '</div>',
    unsafe_allow_html=True
)