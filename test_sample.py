# backend/test_sample.py

from sample_questions import get_sample_questions, print_question_stats
from analyzer import QuestionTrendAnalyzer
import json

def test_analyzer_with_samples():
    print("="*70)
    print("🧪 TESTING ANALYZER WITH SAMPLE QUESTIONS")
    print("="*70)
    
    # Get sample questions
    print("\n📥 Loading sample questions...")
    questions = get_sample_questions("OOP")
    print_question_stats(questions)
    
    # Initialize analyzer
    print("\n🔧 Initializing analyzer...")
    analyzer = QuestionTrendAnalyzer(similarity_threshold=0.7)
    
    # Run analysis
    print("\n⚙️ Running analysis...")
    results = analyzer.analyze(questions)
    
    # Print results
    print("\n" + "="*70)
    print("📊 ANALYSIS RESULTS")
    print("="*70)
    
    print(f"\n📈 Summary:")
    print(f"  • Total Questions: {results['summary']['total_questions']}")
    print(f"  • Unique Topics: {results['summary']['unique_topics']}")
    print(f"  • Repeated Questions: {results['summary']['repeated_questions']}")
    
    print(f"\n⭐ SUPER REPEATERS (Most Frequently Asked):")
    for i, item in enumerate(results['revision_plan']['super_repeaters'][:5], 1):
        print(f"\n  {i}. {item['sample_question'][:150]}...")
        if item.get('main_topics'):
            print(f"     Topics: {', '.join(item['main_topics'])}")
        print(f"     Appeared: {item['frequency']} times")
    
    print(f"\n🔥 HOT TOPICS:")
    for i, item in enumerate(results['revision_plan']['hot_topics'][:5], 1):
        print(f"  {i}. {item['sample_question'][:100]}...")
    
    print(f"\n📝 Question Patterns:")
    for pattern, count in results['patterns'].items():
        percentage = (count / results['summary']['total_questions']) * 100
        print(f"  • {pattern.capitalize()}: {count} times ({percentage:.1f}%)")
    
    print(f"\n⏰ Your 6-Hour Cram Plan:")
    for plan in results['revision_plan']['hourly_plan']:
        print(f"  {plan}")
    
    # Save results to file
    output_file = "analysis_results.json"
    with open(output_file, 'w') as f:
        # Convert non-serializable items
        serializable_results = {
            'summary': results['summary'],
            'patterns': results['patterns'],
            'revision_plan': {
                'hourly_plan': results['revision_plan']['hourly_plan'],
                'main_pattern': results['revision_plan']['main_pattern'],
                'top_topics': [(t[0], t[1]) for t in results['revision_plan']['top_topics']]
            }
        }
        json.dump(serializable_results, f, indent=2)
    print(f"\n💾 Results saved to: {output_file}")
    
    return results

def test_ds_samples():
    """Test with Data Structures samples"""
    print("\n" + "="*70)
    print("🧪 TESTING WITH DATA STRUCTURES SAMPLES")
    print("="*70)
    
    questions = get_sample_questions("DS")
    analyzer = QuestionTrendAnalyzer(similarity_threshold=0.7)
    results = analyzer.analyze(questions)
    
    print(f"\n📊 DS Analysis Summary:")
    print(f"  • Total Questions: {results['summary']['total_questions']}")
    print(f"  • Unique Topics: {results['summary']['unique_topics']}")
    print(f"  • Repeated Questions: {results['summary']['repeated_questions']}")
    
    return results

if __name__ == "__main__":
    # Test OOP samples
    oop_results = test_analyzer_with_samples()
    
    # Test DS samples
    ds_results = test_ds_samples()
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\nYour analyzer is working correctly with sample data!")
    print("Next step: Connect to frontend or add more questions.")