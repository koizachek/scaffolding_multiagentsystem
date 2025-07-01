"""
Logging Utility

This module provides functionality for comprehensive session logging.
"""

import os
import json
import csv
import logging
import datetime
from typing import Dict, List, Any, Optional, Union

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def setup_logging(log_dir: str = "logs", log_level: str = "INFO", log_to_file: bool = True) -> logging.Logger:
    """
    Set up logging configuration for the application.
    
    Args:
        log_dir: Directory to save log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to a file
        
    Returns:
        Configured logger
    """
    # Create log directory if it doesn't exist
    if log_to_file:
        os.makedirs(log_dir, exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    
    # Set log level
    level = getattr(logging, log_level.upper())
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler if requested
    if log_to_file:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"mas_{timestamp}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    logger.info(f"Logging configured with level {log_level}")
    if log_to_file:
        logger.info(f"Logging to file: {log_file}")
    
    return root_logger

class SessionLogger:
    """
    Logger for multi-agent scaffolding sessions.
    
    This class handles comprehensive logging of all session activities,
    including user inputs, agent outputs, internal reasoning, and ZPD estimates.
    """
    
    def __init__(self, 
                log_dir: str = "logs", 
                session_id: Optional[str] = None,
                format: str = "json"):
        """
        Initialize the session logger.
        
        Args:
            log_dir: Directory to save log files
            session_id: Unique identifier for the session (defaults to timestamp)
            format: Log format ('json' or 'csv')
        """
        self.log_dir = log_dir
        self.format = format.lower()
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Generate session ID if not provided
        if session_id is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            session_id = f"session_{timestamp}"
        
        self.session_id = session_id
        
        # Initialize log entries list
        self.log_entries = []
        
        # Set up log file paths
        self.json_log_path = os.path.join(log_dir, f"{session_id}.json")
        self.csv_log_path = os.path.join(log_dir, f"{session_id}.csv")
        
        logger.info(f"Initialized session logger with ID: {session_id}")
    
    def log_event(self, 
                 event_type: str,
                 user_input: Optional[str] = None,
                 agent_type: Optional[str] = None,
                 agent_response: Optional[str] = None,
                 agent_reasoning: Optional[str] = None,
                 zpd_estimate: Optional[Dict[str, Any]] = None,
                 active_features: Optional[Dict[str, bool]] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Log a session event.
        
        Args:
            event_type: Type of event (e.g., 'user_input', 'agent_response')
            user_input: User's input text
            agent_type: Type of agent (e.g., 'lead', 'strategic_scaffolding')
            agent_response: Agent's response text
            agent_reasoning: Agent's internal reasoning
            zpd_estimate: Current ZPD estimate
            active_features: Currently active design features
            metadata: Additional metadata for the event
            
        Returns:
            The created log entry
        """
        # Create timestamp
        timestamp = datetime.datetime.now().isoformat()
        
        # Create log entry
        log_entry = {
            "timestamp": timestamp,
            "event_type": event_type,
            "session_id": self.session_id
        }
        
        # Add optional fields if provided
        if user_input is not None:
            log_entry["user_input"] = user_input
        
        if agent_type is not None:
            log_entry["agent_type"] = agent_type
        
        if agent_response is not None:
            log_entry["agent_response"] = agent_response
        
        if agent_reasoning is not None:
            log_entry["agent_reasoning"] = agent_reasoning
        
        if zpd_estimate is not None:
            log_entry["zpd_estimate"] = zpd_estimate
        
        if active_features is not None:
            log_entry["active_features"] = active_features
        
        if metadata is not None:
            log_entry["metadata"] = metadata
        
        # Add to log entries list
        self.log_entries.append(log_entry)
        
        # Write to log file
        self._write_log()
        
        logger.debug(f"Logged event: {event_type}")
        
        return log_entry
    
    def log_user_input(self, 
                      input_text: str, 
                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Log a user input event.
        
        Args:
            input_text: User's input text
            metadata: Additional metadata for the event
            
        Returns:
            The created log entry
        """
        return self.log_event(
            event_type="user_input",
            user_input=input_text,
            metadata=metadata
        )
    
    def log_agent_response(self, 
                          agent_type: str,
                          response_text: str,
                          reasoning: Optional[str] = None,
                          zpd_estimate: Optional[Dict[str, Any]] = None,
                          active_features: Optional[Dict[str, bool]] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Log an agent response event.
        
        Args:
            agent_type: Type of agent (e.g., 'lead', 'strategic_scaffolding')
            response_text: Agent's response text
            reasoning: Agent's internal reasoning
            zpd_estimate: Current ZPD estimate
            active_features: Currently active design features
            metadata: Additional metadata for the event
            
        Returns:
            The created log entry
        """
        return self.log_event(
            event_type="agent_response",
            agent_type=agent_type,
            agent_response=response_text,
            agent_reasoning=reasoning,
            zpd_estimate=zpd_estimate,
            active_features=active_features,
            metadata=metadata
        )
    
    def log_system_event(self, 
                        event_subtype: str,
                        details: Dict[str, Any],
                        metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Log a system event.
        
        Args:
            event_subtype: Subtype of system event (e.g., 'session_start', 'session_end')
            details: Event details
            metadata: Additional metadata for the event
            
        Returns:
            The created log entry
        """
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "event_subtype": event_subtype,
            "details": details
        })
        
        return self.log_event(
            event_type="system_event",
            metadata=metadata
        )
    
    def log_session_start(self, 
                         config: Dict[str, Any],
                         metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Log a session start event.
        
        Args:
            config: Session configuration
            metadata: Additional metadata for the event
            
        Returns:
            The created log entry
        """
        return self.log_system_event(
            event_subtype="session_start",
            details={"config": config},
            metadata=metadata
        )
    
    def log_session_end(self, 
                       summary: Dict[str, Any],
                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Log a session end event.
        
        Args:
            summary: Session summary
            metadata: Additional metadata for the event
            
        Returns:
            The created log entry
        """
        return self.log_system_event(
            event_subtype="session_end",
            details={"summary": summary},
            metadata=metadata
        )
    
    def log_round_start(self, 
                       round_number: int,
                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Log a round start event.
        
        Args:
            round_number: Round number
            metadata: Additional metadata for the event
            
        Returns:
            The created log entry
        """
        return self.log_system_event(
            event_subtype="round_start",
            details={"round_number": round_number},
            metadata=metadata
        )
    
    def log_round_end(self, 
                     round_number: int,
                     summary: Dict[str, Any],
                     metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Log a round end event.
        
        Args:
            round_number: Round number
            summary: Round summary
            metadata: Additional metadata for the event
            
        Returns:
            The created log entry
        """
        return self.log_system_event(
            event_subtype="round_end",
            details={
                "round_number": round_number,
                "summary": summary
            },
            metadata=metadata
        )
    
    def log_zpd_update(self, 
                      zpd_estimate: Dict[str, Any],
                      reason: str,
                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Log a ZPD update event.
        
        Args:
            zpd_estimate: Updated ZPD estimate
            reason: Reason for the update
            metadata: Additional metadata for the event
            
        Returns:
            The created log entry
        """
        return self.log_system_event(
            event_subtype="zpd_update",
            details={
                "zpd_estimate": zpd_estimate,
                "reason": reason
            },
            metadata=metadata
        )
    
    def _write_log(self) -> None:
        """
        Write log entries to the log file.
        """
        # Write to JSON log file
        with open(self.json_log_path, 'w') as f:
            json.dump(self.log_entries, f, indent=2)
        
        # Write to CSV log file if format is CSV
        if self.format == "csv":
            # Get all possible keys from all log entries
            keys = set()
            for entry in self.log_entries:
                keys.update(entry.keys())
            
            # Sort keys for consistent column order
            sorted_keys = sorted(keys)
            
            with open(self.csv_log_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=sorted_keys)
                writer.writeheader()
                for entry in self.log_entries:
                    writer.writerow(entry)
    
    def get_log_entries(self, 
                       event_type: Optional[str] = None,
                       agent_type: Optional[str] = None,
                       start_time: Optional[Union[str, datetime.datetime]] = None,
                       end_time: Optional[Union[str, datetime.datetime]] = None) -> List[Dict[str, Any]]:
        """
        Get filtered log entries.
        
        Args:
            event_type: Filter by event type
            agent_type: Filter by agent type
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            List of filtered log entries
        """
        # Convert datetime objects to ISO format strings
        if isinstance(start_time, datetime.datetime):
            start_time = start_time.isoformat()
        
        if isinstance(end_time, datetime.datetime):
            end_time = end_time.isoformat()
        
        # Filter log entries
        filtered_entries = []
        for entry in self.log_entries:
            # Check event type
            if event_type is not None and entry.get("event_type") != event_type:
                continue
            
            # Check agent type
            if agent_type is not None and entry.get("agent_type") != agent_type:
                continue
            
            # Check start time
            if start_time is not None and entry.get("timestamp", "") < start_time:
                continue
            
            # Check end time
            if end_time is not None and entry.get("timestamp", "") > end_time:
                continue
            
            filtered_entries.append(entry)
        
        return filtered_entries
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the session.
        
        Returns:
            Session summary dictionary
        """
        # Count events by type
        event_counts = {}
        for entry in self.log_entries:
            event_type = entry.get("event_type")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Count agent responses by type
        agent_counts = {}
        for entry in self.log_entries:
            if entry.get("event_type") == "agent_response":
                agent_type = entry.get("agent_type")
                agent_counts[agent_type] = agent_counts.get(agent_type, 0) + 1
        
        # Get session start and end times
        start_time = self.log_entries[0]["timestamp"] if self.log_entries else None
        end_time = self.log_entries[-1]["timestamp"] if self.log_entries else None
        
        # Calculate session duration
        duration = None
        if start_time and end_time:
            start_dt = datetime.datetime.fromisoformat(start_time)
            end_dt = datetime.datetime.fromisoformat(end_time)
            duration = (end_dt - start_dt).total_seconds()
        
        # Create summary
        summary = {
            "session_id": self.session_id,
            "start_time": start_time,
            "end_time": end_time,
            "duration_seconds": duration,
            "total_events": len(self.log_entries),
            "event_counts": event_counts,
            "agent_counts": agent_counts
        }
        
        return summary
    
    def export_logs(self, format: str = "json") -> str:
        """
        Export logs to a file.
        
        Args:
            format: Export format ('json' or 'csv')
            
        Returns:
            Path to the exported log file
        """
        format = format.lower()
        
        if format == "json":
            return self.json_log_path
        elif format == "csv":
            # Ensure CSV log is up to date
            if self.format != "csv":
                self.format = "csv"
                self._write_log()
            
            return self.csv_log_path
        else:
            raise ValueError(f"Unsupported export format: {format}")
