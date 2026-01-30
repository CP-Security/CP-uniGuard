import numpy as np
from collections import deque
from scipy.stats import norm

class OnlineAdaptiveThreshold:
    """
    Enhanced Online Adaptive Threshold via Dual-Buffer Mechanism
    
    This class implements an enhanced adaptive threshold mechanism with dual buffers:
    - A positive buffer for consensus scores that passed threshold checks
    - A negative buffer for consensus scores that failed threshold checks
    
    The threshold is set at the midpoint between the two distributions, allowing
    it to adapt to the natural gap between benign and malicious consensus patterns.
    """
    
    def __init__(self, alpha=0.2, gamma=0.02, window_size=30, min_window_size=5, initial_threshold=0.3,
                 use_median=True, min_neg_per_frame=1, decay_factor=0.98):
        """
        Initialize the enhanced online adaptive threshold with dual buffers.
        
        Args:
            alpha (float): Smoothing factor for threshold updates (default: 0.2)
            gamma (float): Additive compensation for recursive levels (default: 0.02)
            window_size (int): Maximum size of sliding windows (default: 30)
            min_window_size (int): Minimum window size before computing adaptive threshold (default: 5)
            initial_threshold (float): Initial threshold value (default: 0.3)
            use_median (bool): Use median instead of mean for more robustness (default: True)
            min_neg_per_frame (int): Minimum negative samples to collect per frame (default: 1)
            decay_factor (float): Factor to decay threshold when buffers are incomplete (default: 0.98)
        """
        self.alpha = alpha
        self.gamma = gamma
        self.window_size = window_size
        self.min_window_size = min_window_size
        self.initial_threshold = initial_threshold
        self.use_median = use_median
        self.min_neg_per_frame = min_neg_per_frame
        self.decay_factor = decay_factor
        
        # Dual buffer implementation
        self.positive_buffer = deque(maxlen=window_size)  # Scores that passed threshold
        self.negative_buffer = deque(maxlen=window_size)  # Scores that failed threshold
        
        # Current adaptive threshold
        self.current_threshold = initial_threshold
        
        # Track frame statistics
        self.frame_scores = []  # Stores all scores from current frame
        self.frame_positives = []  # Positive samples from current frame
        self.frame_negatives = []  # Negative samples from current frame
        self.consecutive_empty_frames = 0
        
    def add_score(self, score, is_positive):
        """
        Add a new score to the appropriate buffer.
        
        Args:
            score (float): The consensus score
            is_positive (bool): Whether the score passed threshold check
        """
        self.frame_scores.append(score)
        
        if is_positive:
            self.frame_positives.append(score)
        else:
            self.frame_negatives.append(score)
    
    def end_frame_processing(self):
        """
        Process all collected scores at the end of a frame.
        Should be called once per frame after all scores are collected.
        
        Returns:
            float: Updated threshold for next frame
        """
        # Add all positives to positive buffer
        if self.frame_positives:
            self.positive_buffer.extend(self.frame_positives)
            self.consecutive_empty_frames = 0
        else:
            self.consecutive_empty_frames += 1
        
        # Add all negatives to negative buffer
        if self.frame_negatives:
            self.negative_buffer.extend(self.frame_negatives)
        # If no negatives but we have scores, add the lowest as negative
        elif self.frame_scores and self.min_neg_per_frame > 0:
            # Sort scores and take the lowest n as negative samples
            sorted_scores = sorted(self.frame_scores)
            lowest_scores = sorted_scores[:min(self.min_neg_per_frame, len(sorted_scores))]
            self.negative_buffer.extend(lowest_scores)
            
        # Update threshold based on buffers
        self._update_threshold()
        
        # Clear frame data for next frame
        self.frame_scores = []
        self.frame_positives = []
        self.frame_negatives = []
        
        return self.current_threshold
    
    def _update_threshold(self):
        """
        Update the threshold based on positive and negative buffers.
        Uses the midpoint between distributions as the target threshold.
        """
        # Check if we have enough samples in both buffers
        if (len(self.positive_buffer) >= self.min_window_size and 
            len(self.negative_buffer) >= self.min_window_size):
            
            # Compute statistics from both buffers
            if self.use_median:
                pos_center = np.median(self.positive_buffer)
                neg_center = np.median(self.negative_buffer)
            else:
                pos_center = np.mean(self.positive_buffer)
                neg_center = np.mean(self.negative_buffer)
            
            # Compute midpoint as candidate threshold
            threshold_candidate = 0.5 * (pos_center + neg_center)
            
            # Apply smoothing using alpha
            self.current_threshold = ((1 - self.alpha) * self.current_threshold + 
                                     self.alpha * threshold_candidate)
            
            print(f"Dual buffer update: pos={pos_center:.4f}, neg={neg_center:.4f}, "
                  f"candidate={threshold_candidate:.4f}, new={self.current_threshold:.4f}")
                  
        # If only positive buffer has enough samples
        elif len(self.positive_buffer) >= self.min_window_size:
            if self.use_median:
                pos_center = np.median(self.positive_buffer)
            else:
                pos_center = np.mean(self.positive_buffer)
                
            # Use a more conservative estimate based only on positives
            threshold_candidate = pos_center * 0.8  # 80% of positive center
            self.current_threshold = ((1 - self.alpha) * self.current_threshold + 
                                     self.alpha * threshold_candidate)
            
            print(f"Positive-only update: pos={pos_center:.4f}, "
                  f"candidate={threshold_candidate:.4f}, new={self.current_threshold:.4f}")
                  
        # If only negative buffer has enough samples
        elif len(self.negative_buffer) >= self.min_window_size:
            if self.use_median:
                neg_center = np.median(self.negative_buffer)
            else:
                neg_center = np.mean(self.negative_buffer)
                
            # Use a more aggressive estimate based only on negatives
            threshold_candidate = neg_center * 1.2  # 120% of negative center
            self.current_threshold = ((1 - self.alpha) * self.current_threshold + 
                                     self.alpha * threshold_candidate)
                                     
            print(f"Negative-only update: neg={neg_center:.4f}, "
                  f"candidate={threshold_candidate:.4f}, new={self.current_threshold:.4f}")
                  
        # If neither buffer has enough samples, apply decay
        else:
            if self.consecutive_empty_frames > 2:
                # Apply decay to prevent threshold from getting stuck
                self.current_threshold *= self.decay_factor
                print(f"Applied decay after {self.consecutive_empty_frames} empty frames: "
                      f"threshold={self.current_threshold:.4f}")
    
    def get_threshold_with_depth_adjustment(self, depth=0):
        """
        Get the current threshold with optional adjustment for recursive depth.
        
        Args:
            depth (int): Current recursive depth level
            
        Returns:
            float: Depth-adjusted threshold
        """
        # Apply additive gamma adjustment for depth
        adjusted_threshold = self.current_threshold + (depth * self.gamma)
        return adjusted_threshold
    
    def get_current_threshold(self):
        """
        Get the current adaptive threshold without depth adjustment.
        
        Returns:
            float: Current threshold value
        """
        return self.current_threshold
    
    def reset_buffers(self):
        """
        Reset all buffers and threshold to initial state.
        """
        self.positive_buffer.clear()
        self.negative_buffer.clear()
        self.frame_scores = []
        self.frame_positives = []
        self.frame_negatives = []
        self.consecutive_empty_frames = 0
        self.current_threshold = self.initial_threshold
        print(f"Reset all buffers and threshold to {self.initial_threshold}")
    
    def get_buffer_stats(self):
        """
        Get statistics about the current buffers.
        
        Returns:
            dict: Dictionary containing buffer statistics
        """
        return {
            'positive_buffer_size': len(self.positive_buffer),
            'negative_buffer_size': len(self.negative_buffer),
            'positive_mean': np.mean(self.positive_buffer) if self.positive_buffer else 0.0,
            'negative_mean': np.mean(self.negative_buffer) if self.negative_buffer else 0.0,
            'positive_median': np.median(self.positive_buffer) if len(self.positive_buffer) > 0 else 0.0,
            'negative_median': np.median(self.negative_buffer) if len(self.negative_buffer) > 0 else 0.0,
            'current_threshold': self.current_threshold,
            'consecutive_empty_frames': self.consecutive_empty_frames
        }
