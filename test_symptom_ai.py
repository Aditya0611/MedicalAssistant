import symptom_analyzer

print("=== AI Symptom Analyzer Test ===\n")

test_cases = [
    "My head feels like it's going to explode",
    "I have a pounding sensation in my skull",
    "chest hurts when I breathe",
    "I can't stop coughing",
    "my skin is itchy and red",
    "I don't feel well",
    "headache"  # Simple keyword test
]

for symptom in test_cases:
    print(f"\nInput: '{symptom}'")
    result = symptom_analyzer.analyze_symptom(symptom)
    print(f"→ Specialty: {result['specialty']}")
    print(f"→ Confidence: {result['confidence']}")
    print(f"→ Reasoning: {result['reasoning']}")
    print(f"→ AI Success: {result['success']}")
    print("-" * 50)
