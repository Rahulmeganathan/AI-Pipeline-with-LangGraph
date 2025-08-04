#!/usr/bin/env python3
"""Simple test of the evaluator."""

from src.evaluation.evaluator import ResponseEvaluator

def test_evaluator():
    evaluator = ResponseEvaluator()
    
    result = evaluator.evaluate_response(
        query="What programming languages does Rahul know?",
        response="Rahul is proficient in Python, JavaScript, and C++.",
        context={"source": "resume"}
    )
    
    print("Evaluation result:")
    print(f"Success: {result.get('success')}")
    print(f"Overall score: {result.get('overall_score', 0)}")
    
    if not result.get('success'):
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    test_evaluator()
