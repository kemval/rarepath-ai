"""
RarePath AI - Streamlit Web Interface
A user-friendly web interface for the rare disease diagnostic assistant
"""

import streamlit as st
import asyncio
from config import Config
from agents.orchestrator import RarePathOrchestrator
import time

# Page configuration
st.set_page_config(
    page_title="RarePath AI - Rare Disease Diagnostic Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-size: 1.1rem;
        padding: 0.75rem;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #1557a0;
    }
    .symptom-box {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .result-card {
        background-color: #f9f9f9;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'diagnosis_complete' not in st.session_state:
    st.session_state.diagnosis_complete = False
if 'results' not in st.session_state:
    st.session_state.results = None

def run_diagnosis(patient_input: str, location: str):
    """Run the diagnostic journey asynchronously"""
    async def async_diagnosis():
        orchestrator = RarePathOrchestrator(Config.GEMINI_API_KEY)
        result = await orchestrator.run_diagnostic_journey(
            patient_input=patient_input,
            patient_location=location
        )
        return result
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(async_diagnosis())
    loop.close()
    return result

# Main UI
st.markdown('<h1 class="main-header">RarePath AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Rare Disease Diagnostic Assistant powered by AI Agents</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("About RarePath AI")
    st.markdown("""
    RarePath AI uses advanced multi-agent AI systems to:
    
    - 📋 **Analyze your symptoms** comprehensively
    - 🔬 **Search medical literature** for rare diseases
    - 👨‍⚕️ **Find specialist doctors** in your area
    - 🧪 **Match clinical trials** you may qualify for
    - 🤝 **Connect you with** patient communities
    
    **Built for the Google - Kaggle Agents Intensive Capstone**
    """)
    
    st.divider()
    
    st.header("⚙️ Settings")
    location = st.text_input(
        "Your Location",
        value="United States",
        help="Enter your city/state/country to find local specialists"
    )
    
    st.divider()
    
    st.markdown("""
    ⚠️ **Medical Disclaimer**
    
    This is NOT a medical diagnosis tool. Always consult qualified healthcare professionals.
    """)

# Check API key
if not Config.GEMINI_API_KEY:
    st.error("❌ GEMINI_API_KEY not found! Please set it in your .env file")
    st.stop()

# Main content area
if not st.session_state.diagnosis_complete:
    st.markdown("### Describe Your Symptoms")
    
    st.markdown("""
    Please provide detailed information about your symptoms. Include:
    - When did symptoms start?
    - How severe are they?
    - How often do they occur?
    - Any family history of similar conditions?
    - Previous diagnoses or test results?
    """)
    
    patient_input = st.text_area(
        "Enter your symptoms here:",
        height=200,
        placeholder="""Example:
I've been experiencing chronic joint pain and hypermobility for the past 3 years.
My joints frequently dislocate, especially my shoulders and knees. I also have
extremely stretchy skin and bruise very easily. I'm constantly fatigued and have
frequent headaches. My mother had similar symptoms."""
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start Diagnostic Analysis", type="primary"):
            if not patient_input or len(patient_input) < 20:
                st.error("Please provide a more detailed description of your symptoms (at least 20 characters)")
            else:
                with st.spinner("🔬 Starting analysis..."):
                    st.session_state.patient_input = patient_input
                    st.session_state.diagnosis_complete = True
                    time.sleep(0.5)  # Brief pause to show the loading message
                st.rerun()

else:
    # Show the patient input
    st.markdown("### Your Symptoms")
    patient_input = st.text_area(
        "Symptoms being analyzed:",
        value=st.session_state.get('patient_input', ''),
        height=150,
        disabled=True
    )
    
    if st.session_state.results is None:
        # Run diagnosis
        with st.spinner("🔬 Analyzing your symptoms... This may take 30-60 seconds..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Show progress updates
            status_text.text("📋 Collecting symptom information...")
            progress_bar.progress(20)
            time.sleep(0.5)
            
            status_text.text("🔍 Searching medical literature...")
            progress_bar.progress(40)
            
            # Run actual diagnosis
            try:
                results = run_diagnosis(patient_input, location)
                st.session_state.results = results
                
                status_text.text("👨‍⚕️ Finding specialists...")
                progress_bar.progress(70)
                time.sleep(0.3)
                
                status_text.text("📊 Compiling report...")
                progress_bar.progress(100)
                time.sleep(0.3)
                
                status_text.empty()
                progress_bar.empty()
                st.success("✅ Analysis complete!")
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.info("💡 Try again in a few moments if you hit API rate limits")
                if st.button("🔄 Reset"):
                    st.session_state.diagnosis_complete = False
                    st.session_state.results = None
                    st.rerun()
                st.stop()
    
    # Display results
    if st.session_state.results:
        results = st.session_state.results
        
        st.markdown("---")
        st.markdown("## Diagnostic Report")
        
        # Executive Summary
        if results.get('executive_summary'):
            st.markdown("### Executive Summary")
            st.info(results['executive_summary'])
        
        # Potential Conditions
        st.markdown("### Potential Conditions")
        conditions = results.get('potential_diagnoses', results.get('potential_conditions', []))
        
        # Check if conditions were fetched but empty due to API error
        if results.get('_warnings', {}).get('conditions_failed'):
            st.warning("⚠️ Condition analysis incomplete due to API rate limits. Please wait 60 seconds and try again.")
        
        if conditions and len(conditions) > 0:
            for i, condition in enumerate(conditions[:5], 1):
                with st.expander(f"{i}. {condition.get('name', 'Condition ' + str(i))}", expanded=(i==1)):
                    if condition.get('confidence'):
                        # Handle both string and numeric confidence values
                        confidence = condition.get('confidence', 'N/A')
                        if isinstance(confidence, (int, float)):
                            st.metric("Confidence", f"{confidence:.0%}")
                        else:
                            st.metric("Confidence", str(confidence))
                    if condition.get('matching_symptoms'):
                        st.markdown("**Matching Symptoms:**")
                        for symptom in condition['matching_symptoms']:
                            st.markdown(f"- {symptom}")
                    if condition.get('diagnostic_tests'):
                        st.markdown("**Recommended Tests:**")
                        for test in condition['diagnostic_tests']:
                            st.markdown(f"- {test}")
        else:
            st.info("No specific conditions identified. Please consult with a healthcare provider for further evaluation.")
        
        # Clinical Trials
        st.markdown("### Relevant Clinical Trials")
        trials = results.get('clinical_trials', [])
        
        # Check if trials search failed
        if results.get('_warnings', {}).get('trials_failed'):
            st.warning("⚠️ Clinical trials search unavailable due to API limits. Try again later.")
        
        if trials and len(trials) > 0:
            for i, trial in enumerate(trials[:5], 1):
                with st.expander(f"Trial {i}: {trial.get('title', 'Clinical Trial')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        if trial.get('status'):
                            st.markdown(f"**Status:** {trial['status']}")
                        if trial.get('nct_id'):
                            st.markdown(f"**ID:** {trial['nct_id']}")
                    with col2:
                        if trial.get('url'):
                            st.markdown(f"[View on ClinicalTrials.gov]({trial['url']})")
                    if trial.get('locations'):
                        st.markdown("**Locations:**")
                        for loc in trial['locations'][:3]:
                            st.markdown(f"- {loc}")
        else:
            st.info("No clinical trials found matching your symptoms.")
        
        # Specialist Recommendations
        st.markdown("### Specialist Recommendations")
        specialists = results.get('specialist_recommendations', [])
        
        # Check if specialist search failed
        if results.get('_warnings', {}).get('specialists_failed'):
            st.warning("⚠️ Specialist search temporarily unavailable. Please try again in a moment.")
        
        if specialists and len(specialists) > 0:
            for spec in specialists[:3]:
                st.markdown(f"**{spec.get('condition', 'Condition')}**")
                st.markdown(spec.get('recommendations', 'No specific recommendations available.'))
                st.markdown("---")
        else:
            st.info("General recommendation: Consult with your primary care physician for specialist referrals.")
        
        # Community Resources
        st.markdown("### Community Resources")
        
        # Check if community search failed
        if results.get('_warnings', {}).get('communities_failed'):
            st.warning("⚠️ Community resources unavailable due to API rate limits.")
        elif results.get('community_resources'):
            communities = results['community_resources']
            for community in communities[:3]:
                with st.expander(f"Resources for {community.get('condition', 'Condition')}"):
                    st.markdown(community.get('resources', 'No resources available.'))
        else:
            st.info("No community resources found for the identified conditions.")
        
        # Next Steps
        st.markdown("### Recommended Next Steps")
        next_steps = results.get('next_steps', [])
        
        if next_steps:
            for step in next_steps:
                # Check if step already starts with a number (e.g., "1. ", "2. ")
                step_stripped = step.strip()
                if step_stripped and step_stripped[0].isdigit() and '. ' in step_stripped[:4]:
                    # Already has number identifier, don't add bullet point
                    st.markdown(step)
                else:
                    # Add bullet point for non-numbered steps
                    st.markdown(f"- {step}")
        else:
            st.markdown("""
            - Schedule appointment with primary care physician to discuss findings
            - Request referrals to recommended specialists
            - Keep detailed symptom diary
            - Gather all previous medical records
            """)
        
        # Questions for Doctor
        if results.get('questions_for_doctor'):
            st.markdown("### Questions to Ask Your Doctor")
            for question in results['questions_for_doctor']:
                st.markdown(f"- {question}")
        
        # Disclaimer
        st.markdown("---")
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.warning(results.get('disclaimer', 
            "⚠️ IMPORTANT: This report is generated by an AI system for informational purposes only. "
            "It is NOT a medical diagnosis and should NOT replace professional medical advice. "
            "Always consult with qualified healthcare providers before making any medical decisions."))
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Reset button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Start New Analysis"):
                st.session_state.diagnosis_complete = False
                st.session_state.results = None
                st.session_state.patient_input = ""
                st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>RarePath AI - Empowering patients with rare disease information</p>
    <p style='font-size: 0.9rem;'>Built with Multi-Agent AI Systems | Google - Kaggle Agents Intensive Capstone Project</p>
</div>
""", unsafe_allow_html=True)
