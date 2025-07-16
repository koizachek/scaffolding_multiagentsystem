"""
Enhanced I/O Manager

This module provides enhanced input/output handling for the multi-agent scaffolding system
with support for experimental data collection, user interaction analysis, and multiple
interface types while maintaining compatibility with the existing scaffolding workflow.
"""

import json
import logging
import time
import re
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class InputHandler(ABC):
    """Abstract base class for input handlers."""
    
    @abstractmethod
    def get_input(self, prompt: str, **kwargs) -> str:
        """Get input from user."""
        pass
    
    @abstractmethod
    async def get_input_async(self, prompt: str, **kwargs) -> str:
        """Get input from user asynchronously."""
        pass

class OutputHandler(ABC):
    """Abstract base class for output handlers."""
    
    @abstractmethod
    def display_output(self, text: str, **kwargs) -> None:
        """Display output to user."""
        pass
    
    @abstractmethod
    def display_formatted_output(self, content: Dict[str, Any]) -> None:
        """Display formatted output to user."""
        pass

class InteractionAnalyzer:
    """Analyzes user interactions for experimental and scaffolding purposes."""
    
    def __init__(self):
        self.analysis_cache = {}
    
    def analyze_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive analysis of user response for scaffolding and research.
        
        Args:
            response: User response text
            context: Context including scaffolding type, prompt, etc.
            
        Returns:
            Detailed analysis results
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "response_text": response,
            "context": context,
            "metrics": self._calculate_response_metrics(response),
            "linguistic_features": self._analyze_linguistic_features(response),
            "cognitive_indicators": self._analyze_cognitive_indicators(response, context),
            "engagement_level": self._assess_engagement_level(response),
            "scaffolding_needs": self._assess_scaffolding_needs(response, context),
            "learning_indicators": self._identify_learning_indicators(response)
        }
        
        return analysis
    
    def _calculate_response_metrics(self, response: str) -> Dict[str, Any]:
        """Calculate basic response metrics."""
        words = response.split()
        sentences = re.split(r'[.!?]+', response)
        
        return {
            "character_count": len(response),
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "avg_word_length": sum(len(word) for word in words) / max(1, len(words)),
            "question_count": response.count("?"),
            "exclamation_count": response.count("!"),
            "response_time": None  # To be filled by caller if available
        }
    
    def _analyze_linguistic_features(self, response: str) -> Dict[str, Any]:
        """Analyze linguistic features of the response."""
        # Convert to lowercase for analysis
        lower_response = response.lower()
        
        # Uncertainty indicators
        uncertainty_words = ["maybe", "perhaps", "might", "could", "possibly", 
                           "not sure", "don't know", "uncertain", "unclear"]
        uncertainty_count = sum(1 for word in uncertainty_words if word in lower_response)
        
        # Confidence indicators
        confidence_words = ["definitely", "certainly", "sure", "confident", 
                          "clear", "obvious", "understand", "know"]
        confidence_count = sum(1 for word in confidence_words if word in lower_response)
        
        # Metacognitive language
        metacognitive_words = ["think", "believe", "feel", "realize", "understand",
                             "learned", "discovered", "noticed", "remember"]
        metacognitive_count = sum(1 for word in metacognitive_words if word in lower_response)
        
        # Elaboration indicators
        elaboration_words = ["because", "since", "therefore", "however", "although",
                           "for example", "such as", "specifically", "in particular"]
        elaboration_count = sum(1 for phrase in elaboration_words if phrase in lower_response)
        
        return {
            "uncertainty_indicators": uncertainty_count,
            "confidence_indicators": confidence_count,
            "metacognitive_language": metacognitive_count,
            "elaboration_indicators": elaboration_count,
            "sentiment": self._assess_sentiment(response)
        }
    
    def _analyze_cognitive_indicators(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cognitive processing indicators."""
        lower_response = response.lower()
        
        # Deep processing indicators
        deep_processing = ["analyze", "compare", "evaluate", "synthesize", "relate",
                         "connect", "integrate", "apply", "transfer"]
        deep_count = sum(1 for word in deep_processing if word in lower_response)
        
        # Surface processing indicators
        surface_processing = ["memorize", "repeat", "list", "recall", "remember"]
        surface_count = sum(1 for word in surface_processing if word in lower_response)
        
        # Conceptual understanding indicators
        conceptual_words = ["relationship", "connection", "pattern", "principle",
                          "concept", "idea", "theory", "model"]
        conceptual_count = sum(1 for word in conceptual_words if word in lower_response)
        
        return {
            "deep_processing_indicators": deep_count,
            "surface_processing_indicators": surface_count,
            "conceptual_understanding": conceptual_count,
            "cognitive_load": self._assess_cognitive_load(response)
        }
    
    def _assess_engagement_level(self, response: str) -> str:
        """Assess user engagement level based on response characteristics."""
        metrics = self._calculate_response_metrics(response)
        
        # High engagement indicators
        if (metrics["word_count"] > 50 or 
            metrics["question_count"] > 1 or
            "interesting" in response.lower() or
            "excited" in response.lower()):
            return "high"
        
        # Low engagement indicators
        elif (metrics["word_count"] < 10 or
              response.lower().strip() in ["yes", "no", "ok", "sure", "maybe"]):
            return "low"
        
        return "medium"
    
    def _assess_scaffolding_needs(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess what type of scaffolding might be needed based on response."""
        lower_response = response.lower()
        scaffolding_type = context.get("scaffolding_type", "")
        
        needs = {
            "strategic": 0.0,
            "metacognitive": 0.0,
            "procedural": 0.0,
            "conceptual": 0.0
        }
        
        # Strategic scaffolding needs
        if any(word in lower_response for word in ["confused", "lost", "don't know where to start"]):
            needs["strategic"] += 0.3
        if "organize" in lower_response or "structure" in lower_response:
            needs["strategic"] += 0.2
        
        # Metacognitive scaffolding needs
        if any(word in lower_response for word in ["not sure", "uncertain", "don't understand"]):
            needs["metacognitive"] += 0.3
        if "confidence" in lower_response or "feel" in lower_response:
            needs["metacognitive"] += 0.2
        
        # Procedural scaffolding needs
        if any(word in lower_response for word in ["how", "steps", "process", "method"]):
            needs["procedural"] += 0.3
        if "tool" in lower_response or "technique" in lower_response:
            needs["procedural"] += 0.2
        
        # Conceptual scaffolding needs
        if any(word in lower_response for word in ["concept", "relationship", "connection"]):
            needs["conceptual"] += 0.3
        if "why" in lower_response or "what" in lower_response:
            needs["conceptual"] += 0.2
        
        return needs
    
    def _identify_learning_indicators(self, response: str) -> Dict[str, Any]:
        """Identify indicators of learning progress."""
        lower_response = response.lower()
        
        # Learning progress indicators
        progress_indicators = ["learned", "understand", "realize", "see", "get it",
                             "makes sense", "clear", "aha", "insight"]
        progress_count = sum(1 for word in progress_indicators if word in lower_response)
        
        # Confusion indicators
        confusion_indicators = ["confused", "unclear", "don't understand", "lost",
                              "difficult", "hard", "complicated"]
        confusion_count = sum(1 for word in confusion_indicators if word in lower_response)
        
        # Knowledge construction indicators
        construction_indicators = ["connect", "relate", "link", "combine", "integrate",
                                 "build", "develop", "create"]
        construction_count = sum(1 for word in construction_indicators if word in lower_response)
        
        return {
            "progress_indicators": progress_count,
            "confusion_indicators": confusion_count,
            "knowledge_construction": construction_count,
            "learning_state": self._determine_learning_state(progress_count, confusion_count)
        }
    
    def _assess_sentiment(self, response: str) -> str:
        """Simple sentiment analysis."""
        positive_words = ["good", "great", "excellent", "like", "enjoy", "interesting",
                         "helpful", "useful", "clear", "understand"]
        negative_words = ["bad", "difficult", "hard", "confusing", "unclear", "frustrated",
                         "don't like", "boring", "useless"]
        
        lower_response = response.lower()
        positive_count = sum(1 for word in positive_words if word in lower_response)
        negative_count = sum(1 for word in negative_words if word in lower_response)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        return "neutral"
    
    def _assess_cognitive_load(self, response: str) -> str:
        """Assess cognitive load based on response complexity."""
        metrics = self._calculate_response_metrics(response)
        
        # High cognitive load indicators
        if (metrics["word_count"] > 100 or
            metrics["avg_word_length"] > 6 or
            "complex" in response.lower() or
            "overwhelming" in response.lower()):
            return "high"
        
        # Low cognitive load indicators
        elif (metrics["word_count"] < 20 or
              metrics["avg_word_length"] < 4):
            return "low"
        
        return "medium"
    
    def _determine_learning_state(self, progress_count: int, confusion_count: int) -> str:
        """Determine overall learning state."""
        if progress_count > confusion_count and progress_count > 0:
            return "progressing"
        elif confusion_count > progress_count and confusion_count > 0:
            return "struggling"
        elif progress_count == 0 and confusion_count == 0:
            return "neutral"
        return "mixed"

class InputValidator:
    """Validates and sanitizes user input."""
    
    @staticmethod
    def validate_text_input(text: str, max_length: int = 2000, min_length: int = 1) -> Tuple[bool, str]:
        """
        Validate text input.
        
        Args:
            text: Input text to validate
            max_length: Maximum allowed length
            min_length: Minimum required length
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "Input cannot be empty"
        
        if len(text) < min_length:
            return False, f"Input must be at least {min_length} characters"
        
        if len(text) > max_length:
            return False, f"Input must be no more than {max_length} characters"
        
        # Check for potentially harmful content
        harmful_patterns = [
            r'<script.*?>.*?</script>',  # Script tags
            r'javascript:',              # JavaScript URLs
            r'on\w+\s*=',               # Event handlers
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False, "Input contains potentially harmful content"
        
        return True, ""
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Sanitize user input.
        
        Args:
            text: Input text to sanitize
            
        Returns:
            Sanitized text
        """
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Remove potentially harmful HTML/JavaScript
        text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text

class EnhancedCLIInputHandler(InputHandler):
    """Enhanced CLI input handler with validation and timeout support."""
    
    def __init__(self, validator: Optional[InputValidator] = None):
        self.validator = validator or InputValidator()
        self.input_history = []
    
    def get_input(self, prompt: str, **kwargs) -> str:
        """
        Get input from user with validation and error handling.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional options (timeout, max_length, etc.)
            
        Returns:
            Validated user input
        """
        timeout = kwargs.get('timeout', None)
        max_length = kwargs.get('max_length', 2000)
        min_length = kwargs.get('min_length', 1)
        max_attempts = kwargs.get('max_attempts', 3)
        
        for attempt in range(max_attempts):
            try:
                if timeout:
                    # For timeout support, we'd need to use threading or signal
                    # For now, just use regular input
                    user_input = input(prompt)
                else:
                    user_input = input(prompt)
                
                # Sanitize input
                user_input = self.validator.sanitize_input(user_input)
                
                # Validate input
                is_valid, error_message = self.validator.validate_text_input(
                    user_input, max_length, min_length
                )
                
                if is_valid:
                    # Store in history
                    self.input_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "prompt": prompt,
                        "input": user_input,
                        "attempt": attempt + 1
                    })
                    return user_input
                else:
                    print(f"Invalid input: {error_message}")
                    if attempt < max_attempts - 1:
                        print("Please try again.")
            
            except KeyboardInterrupt:
                print("\nInput cancelled by user.")
                return ""
            except Exception as e:
                logger.error(f"Error getting input: {e}")
                if attempt < max_attempts - 1:
                    print("An error occurred. Please try again.")
        
        print("Maximum attempts reached. Using empty input.")
        return ""
    
    async def get_input_async(self, prompt: str, **kwargs) -> str:
        """Asynchronous version of get_input."""
        # For now, just call the synchronous version
        # In a real implementation, this would use asyncio
        return self.get_input(prompt, **kwargs)

class EnhancedCLIOutputHandler(OutputHandler):
    """Enhanced CLI output handler with formatting and logging."""
    
    def __init__(self, enable_colors: bool = True, log_output: bool = True):
        self.enable_colors = enable_colors
        self.log_output = log_output
        self.output_history = []
    
    def display_output(self, text: str, **kwargs) -> None:
        """
        Display output with optional formatting.
        
        Args:
            text: Output text
            **kwargs: Formatting options (color, style, etc.)
        """
        output_type = kwargs.get('output_type', 'normal')
        color = kwargs.get('color', None)
        
        # Format text based on type
        formatted_text = self._format_text(text, output_type, color)
        
        # Display text
        print(formatted_text)
        
        # Log output if enabled
        if self.log_output:
            self.output_history.append({
                "timestamp": datetime.now().isoformat(),
                "text": text,
                "formatted_text": formatted_text,
                "type": output_type
            })
    
    def display_formatted_output(self, content: Dict[str, Any]) -> None:
        """Display formatted content."""
        if content.get("type") == "scaffolding_prompt":
            self._display_scaffolding_prompt(content)
        elif content.get("type") == "analysis_result":
            self._display_analysis_result(content)
        else:
            # Default formatting
            self.display_output(str(content))
    
    def _format_text(self, text: str, output_type: str, color: Optional[str]) -> str:
        """Format text with colors and styles."""
        if not self.enable_colors:
            return text
        
        # ANSI color codes
        colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'reset': '\033[0m'
        }
        
        # Type-based formatting
        if output_type == 'error':
            return f"{colors['red']}{text}{colors['reset']}"
        elif output_type == 'success':
            return f"{colors['green']}{text}{colors['reset']}"
        elif output_type == 'warning':
            return f"{colors['yellow']}{text}{colors['reset']}"
        elif output_type == 'info':
            return f"{colors['blue']}{text}{colors['reset']}"
        elif color and color in colors:
            return f"{colors[color]}{text}{colors['reset']}"
        
        return text
    
    def _display_scaffolding_prompt(self, content: Dict[str, Any]) -> None:
        """Display scaffolding prompt with special formatting."""
        scaffolding_type = content.get("scaffolding_type", "")
        prompt = content.get("prompt", "")
        
        # Get emoji for scaffolding type
        emojis = {
            "strategic": "🧭",
            "metacognitive": "🧠",
            "procedural": "🛠️",
            "conceptual": "💡"
        }
        
        emoji = emojis.get(scaffolding_type, "🤖")
        formatted_prompt = f"\n{emoji} {prompt}\n"
        
        self.display_output(formatted_prompt, output_type='info')
    
    def _display_analysis_result(self, content: Dict[str, Any]) -> None:
        """Display analysis result with structured formatting."""
        analysis = content.get("analysis", {})
        
        print("\n--- Response Analysis ---")
        
        metrics = analysis.get("metrics", {})
        if metrics:
            print(f"Word count: {metrics.get('word_count', 0)}")
            print(f"Engagement level: {analysis.get('engagement_level', 'unknown')}")
        
        learning_indicators = analysis.get("learning_indicators", {})
        if learning_indicators:
            print(f"Learning state: {learning_indicators.get('learning_state', 'unknown')}")
        
        print("------------------------\n")

class ExperimentalIOManager:
    """
    Enhanced I/O Manager for experimental scaffolding research.
    
    This class provides comprehensive input/output handling with experimental
    data collection, user interaction analysis, and support for the iterative
    scaffolding process.
    """
    
    def __init__(self, 
                 input_handler: Optional[InputHandler] = None,
                 output_handler: Optional[OutputHandler] = None,
                 analyzer: Optional[InteractionAnalyzer] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the experimental I/O manager.
        
        Args:
            input_handler: Input handler instance
            output_handler: Output handler instance
            analyzer: Interaction analyzer instance
            config: Configuration options
        """
        self.input_handler = input_handler or EnhancedCLIInputHandler()
        self.output_handler = output_handler or EnhancedCLIOutputHandler()
        self.analyzer = analyzer or InteractionAnalyzer()
        self.config = config or {}
        
        # Experimental data collection
        self.interaction_log = []
        self.session_data = {
            "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": datetime.now().isoformat(),
            "interactions": [],
            "analysis_summary": {}
        }
        
        logger.info("Initialized experimental I/O manager")
    
    def handle_user_input(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Enhanced user input handling with analysis and logging.
        
        Args:
            prompt: Input prompt
            context: Context information for analysis
            
        Returns:
            User input with analysis
        """
        start_time = time.time()
        
        # Get user input
        user_input = self.input_handler.get_input(
            prompt,
            max_length=self.config.get("max_input_length", 2000),
            timeout=self.config.get("input_timeout", None)
        )
        
        response_time = time.time() - start_time
        
        # Analyze response
        analysis_context = context or {}
        analysis_context["response_time"] = response_time
        
        analysis = self.analyzer.analyze_response(user_input, analysis_context)
        
        # Log interaction
        interaction_record = {
            "timestamp": datetime.now().isoformat(),
            "type": "user_input",
            "prompt": prompt,
            "response": user_input,
            "response_time": response_time,
            "context": context,
            "analysis": analysis
        }
        
        self.interaction_log.append(interaction_record)
        self.session_data["interactions"].append(interaction_record)
        
        # Log for research purposes
        logger.info(f"User input collected: {len(user_input)} characters, "
                   f"engagement: {analysis.get('engagement_level', 'unknown')}")
        
        return user_input
    
    def handle_system_output(self, content: Any, output_type: str = "text", 
                           context: Optional[Dict[str, Any]] = None) -> None:
        """
        Enhanced system output handling with logging.
        
        Args:
            content: Content to output
            output_type: Type of output (text, scaffolding_prompt, etc.)
            context: Context information
        """
        # Format content based on type
        if isinstance(content, dict):
            self.output_handler.display_formatted_output(content)
            display_text = str(content)
        else:
            self.output_handler.display_output(str(content), output_type=output_type)
            display_text = str(content)
        
        # Log output
        output_record = {
            "timestamp": datetime.now().isoformat(),
            "type": "system_output",
            "content": display_text,
            "output_type": output_type,
            "context": context
        }
        
        self.interaction_log.append(output_record)
        self.session_data["interactions"].append(output_record)
        
        logger.info(f"System output displayed: {output_type}")
    
    def get_interaction_analysis(self) -> Dict[str, Any]:
        """
        Get comprehensive analysis of all interactions in the session.
        
        Returns:
            Analysis summary
        """
        user_inputs = [i for i in self.interaction_log if i["type"] == "user_input"]
        
        if not user_inputs:
            return {"message": "No user interactions recorded"}
        
        # Aggregate metrics
        total_words = sum(i["analysis"]["metrics"]["word_count"] for i in user_inputs)
        avg_response_time = sum(i["response_time"] for i in user_inputs) / len(user_inputs)
        
        engagement_levels = [i["analysis"]["engagement_level"] for i in user_inputs]
        learning_states = [i["analysis"]["learning_indicators"]["learning_state"] 
                          for i in user_inputs]
        
        # Calculate scaffolding effectiveness
        scaffolding_needs = {}
        for interaction in user_inputs:
            needs = interaction["analysis"]["scaffolding_needs"]
            for need_type, score in needs.items():
                if need_type not in scaffolding_needs:
                    scaffolding_needs[need_type] = []
                scaffolding_needs[need_type].append(score)
        
        # Average scaffolding needs
        avg_scaffolding_needs = {
            need_type: sum(scores) / len(scores) if scores else 0
            for need_type, scores in scaffolding_needs.items()
        }
        
        analysis_summary = {
            "session_summary": {
                "total_interactions": len(user_inputs),
                "total_words": total_words,
                "avg_words_per_response": total_words / len(user_inputs),
                "avg_response_time": avg_response_time
            },
            "engagement_analysis": {
                "high_engagement": engagement_levels.count("high"),
                "medium_engagement": engagement_levels.count("medium"),
                "low_engagement": engagement_levels.count("low")
            },
            "learning_analysis": {
                "progressing": learning_states.count("progressing"),
                "struggling": learning_states.count("struggling"),
                "neutral": learning_states.count("neutral"),
                "mixed": learning_states.count("mixed")
            },
            "scaffolding_needs": avg_scaffolding_needs,
            "interaction_timeline": [
                {
                    "timestamp": i["timestamp"],
                    "engagement": i["analysis"]["engagement_level"],
                    "learning_state": i["analysis"]["learning_indicators"]["learning_state"]
                }
                for i in user_inputs
            ]
        }
        
        self.session_data["analysis_summary"] = analysis_summary
        return analysis_summary
    
    def export_session_data(self, filepath: Optional[str] = None) -> str:
        """
        Export session data for experimental analysis.
        
        Args:
            filepath: Optional filepath for export
            
        Returns:
            Filepath where data was saved
        """
        if not filepath:
            filepath = f"experimental_data_{self.session_data['session_id']}.json"
        
        # Add final analysis
        self.session_data["analysis_summary"] = self.get_interaction_analysis()
        self.session_data["end_time"] = datetime.now().isoformat()
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(self.session_data, f, indent=2)
        
        logger.info(f"Session data exported to {filepath}")
        return filepath
    
    def get_session_data(self) -> Dict[str, Any]:
        """Get current session data."""
        return self.session_data
    
    def reset_session(self) -> None:
        """Reset session data for a new session."""
        self.interaction_log = []
        self.session_data = {
            "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": datetime.now().isoformat(),
            "interactions": [],
            "analysis_summary": {}
        }
        logger.info("Session data reset")

# Compatibility functions for existing system
def create_enhanced_io_manager(config: Optional[Dict[str, Any]] = None) -> ExperimentalIOManager:
    """
    Create an enhanced I/O manager with default settings.
    
    Args:
        config: Configuration options
        
    Returns:
        Configured ExperimentalIOManager instance
    """
    return ExperimentalIOManager(config=config)

def create_experimental_handlers(config: Optional[Dict[str, Any]] = None) -> Tuple[Callable, Callable]:
    """
    Create enhanced input/output handlers compatible with existing DialogueManager.
    
    Args:
        config: Configuration options
        
    Returns:
        Tuple of (input_handler, output_handler) functions
    """
    io_manager = create_enhanced_io_manager(config)
    
    def enhanced_input_handler(prompt: str) -> str:
        return io_manager.handle_user_input(prompt)
    
    def enhanced_output_handler(text: str) -> None:
        io_manager.handle_system_output(text)
    
    # Store reference to io_manager for later access
    enhanced_input_handler.io_manager = io_manager
    enhanced_output_handler.io_manager = io_manager
    
    return enhanced_input_handler, enhanced_output_handler
