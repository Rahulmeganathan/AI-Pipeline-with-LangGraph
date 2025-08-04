from typing import Dict, Any, List
from langsmith import Client
from langsmith.evaluation import StringEvaluator
from src.config import get_settings


class ResponseEvaluator:
    """LangSmith-based response evaluator."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = Client(
            api_key=self.settings.langchain_api_key
        )
        
        # Custom evaluators with grading functions
        self.relevance_evaluator = StringEvaluator(
            criteria="relevance",
            criteria_description="How relevant is the response to the user's query?",
            grading_function=self._grade_relevance
        )
        
        self.accuracy_evaluator = StringEvaluator(
            criteria="accuracy",
            criteria_description="How accurate is the information provided in the response?",
            grading_function=self._grade_accuracy
        )
        
        self.helpfulness_evaluator = StringEvaluator(
            criteria="helpfulness",
            criteria_description="How helpful and informative is the response?",
            grading_function=self._grade_helpfulness
        )
    
    def _grade_relevance(self, prediction: str, input: str) -> Dict[str, Any]:
        """Grade the relevance of a response to the input query."""
        # Simple relevance scoring based on keyword overlap
        query_words = set(input.lower().split())
        response_words = set(prediction.lower().split())
        
        if not query_words:
            return {"score": 0.5, "reasoning": "No query provided"}
        
        # Calculate word overlap
        overlap = len(query_words.intersection(response_words))
        total_query_words = len(query_words)
        
        if total_query_words == 0:
            score = 0.5
        else:
            score = min(1.0, overlap / total_query_words)
        
        return {
            "score": score,
            "reasoning": f"Relevance score based on word overlap: {overlap}/{total_query_words} words matched"
        }
    
    def _grade_accuracy(self, prediction: str, input: str) -> Dict[str, Any]:
        """Grade the accuracy of a response."""
        # Simple accuracy scoring - in a real system, this would be more sophisticated
        # For now, we'll use a basic heuristic based on response length and content
        
        if not prediction.strip():
            return {"score": 0.0, "reasoning": "Empty response"}
        
        # Basic accuracy scoring
        response_length = len(prediction.split())
        
        if response_length < 5:
            score = 0.3
            reasoning = "Very short response, may lack detail"
        elif response_length < 20:
            score = 0.7
            reasoning = "Moderate length response"
        else:
            score = 0.9
            reasoning = "Detailed response with substantial content"
        
        return {"score": score, "reasoning": reasoning}
    
    def _grade_helpfulness(self, prediction: str, input: str) -> Dict[str, Any]:
        """Grade the helpfulness of a response."""
        if not prediction.strip():
            return {"score": 0.0, "reasoning": "Empty response is not helpful"}
        
        # Simple helpfulness scoring based on response characteristics
        response_lower = prediction.lower()
        
        # Check for helpful indicators
        helpful_indicators = [
            "here", "this", "information", "details", "explanation",
            "because", "therefore", "however", "additionally", "furthermore"
        ]
        
        helpful_count = sum(1 for indicator in helpful_indicators if indicator in response_lower)
        
        # Base score on helpful indicators and response length
        base_score = min(0.8, helpful_count * 0.1 + 0.3)
        
        # Adjust based on response length
        word_count = len(prediction.split())
        if word_count > 50:
            base_score = min(1.0, base_score + 0.2)
        elif word_count < 10:
            base_score = max(0.2, base_score - 0.2)
        
        return {
            "score": base_score,
            "reasoning": f"Helpfulness based on content indicators and length ({word_count} words)"
        }
    
    def evaluate_response(self, query: str, response: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Evaluate a response using custom grading functions."""
        try:
            evaluation_results = {}
            
            # Evaluate relevance using our custom grading function
            relevance_result = self._grade_relevance(response, query)
            evaluation_results["relevance"] = relevance_result
            
            # Evaluate accuracy using our custom grading function
            accuracy_result = self._grade_accuracy(response, query)
            evaluation_results["accuracy"] = accuracy_result
            
            # Evaluate helpfulness using our custom grading function
            helpfulness_result = self._grade_helpfulness(response, query)
            evaluation_results["helpfulness"] = helpfulness_result
            
            # Calculate overall score
            scores = [
                relevance_result.get("score", 0),
                accuracy_result.get("score", 0),
                helpfulness_result.get("score", 0)
            ]
            overall_score = sum(scores) / len(scores) if scores else 0
            
            return {
                "success": True,
                "evaluations": evaluation_results,
                "overall_score": overall_score,
                "query": query,
                "response": response,
                "context": context
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "response": response
            }
    
    def evaluate_batch(self, queries_responses: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Evaluate a batch of query-response pairs."""
        results = []
        
        for item in queries_responses:
            query = item.get("query", "")
            response = item.get("response", "")
            context = item.get("context", {})
            
            evaluation = self.evaluate_response(query, response, context)
            results.append(evaluation)
        
        return results
    
    def get_evaluation_summary(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of evaluation results."""
        if not evaluations:
            return {
                "total_evaluations": 0,
                "average_scores": {},
                "success_rate": 0
            }
        
        successful_evaluations = [e for e in evaluations if e.get("success", False)]
        
        if not successful_evaluations:
            return {
                "total_evaluations": len(evaluations),
                "successful_evaluations": 0,
                "success_rate": 0,
                "average_scores": {}
            }
        
        # Calculate average scores
        relevance_scores = []
        accuracy_scores = []
        helpfulness_scores = []
        overall_scores = []
        
        for eval_result in successful_evaluations:
            evaluations = eval_result.get("evaluations", {})
            
            if "relevance" in evaluations and "score" in evaluations["relevance"]:
                relevance_scores.append(evaluations["relevance"]["score"])
            
            if "accuracy" in evaluations and "score" in evaluations["accuracy"]:
                accuracy_scores.append(evaluations["accuracy"]["score"])
            
            if "helpfulness" in evaluations and "score" in evaluations["helpfulness"]:
                helpfulness_scores.append(evaluations["helpfulness"]["score"])
            
            overall_score = eval_result.get("overall_score", 0)
            overall_scores.append(overall_score)
        
        return {
            "total_evaluations": len(evaluations),
            "successful_evaluations": len(successful_evaluations),
            "success_rate": len(successful_evaluations) / len(evaluations),
            "average_scores": {
                "relevance": sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0,
                "accuracy": sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0,
                "helpfulness": sum(helpfulness_scores) / len(helpfulness_scores) if helpfulness_scores else 0,
                "overall": sum(overall_scores) / len(overall_scores) if overall_scores else 0
            }
        }
    
    def log_evaluation(self, query: str, response: str, classification: str, 
                      evaluation_results: Dict[str, Any]) -> bool:
        """Log evaluation results to LangSmith."""
        try:
            # Create a run for logging
            run = self.client.create_run(
                name="response_evaluation",
                inputs={"query": query, "classification": classification},
                outputs={"response": response, "evaluation": evaluation_results}
            )
            
            return True
            
        except Exception as e:
            print(f"Error logging evaluation: {str(e)}")
            return False
    
    def get_evaluation_metrics(self) -> Dict[str, Any]:
        """Get evaluation metrics from LangSmith."""
        try:
            # This would typically fetch metrics from LangSmith
            # For now, return basic structure
            return {
                "total_evaluations": 0,
                "average_scores": {
                    "relevance": 0.0,
                    "accuracy": 0.0,
                    "helpfulness": 0.0,
                    "overall": 0.0
                },
                "success_rate": 0.0
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "total_evaluations": 0,
                "average_scores": {},
                "success_rate": 0.0
            } 