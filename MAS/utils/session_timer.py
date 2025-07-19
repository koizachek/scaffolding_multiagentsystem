"""
Session Timer

This module provides timing functionality for experimental sessions,
including round timers and break management.
"""

import time
import threading
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SessionTimer:
    """
    Manages timing for experimental sessions with round limits and breaks.
    """
    
    def __init__(self, 
                 round_duration_minutes: int = 7,
                 break_duration_minutes: int = 2):
        """
        Initialize the session timer.
        
        Args:
            round_duration_minutes: Duration of each round in minutes
            break_duration_minutes: Duration of breaks between rounds in minutes
        """
        self.round_duration = round_duration_minutes * 60  # Convert to seconds
        self.break_duration = break_duration_minutes * 60  # Convert to seconds
        
        # Timer state
        self.current_round = 0
        self.round_active = False
        self.break_active = False
        self.session_start_time = None
        self.round_start_time = None
        self.round_end_time = None
        
        # Callbacks
        self.round_timeout_callback = None
        self.break_end_callback = None
        
        # Threading
        self.timer_thread = None
        self.break_thread = None
        
        logger.info(f"Session timer initialized: {round_duration_minutes}min rounds, {break_duration_minutes}min breaks")
    
    def start_session(self):
        """Start a new experimental session."""
        self.session_start_time = datetime.now()
        self.current_round = 0
        logger.info(f"Session started at {self.session_start_time.isoformat()}")
    
    def start_round(self, round_number: int, timeout_callback: Optional[Callable] = None):
        """
        Start a new round with timer.
        
        Args:
            round_number: Round number (0-based)
            timeout_callback: Function to call when round times out
        """
        if self.round_active:
            logger.warning("Round already active, stopping previous round")
            self.stop_round()
        
        self.current_round = round_number
        self.round_start_time = datetime.now()
        self.round_active = True
        self.round_timeout_callback = timeout_callback
        
        # Start timer thread
        self.timer_thread = threading.Thread(target=self._round_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()
        
        logger.info(f"Round {round_number} started at {self.round_start_time.isoformat()}")
        print(f"\n⏱️  Round {round_number + 1} started! You have {self.round_duration // 60} minutes.")
    
    def stop_round(self) -> Dict[str, Any]:
        """
        Stop the current round and return timing data.
        
        Returns:
            Dictionary with round timing information
        """
        if not self.round_active:
            logger.warning("No active round to stop")
            return {}
        
        self.round_end_time = datetime.now()
        self.round_active = False
        
        # Calculate duration
        if self.round_start_time:
            duration = (self.round_end_time - self.round_start_time).total_seconds()
        else:
            duration = 0
        
        round_data = {
            "round_number": self.current_round,
            "start_time": self.round_start_time.isoformat() if self.round_start_time else None,
            "end_time": self.round_end_time.isoformat(),
            "duration_seconds": duration,
            "duration_minutes": duration / 60,
            "completed_naturally": duration < self.round_duration,
            "timed_out": duration >= self.round_duration
        }
        
        logger.info(f"Round {self.current_round} ended after {duration:.1f} seconds")
        return round_data
    
    def start_break(self, break_end_callback: Optional[Callable] = None):
        """
        Start a break period between rounds.
        
        Args:
            break_end_callback: Function to call when break ends
        """
        if self.break_active:
            logger.warning("Break already active")
            return
        
        self.break_active = True
        self.break_end_callback = break_end_callback
        
        # Start break thread
        self.break_thread = threading.Thread(target=self._break_timer)
        self.break_thread.daemon = True
        self.break_thread.start()
        
        logger.info(f"Break started for {self.break_duration // 60} minutes")
        print(f"\n☕ Break time! {self.break_duration // 60} minutes to rest...")
    
    def get_round_time_remaining(self) -> int:
        """
        Get remaining time in current round.
        
        Returns:
            Remaining seconds, or 0 if no active round
        """
        if not self.round_active or not self.round_start_time:
            return 0
        
        elapsed = (datetime.now() - self.round_start_time).total_seconds()
        remaining = max(0, self.round_duration - elapsed)
        return int(remaining)
    
    def get_round_elapsed_time(self) -> int:
        """
        Get elapsed time in current round.
        
        Returns:
            Elapsed seconds, or 0 if no active round
        """
        if not self.round_active or not self.round_start_time:
            return 0
        
        elapsed = (datetime.now() - self.round_start_time).total_seconds()
        return int(elapsed)
    
    def is_round_active(self) -> bool:
        """Check if a round is currently active."""
        return self.round_active
    
    def is_break_active(self) -> bool:
        """Check if a break is currently active."""
        return self.break_active
    
    def get_session_duration(self) -> int:
        """
        Get total session duration.
        
        Returns:
            Session duration in seconds, or 0 if session not started
        """
        if not self.session_start_time:
            return 0
        
        return int((datetime.now() - self.session_start_time).total_seconds())
    
    def _round_timer(self):
        """Internal timer thread for round duration."""
        try:
            # Wait for round duration
            time.sleep(self.round_duration)
            
            # Check if round is still active (might have been stopped manually)
            if self.round_active:
                self.round_active = False
                logger.info(f"Round {self.current_round} timed out")
                print(f"\n⏰ Time's up! Round {self.current_round + 1} has ended.")
                
                # Call timeout callback if provided
                if self.round_timeout_callback:
                    try:
                        self.round_timeout_callback()
                    except Exception as e:
                        logger.error(f"Error in round timeout callback: {e}")
        
        except Exception as e:
            logger.error(f"Error in round timer thread: {e}")
    
    def _break_timer(self):
        """Internal timer thread for break duration."""
        try:
            # Show countdown every 30 seconds
            remaining = self.break_duration
            
            while remaining > 0 and self.break_active:
                if remaining % 30 == 0 or remaining <= 10:
                    mins, secs = divmod(remaining, 60)
                    print(f"⏱️  Break time remaining: {mins:02d}:{secs:02d}")
                
                time.sleep(min(10, remaining))
                remaining -= min(10, remaining)
            
            # Break ended
            if self.break_active:
                self.break_active = False
                logger.info("Break period ended")
                print("🔔 Break over! Ready for the next round.")
                
                # Call break end callback if provided
                if self.break_end_callback:
                    try:
                        self.break_end_callback()
                    except Exception as e:
                        logger.error(f"Error in break end callback: {e}")
        
        except Exception as e:
            logger.error(f"Error in break timer thread: {e}")
    
    def format_time(self, seconds: int) -> str:
        """
        Format seconds into MM:SS format.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted time string
        """
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"
    
    def get_time_display(self) -> str:
        """
        Get current time display for UI.
        
        Returns:
            Formatted time string showing current status
        """
        if self.round_active:
            remaining = self.get_round_time_remaining()
            elapsed = self.get_round_elapsed_time()
            return f"Round {self.current_round + 1} - {self.format_time(elapsed)} elapsed, {self.format_time(remaining)} remaining"
        elif self.break_active:
            return "Break in progress..."
        else:
            session_duration = self.get_session_duration()
            return f"Session time: {self.format_time(session_duration)}"

class RoundManager:
    """
    Higher-level manager for handling complete round cycles with timing.
    """
    
    def __init__(self, 
                 total_rounds: int = 4,
                 round_duration_minutes: int = 7,
                 break_duration_minutes: int = 2):
        """
        Initialize the round manager.
        
        Args:
            total_rounds: Total number of rounds in session
            round_duration_minutes: Duration of each round
            break_duration_minutes: Duration of breaks
        """
        self.total_rounds = total_rounds
        self.timer = SessionTimer(round_duration_minutes, break_duration_minutes)
        self.round_data = []
        self.current_round_number = 0
        
        logger.info(f"Round manager initialized for {total_rounds} rounds")
    
    def start_session(self):
        """Start the experimental session."""
        self.timer.start_session()
        self.round_data = []
        self.current_round_number = 0
    
    def start_next_round(self, timeout_callback: Optional[Callable] = None) -> bool:
        """
        Start the next round if available.
        
        Args:
            timeout_callback: Function to call when round times out
            
        Returns:
            True if round started, False if no more rounds
        """
        if self.current_round_number >= self.total_rounds:
            logger.info("All rounds completed")
            return False
        
        self.timer.start_round(self.current_round_number, timeout_callback)
        return True
    
    def end_current_round(self) -> Dict[str, Any]:
        """
        End the current round and store timing data.
        
        Returns:
            Round timing data
        """
        round_data = self.timer.stop_round()
        if round_data:
            self.round_data.append(round_data)
            self.current_round_number += 1
        
        return round_data
    
    def start_break_if_needed(self, break_end_callback: Optional[Callable] = None) -> bool:
        """
        Start break if more rounds remain.
        
        Args:
            break_end_callback: Function to call when break ends
            
        Returns:
            True if break started, False if no break needed
        """
        if self.current_round_number < self.total_rounds:
            self.timer.start_break(break_end_callback)
            return True
        return False
    
    def is_session_complete(self) -> bool:
        """Check if all rounds are completed."""
        return self.current_round_number >= self.total_rounds
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary of the entire session.
        
        Returns:
            Session summary with timing data
        """
        total_session_time = self.timer.get_session_duration()
        total_round_time = sum(rd.get("duration_seconds", 0) for rd in self.round_data)
        
        return {
            "total_rounds": len(self.round_data),
            "planned_rounds": self.total_rounds,
            "session_completed": self.is_session_complete(),
            "total_session_time_seconds": total_session_time,
            "total_round_time_seconds": total_round_time,
            "average_round_time_seconds": total_round_time / max(1, len(self.round_data)),
            "rounds_timed_out": sum(1 for rd in self.round_data if rd.get("timed_out", False)),
            "round_details": self.round_data
        }
