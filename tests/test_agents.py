import asyncio
from config import Config
from agents.orchestrator import RarePathOrchestrator
from tests.test_agents import AgentTester

async def interactive_mode():
    """Interactive mode for patient input"""
    
    if not Config.GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY not found")
        return
    
    orchestrator = RarePathOrchestrator(Config.GEMINI_API_KEY)
    
    print("🏥 RarePath AI - Rare Disease Diagnostic Assistant")
    print("=" * 60)
    print("\nWelcome! I'm here to help you navigate your diagnostic journey.")
    print("Please describe your symptoms in detail.\n")
    
    # Get patient input
    print("Enter your symptoms (press Enter twice when done):")
    lines = []
    while True:
        line = input()
        if line == "" and lines:
            break
        lines.append(line)
    
    patient_input = "\n".join(lines)
    
    if not patient_input.strip():
        print("No input provided. Exiting.")
        return
    
    # Get location
    location = input("\nWhat's your location (city, state, or country)? ")
    if not location:
        location = "United States"
    
    print("\n" + "=" * 60)
    
    # Run diagnostic journey
    report = await orchestrator.run_diagnostic_journey(
        patient_input,
        patient_location=location
    )
    
    # Display comprehensive report
    display_report(report)

def display_report(report: Dict):
    """Display formatted diagnostic report"""
    
    print("\n" + "=" * 80)
    print("📊 YOUR COMPREHENSIVE DIAGNOSTIC REPORT")
    print("=" * 80)
    
    # Executive Summary
    print("\n📝 EXECUTIVE SUMMARY")
    print("-" * 80)
    print(report.get('executive_summary', 'No summary available'))
    
    # Potential Diagnoses
    print("\n\n🔍 POTENTIAL RARE DISEASE DIAGNOSES")
    print("-" * 80)
    diagnoses = report.get('potential_diagnoses', [])
    
    if diagnoses:
        for i, diagnosis in enumerate(diagnoses[:5], 1):
            if isinstance(diagnosis, dict):
                name = diagnosis.get('name', 'Unknown Condition')
                confidence = diagnosis.get('confidence', 0)
                print(f"\n{i}. {name}")
                print(f"   Confidence: {'High' if confidence > 0.7 else 'Medium' if confidence > 0.4 else 'Low'}")
                
                if 'matching_symptoms' in diagnosis:
                    print(f"   Matching Symptoms: {', '.join(diagnosis['matching_symptoms'])}")
                
                if 'diagnostic_tests' in diagnosis:
                    print(f"   Recommended Tests: {', '.join(diagnosis['diagnostic_tests'])}")
    else:
        print("No specific conditions identified. Please consult with your doctor.")
    
    # Specialist Recommendations
    print("\n\n👨‍⚕️ SPECIALIST RECOMMENDATIONS")
    print("-" * 80)
    specialists = report.get('specialist_recommendations', [])
    
    if specialists:
        for spec in specialists[:5]:
            condition = spec.get('condition', '')
            print(f"\nFor {condition}:")
            print(spec.get('recommendations', 'See specialist'))
    else:
        print("Consult with your primary care physician for specialist referrals.")
    
    # Clinical Trials
    print("\n\n🔬 RELEVANT CLINICAL TRIALS")
    print("-" * 80)
    trials = report.get('clinical_trials', [])
    
    if trials:
        for i, trial in enumerate(trials[:3], 1):
            print(f"\n{i}. {trial.get('title', 'Unknown Trial')}")
            print(f"   Status: {trial.get('status', 'Unknown')}")
            print(f"   NCT ID: {trial.get('nct_id', 'N/A')}")
            print(f"   URL: {trial.get('url', 'N/A')}")
            locations = trial.get('locations', [])
            if locations:
                print(f"   Locations: {', '.join(locations[:3])}")
    else:
        print("No active clinical trials found at this time.")
    
    # Community Resources
    print("\n\n🤝 PATIENT COMMUNITY RESOURCES")
    print("-" * 80)
    communities = report.get('community_resources', [])
    
    if communities:
        for comm in communities[:3]:
            condition = comm.get('condition', '')
            print(f"\nFor {condition}:")
            print(comm.get('resources', 'Check patient advocacy websites'))
    else:
        print("Search for patient advocacy groups related to your conditions.")
    
    # Next Steps
    print("\n\n📋 RECOMMENDED NEXT STEPS")
    print("-" * 80)
    for i, step in enumerate(report.get('next_steps', []), 1):
        print(f"{i}. {step}")
    
    # Questions for Doctor
    print("\n\n❓ QUESTIONS TO ASK YOUR DOCTOR")
    print("-" * 80)
    questions = report.get('questions_for_doctor', [])
    for i, question in enumerate(questions, 1):
        print(f"{i}. {question}")
    
    # Disclaimer
    print("\n\n⚠️  IMPORTANT DISCLAIMER")
    print("-" * 80)
    print(report.get('disclaimer', ''))
    
    # Metrics
    print("\n\n📈 EXECUTION METRICS")
    print("-" * 80)
    metrics = report.get('execution_metrics', {})
    print(f"Total Processing Time: {metrics.get('total_time_seconds', 0):.2f} seconds")
    print(f"Agents Used: {metrics.get('agents_used', 0)}")
    
    print("\n" + "=" * 80)
    print("Report Complete. Save this information to share with your healthcare providers.")
    print("=" * 80)

async def test_mode():
    """Run automated tests"""
    print("\n🧪 Running RarePath AI Test Suite...\n")
    
    if not Config.GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY not found")
        return
    
    tester = AgentTester(Config.GEMINI_API_KEY)
    await tester.run_all_tests()

async def main():
    """Main entry point with mode selection"""
    
    print("\n🏥 RarePath AI - Rare Disease Diagnostic Assistant")
    print("=" * 60)
    print("\nSelect Mode:")
    print("1. Interactive Mode (Enter your symptoms)")
    print("2. Test Mode (Run evaluation tests)")
    print("3. Demo Mode (Use example case)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        await interactive_mode()
    elif choice == "2":
        await test_mode()
    elif choice == "3":
        await demo_mode()
    else:
        print("Invalid choice. Exiting.")

async def demo_mode():
    """Demo mode with example case"""
    
    if not Config.GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY not found")
        return
    
    orchestrator = RarePathOrchestrator(Config.GEMINI_API_KEY)
    
    # Example case
    demo_input = """
    I've been experiencing chronic joint pain and hypermobility for the past 3 years.
    My joints frequently dislocate, especially my shoulders and knees. I also have
    extremely stretchy skin and bruise very easily. I'm constantly fatigued and have
    frequent headaches. My mother had similar symptoms. Multiple doctors have told me
    it's just anxiety or fibromyalgia, but I know something else is wrong.
    """
    
    print("🏥 RarePath AI - Demo Mode")
    print("=" * 60)
    print(f"\nDemo Patient Case:\n{demo_input.strip()}")
    print("\n" + "=" * 60)
    
    # Run diagnostic journey
    report = await orchestrator.run_diagnostic_journey(demo_input)
    
    # Display report
    display_report(report)

if __name__ == "__main__":
    asyncio.run(main())
