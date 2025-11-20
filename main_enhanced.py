import asyncio
from config import Config
from agents.orchestrator import RarePathOrchestrator

async def main():
    """Main entry point for RarePath AI"""
    
    # Check for API key
    if not Config.GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY not found in environment variables")
        print("Please create a .env file with your API key")
        return
    
    # Initialize orchestrator
    orchestrator = RarePathOrchestrator(Config.GEMINI_API_KEY)
    
    print("🏥 RarePath AI - Rare Disease Diagnostic Assistant")
    print("=" * 60)
    print("\n📝 Please describe your symptoms in detail.")
    print("   Include: when they started, severity, frequency, family history, etc.")
    print("   (Press Enter twice when finished)\n")
    
    # Collect multi-line input from user
    lines = []
    print("Enter your symptoms:")
    while True:
        line = input()
        if line == "":
            if lines:  # If we have at least one line and user presses enter again
                break
        lines.append(line)
    
    patient_input = "\n".join(lines).strip()
    
    # Validate input
    if not patient_input or len(patient_input) < 10:
        print("\n❌ Please provide a detailed description of your symptoms.")
        return
    
    print("\n" + "=" * 60)
    print(f"📋 Analyzing your symptoms...")
    print("=" * 60)
    
    # Run diagnostic journey
    result = await orchestrator.run_diagnostic_journey(patient_input)
    
    # Display results
    print("\n" + "=" * 60)
    print("📊 DIAGNOSTIC REPORT")
    print("=" * 60)
    
    print("\n🔍 POTENTIAL CONDITIONS:")
    for i, condition in enumerate(result.get('potential_conditions', [])[:5], 1):
        print(f"\n{i}. {condition.get('name', 'Unknown')}")
        print(f"   Confidence: {condition.get('confidence', 0):.2f}")
        print(f"   Matching Symptoms: {condition.get('matching_symptoms', [])}")
    
    print("\n🔬 RELEVANT CLINICAL TRIALS:")
    for i, trial in enumerate(result.get('clinical_trials', [])[:3], 1):
        print(f"\n{i}. {trial.get('title', 'Unknown')}")
        print(f"   Status: {trial.get('status', 'Unknown')}")
        print(f"   URL: {trial.get('url', '')}")
    
    print("\n📋 NEXT STEPS:")
    for step in result.get('next_steps', []):
        print(f"  • {step}")
    
    print(f"\n⚠️  DISCLAIMER: {result.get('disclaimer', '')}")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
