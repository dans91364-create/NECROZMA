#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - ADVANCED FEATURES 💎🌟⚡

Advanced Feature Extraction:  The Higher Dimensions
"Beyond the visible spectrum lies infinite power"

Technical: Advanced time series feature extraction
- Phase Space Reconstruction (Takens Embedding)
- Recurrence Quantification Analysis (RQA)
- Multifractal Analysis
- Pattern Detection (Crystals)
- Ultra Necrozma Features (Photon, Z-Crystal)
"""

import numpy as np
from scipy import stats
from scipy.spatial. distance import pdist, cdist
import warnings

warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════
# ⚡ NUMBA JIT COMPILATION
# ═══════════════════════════════════════════════════════════════

try:
    from numba import njit
    NUMBA_AVAILABLE = True
except ImportError: 
    NUMBA_AVAILABLE = False
    def njit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


# ═══════════════════════════════════════════════════════════════
# 🌌 GRUPO 5: PHASE SPACE / QUANTUM FEATURES
# Technical: Nonlinear dynamics state space analysis
# ═══════════════════════════════════════════════════════════════

def phase_space_reconstruction(data, dim=3, delay=1):
    """
    Phase Space Reconstruction - Takens Embedding (Palkia's Spatial Rift)
    Technical: Reconstruct attractor from time series
    
    Args: 
        data: Time series
        dim: Embedding dimension
        delay: Time delay
        
    Returns: 
        dict: Phase space features
    """
    features = {}
    
    if len(data) < dim * delay + 10:
        return features
    
    data = np.asarray(data, dtype=np.float64)
    
    try:
        # Build embedding vectors
        n_vectors = len(data) - (dim - 1) * delay
        vectors = np.zeros((n_vectors, dim))
        
        for i in range(n_vectors):
            for j in range(dim):
                vectors[i, j] = data[i + j * delay]
        
        # Distance statistics
        if len(vectors) > 1:
            # Sample for large datasets
            if len(vectors) > 500:
                idx = np.random.choice(len(vectors), 500, replace=False)
                vectors_sample = vectors[idx]
            else:
                vectors_sample = vectors
            
            distances = pdist(vectors_sample, metric="euclidean")
            
            if len(distances) > 0:
                features["phase_dist_mean"] = float(np.mean(distances))
                features["phase_dist_std"] = float(np.std(distances))
                features["phase_dist_max"] = float(np.max(distances))
                features["phase_dist_min"] = float(np.min(distances))
                features["phase_dist_median"] = float(np.median(distances))
                
                # Correlation dimension estimate
                if len(distances) > 10:
                    r_vals = np.percentile(distances[distances > 0], [10, 25, 50, 75, 90])
                    C_r = []
                    
                    for r in r_vals:
                        C_r.append(np.mean(distances < r))
                    
                    valid = [i for i, c in enumerate(C_r) if c > 0 and c < 1]
                    if len(valid) >= 2:
                        log_r = np.log([r_vals[i] for i in valid])
                        log_C = np.log([C_r[i] for i in valid])
                        slope = np.polyfit(log_r, log_C, 1)[0]
                        features["correlation_dimension"] = float(slope)
        
        # Attractor properties
        if len(vectors) > 0:
            # Center of mass
            centroid = np.mean(vectors, axis=0)
            features["attractor_centroid_norm"] = float(np.linalg.norm(centroid))
            
            # Spread (average distance from centroid)
            dists_from_center = np.linalg.norm(vectors - centroid, axis=1)
            features["attractor_spread"] = float(np.mean(dists_from_center))
            features["attractor_spread_std"] = float(np.std(dists_from_center))
            
            # Trajectory length
            trajectory_diffs = np.diff(vectors, axis=0)
            trajectory_lengths = np.linalg.norm(trajectory_diffs, axis=1)
            features["trajectory_length_mean"] = float(np.mean(trajectory_lengths))
            features["trajectory_length_total"] = float(np.sum(trajectory_lengths))
        
    except Exception:
        pass
    
    return features


def correlation_dimension(data, max_dim=10):
    """
    Correlation Dimension (Dimensional Complexity)
    Technical: Grassberger-Procaccia algorithm approximation
    """
    if len(data) < 100:
        return 1.0
    
    data = np.asarray(data, dtype=np.float64)
    
    try:
        features = phase_space_reconstruction(data, dim=3, delay=1)
        return features. get("correlation_dimension", 1.0)
    except:
        return 1.0


# ═══════════════════════════════════════════════════════════════
# 🔄 GRUPO 6: RECURRENCE QUANTIFICATION ANALYSIS (RQA)
# Technical: Analyze recurrence plot statistics
# ═══════════════════════════════════════════════════════════════

def _find_line_lengths(binary_array):
    """Helper:  Find lengths of consecutive 1s in binary array"""
    lengths = []
    current_length = 0
    
    for val in binary_array:
        if val == 1:
            current_length += 1
        else:
            if current_length > 0:
                lengths.append(current_length)
            current_length = 0
    
    if current_length > 0:
        lengths.append(current_length)
    
    return lengths


def recurrence_features(data, threshold_mult=0.1, max_size=300):
    """
    Recurrence Quantification Analysis - RQA (Dialga's Time Echo)
    Technical: Analyze patterns in recurrence plots
    
    Returns:
        dict: RQA features including:
            - recurrence_rate: Probability of recurrence
            - determinism: Ratio of recurrent points in diagonal lines
            - laminarity: Ratio of recurrent points in vertical lines
            - entropy_diagonal: Shannon entropy of diagonal line lengths
    """
    features = {}
    
    n = len(data)
    if n < 20:
        return features
    
    data = np.asarray(data, dtype=np.float64)
    
    # Limit size for performance
    if n > max_size:
        data = data[-max_size:]
        n = max_size
    
    try: 
        threshold = threshold_mult * np.std(data)
        if threshold == 0:
            threshold = 0.01
        
        # Build recurrence matrix
        dist_matrix = cdist(data. reshape(-1, 1), data.reshape(-1, 1), metric="euclidean")
        recurrence = (dist_matrix <= threshold).astype(np.int32)
        
        total_recurrence = np.sum(recurrence)
        
        # Recurrence rate
        rr = total_recurrence / (n * n)
        features["recurrence_rate"] = float(rr)
        
        if total_recurrence == 0:
            return features
        
        # ═══ DIAGONAL LINES (Determinism) ═══
        diag_lengths = []
        
        for k in range(1, n):
            diag = np.diag(recurrence, k)
            diag_lengths.extend(_find_line_lengths(diag))
            
            if k > 0:
                diag = np.diag(recurrence, -k)
                diag_lengths.extend(_find_line_lengths(diag))
        
        if diag_lengths:
            diag_lengths = [l for l in diag_lengths if l >= 2]
            if diag_lengths:
                total_diag_points = sum(diag_lengths)
                det = total_diag_points / (total_recurrence - n + 1)
                features["determinism"] = float(min(det, 1.0))
                features["avg_diagonal_length"] = float(np. mean(diag_lengths))
                features["max_diagonal_length"] = float(np.max(diag_lengths))
                
                # Entropy of diagonal line distribution
                hist, _ = np.histogram(diag_lengths, bins=min(20, max(diag_lengths)))
                hist = hist[hist > 0]
                if len(hist) > 0:
                    probs = hist / sum(hist)
                    features["entropy_diagonal"] = float(-np.sum(probs * np.log2(probs)))
        
        # ═══ VERTICAL LINES (Laminarity) ═══
        vert_lengths = []
        
        for col in range(n):
            vert_lengths.extend(_find_line_lengths(recurrence[:, col]))
        
        if vert_lengths: 
            vert_lengths = [l for l in vert_lengths if l >= 2]
            if vert_lengths:
                total_vert_points = sum(vert_lengths)
                lam = total_vert_points / total_recurrence
                features["laminarity"] = float(min(lam, 1.0))
                features["trapping_time"] = float(np.mean(vert_lengths))
                features["max_vertical_length"] = float(np. max(vert_lengths))
        
        # ═══ RATIO FEATURES ═══
        if "determinism" in features and "laminarity" in features: 
            features["det_lam_ratio"] = float(
                features["determinism"] / (features["laminarity"] + 1e-10)
            )
        
    except Exception:
        pass
    
    return features


# ═══════════════════════════════════════════════════════════════
# 💎 GRUPO 7: MULTIFRACTAL ANALYSIS
# Technical: Multiscale fractal properties (MF-DFA)
# ═══════════════════════════════════════════════════════════════

def multifractal_features(data, q_values=None, scales=None):
    """
    Multifractal Detrended Fluctuation Analysis - MF-DFA (Z-Crystal Spectrum)
    Technical: Generalized Hurst exponents for different q-moments
    
    Args:
        data: Time series
        q_values: List of q-moments (default: -3 to 3)
        scales: List of scales (default: auto)
        
    Returns:
        dict:  Multifractal features including:
            - h_q values for each q
            - multifractal_width:  Range of h(q)
            - multifractal_asymmetry: Asymmetry of spectrum
    """
    features = {}
    
    if len(data) < 64:
        return features
    
    data = np.asarray(data, dtype=np.float64)
    n = len(data)
    
    if q_values is None: 
        q_values = [-3, -2, -1, -0.5, 0.5, 1, 2, 3]
    
    if scales is None:
        scales = [4, 8, 16, 32]
        scales = [s for s in scales if s < n // 4]
    
    if len(scales) < 2:
        return features
    
    try:
        # Integrate series
        y = np.cumsum(data - np.mean(data))
        
        # Calculate fluctuation for each q and scale
        h_q = {}
        
        for q in q_values:
            F_q = []
            
            for s in scales:
                n_segments = n // s
                if n_segments == 0:
                    continue
                
                fluctuations = []
                
                for v in range(n_segments):
                    segment = y[v * s:(v + 1) * s]
                    x = np.arange(s)
                    
                    # Detrend with linear fit
                    coeffs = np.polyfit(x, segment, 1)
                    trend = np.polyval(coeffs, x)
                    variance = np.mean((segment - trend) ** 2)
                    
                    if variance > 0:
                        fluctuations.append(np.sqrt(variance))
                
                if fluctuations:
                    fluct_array = np.array(fluctuations)
                    
                    if q == 0:
                        F_q.append(np.exp(np.mean(np.log(fluct_array + 1e-10))))
                    else:
                        F_q.append(np.power(np.mean(np.power(fluct_array, q)), 1.0 / q))
            
            if len(F_q) >= 2:
                log_s = np.log(scales[: len(F_q)])
                log_F = np.log(np.array(F_q) + 1e-10)
                
                slope, _ = np.polyfit(log_s, log_F, 1)
                h_q[q] = slope
                
                # Safe feature name
                q_str = f"{q}". replace(".", "_").replace("-", "m")
                features[f"mf_h_q{q_str}"] = float(slope)
        
        # Multifractal spectrum properties
        if len(h_q) >= 3:
            h_values = list(h_q.values())
            
            # Width (measure of multifractality)
            features["multifractal_width"] = float(max(h_values) - min(h_values))
            
            # Asymmetry
            h_positive = [h_q[q] for q in q_values if q > 0 and q in h_q]
            h_negative = [h_q[q] for q in q_values if q < 0 and q in h_q]
            
            if h_positive and h_negative:
                features["multifractal_asymmetry"] = float(
                    np.mean(h_negative) - np.mean(h_positive)
                )
            
            # Mean Hurst (from q=2)
            if 2 in h_q: 
                features["mf_hurst_q2"] = float(h_q[2])
            
            # Curvature
            if len(h_values) >= 3:
                q_list = sorted(h_q.keys())
                h_list = [h_q[q] for q in q_list]
                curvature = np.diff(h_list, n=2)
                features["multifractal_curvature"] = float(np.mean(np.abs(curvature)))
        
    except Exception:
        pass
    
    return features


# ═══════════════════════════════════════════════════════════════
# 🔮 GRUPO 8: PATTERN DETECTION (Light Crystals)
# Technical: Price pattern recognition
# ═══════════════════════════════════════════════════════════════

def detect_patterns(prices, pips=None):
    """
    Pattern Detection (Light Crystal Formation)
    Technical: Identify price patterns and formations
    
    Returns:
        dict: Pattern features including crystal counts and statistics
    """
    features = {}
    
    if len(prices) < 10:
        return features
    
    prices = np.asarray(prices, dtype=np.float64)
    
    if pips is None:
        pips = np.diff(prices) * 10000
    else:
        pips = np. asarray(pips, dtype=np.float64)
    
    if len(pips) < 5:
        return features
    
    try:
        # ═══ DIRECTION PATTERNS ═══
        directions = np.sign(pips)
        
        # Count consecutive moves
        up_streaks = []
        down_streaks = []
        current_streak = 1
        current_dir = directions[0] if len(directions) > 0 else 0
        
        for i in range(1, len(directions)):
            if directions[i] == current_dir and current_dir != 0:
                current_streak += 1
            else: 
                if current_dir > 0:
                    up_streaks.append(current_streak)
                elif current_dir < 0:
                    down_streaks.append(current_streak)
                current_streak = 1
                current_dir = directions[i]
        
        if current_dir > 0:
            up_streaks.append(current_streak)
        elif current_dir < 0:
            down_streaks.append(current_streak)
        
        features["pattern_max_up_streak"] = float(max(up_streaks)) if up_streaks else 0.0
        features["pattern_max_down_streak"] = float(max(down_streaks)) if down_streaks else 0.0
        features["pattern_avg_up_streak"] = float(np.mean(up_streaks)) if up_streaks else 0.0
        features["pattern_avg_down_streak"] = float(np.mean(down_streaks)) if down_streaks else 0.0
        
        # Direction balance
        up_count = np.sum(directions > 0)
        down_count = np. sum(directions < 0)
        total_moves = up_count + down_count
        features["pattern_up_ratio"] = float(up_count / total_moves) if total_moves > 0 else 0.5
        
        # ═══ CRYSTAL PATTERNS ═══
        
        # Symmetry crystals (V or inverted V)
        symmetry_count = 0
        for i in range(1, len(pips) - 1):
            sum_neighbors = abs(pips[i-1] + pips[i+1])
            total_neighbors = abs(pips[i-1]) + abs(pips[i+1])
            if total_neighbors > 0 and sum_neighbors < 0.5 * total_neighbors:
                symmetry_count += 1
        features["crystal_symmetry"] = float(symmetry_count)
        
        # Staircase crystals (consistent direction with similar steps)
        staircase_count = 0
        for i in range(2, len(pips)):
            same_dir = np.sign(pips[i]) == np.sign(pips[i-1]) == np.sign(pips[i-2])
            if same_dir and abs(pips[i]) > 0:
                step_diff = abs(pips[i] - pips[i-1])
                if step_diff < 0.3 * abs(pips[i]):
                    staircase_count += 1
        features["crystal_staircase"] = float(staircase_count)
        
        # Reversal crystals (strong reversal)
        reversal_count = 0
        for i in range(1, len(pips)):
            diff_sign = np.sign(pips[i]) != np.sign(pips[i-1])
            if diff_sign and abs(pips[i-1]) > 0:
                if abs(pips[i]) > 1.5 * abs(pips[i-1]):
                    reversal_count += 1
        features["crystal_reversal"] = float(reversal_count)
        
        # Acceleration crystals (increasing magnitude)
        accel_count = 0
        for i in range(2, len(pips)):
            increasing = abs(pips[i]) > abs(pips[i-1]) > abs(pips[i-2])
            same_dir = np.sign(pips[i]) == np.sign(pips[i-1])
            if increasing and same_dir:
                accel_count += 1
        features["crystal_acceleration"] = float(accel_count)
        
        # Deceleration crystals
        decel_count = 0
        for i in range(2, len(pips)):
            decreasing = abs(pips[i]) < abs(pips[i-1]) < abs(pips[i-2])
            same_dir = np.sign(pips[i]) == np.sign(pips[i-1])
            if decreasing and same_dir: 
                decel_count += 1
        features["crystal_deceleration"] = float(decel_count)
        
        # Total crystals
        features["crystal_total"] = float(
            symmetry_count + staircase_count + reversal_count +
            accel_count + decel_count
        )
        
        # ═══ VOLATILITY PATTERNS ═══
        abs_pips = np.abs(pips)
        
        if len(abs_pips) > 4:
            vol_threshold = np.percentile(abs_pips, 75)
            high_vol = abs_pips > vol_threshold
            
            vol_clusters = 0
            for i in range(1, len(high_vol)):
                if high_vol[i] and high_vol[i-1]:
                    vol_clusters += 1
            features["pattern_vol_clusters"] = float(vol_clusters)
            
            # Calm periods
            low_vol_threshold = np.percentile(abs_pips, 25)
            low_vol = abs_pips < low_vol_threshold
            calm_streaks = _find_line_lengths(low_vol. astype(int))
            features["pattern_max_calm_period"] = float(max(calm_streaks)) if calm_streaks else 0.0
        
    except Exception:
        pass
    
    return features


# ═══════════════════════════════════════════════════════════════
# ⚡ GRUPO 9: ULTRA NECROZMA FEATURES (Photon + Z-Crystal)
# Technical: Custom advanced features
# ═══════════════════════════════════════════════════════════════

def photon_features(prices, pips=None):
    """
    Photon Energy Features (Ultra Necrozma's Light)
    Technical: Custom energy and momentum features
    """
    features = {}
    
    if len(prices) < 10:
        return features
    
    prices = np.asarray(prices, dtype=np.float64)
    
    if pips is None:
        pips = np.diff(prices) * 10000
    else: 
        pips = np.asarray(pips, dtype=np. float64)
    
    if len(pips) < 5:
        return features
    
    try:
        abs_pips = np.abs(pips)
        
        # ═══ PHOTON ENERGY ═══
        energy = np.sum(abs_pips)
        features["photon_energy_total"] = float(energy)
        features["photon_energy_mean"] = float(np.mean(abs_pips))
        features["photon_energy_std"] = float(np.std(abs_pips))
        features["photon_energy_max"] = float(np.max(abs_pips))
        
        # Efficiency (net movement / total movement)
        net_movement = abs(np.sum(pips))
        efficiency = net_movement / (energy + 1e-10)
        features["photon_efficiency"] = float(efficiency)
        
        # ═══ LIGHT INTENSITY ═══
        intensity = np.std(pips)
        features["light_intensity"] = float(intensity)
        
        # Intensity trend (comparing halves)
        if len(pips) >= 10:
            mid = len(pips) // 2
            first_half = np.std(pips[:mid])
            second_half = np.std(pips[mid:])
            features["light_intensity_trend"] = float(second_half - first_half)
            features["light_intensity_ratio"] = float(second_half / (first_half + 1e-10))
        
        # ═══ WAVE-PARTICLE DUALITY ═══
        wave_component = abs(prices[-1] - prices[0]) * 10000
        particle_component = energy - wave_component
        
        features["wave_component"] = float(wave_component)
        features["particle_component"] = float(max(0, particle_component))
        
        total_component = wave_component + abs(particle_component)
        features["wave_particle_ratio"] = float(wave_component / (total_component + 1e-10))
        
        # ═══ QUANTUM COHERENCE ═══
        if len(pips) > 5:
            # Autocorrelation as coherence measure
            pips_centered = pips - np.mean(pips)
            autocorr = np.correlate(pips_centered, pips_centered, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            
            if autocorr[0] != 0:
                autocorr = autocorr / autocorr[0]
                features["quantum_coherence_lag1"] = float(autocorr[1]) if len(autocorr) > 1 else 0.0
                features["quantum_coherence_lag2"] = float(autocorr[2]) if len(autocorr) > 2 else 0.0
                
                # Coherence decay rate
                if len(autocorr) > 5:
                    decay_rate = np.polyfit(np.arange(5), autocorr[:5], 1)[0]
                    features["quantum_coherence_decay"] = float(decay_rate)
        
        # ═══ PHOTON DISPERSION ═══
        features["photon_dispersion"] = float(np.std(abs_pips))
        
        # Dispersion asymmetry (up vs down moves)
        up_moves = pips[pips > 0]
        down_moves = pips[pips < 0]
        
        if len(up_moves) > 0 and len(down_moves) > 0:
            up_std = np.std(up_moves)
            down_std = np.std(np.abs(down_moves))
            features["photon_dispersion_asymmetry"] = float(up_std - down_std)
        
    except Exception:
        pass
    
    return features


def z_crystal_features(prices, pips=None):
    """
    Z-Crystal Features (Ultra Necrozma's Z-Move Power)
    Technical: Advanced pattern and energy features
    """
    features = {}
    
    if len(prices) < 15:
        return features
    
    prices = np.asarray(prices, dtype=np.float64)
    
    if pips is None:
        pips = np.diff(prices) * 10000
    else:
        pips = np.asarray(pips, dtype=np.float64)
    
    if len(pips) < 10:
        return features
    
    try:
        abs_pips = np.abs(pips)
        
        # ═══ Z-POWER CHARGE ═══
        # Cumulative energy buildup
        cumulative_energy = np.cumsum(abs_pips)
        features["z_power_total"] = float(cumulative_energy[-1])
        
        # Energy acceleration
        energy_diff = np.diff(cumulative_energy)
        features["z_power_acceleration"] = float(np.mean(np.diff(energy_diff))) if len(energy_diff) > 1 else 0.0
        
        # ═══ Z-CRYSTAL RESONANCE ═══
        # Detect periodic patterns using autocorrelation peaks
        pips_centered = pips - np.mean(pips)
        autocorr = np.correlate(pips_centered, pips_centered, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        if autocorr[0] != 0:
            autocorr_norm = autocorr / autocorr[0]
            
            # Find peaks (potential resonance frequencies)
            peaks = []
            for i in range(2, len(autocorr_norm) - 1):
                if autocorr_norm[i] > autocorr_norm[i-1] and autocorr_norm[i] > autocorr_norm[i+1]:
                    if autocorr_norm[i] > 0.1:  # Minimum peak height
                        peaks.append((i, autocorr_norm[i]))
            
            if peaks:
                # Dominant resonance period
                dominant_peak = max(peaks, key=lambda x:  x[1])
                features["z_crystal_resonance_period"] = float(dominant_peak[0])
                features["z_crystal_resonance_strength"] = float(dominant_peak[1])
                features["z_crystal_resonance_count"] = float(len(peaks))
        
        # ═══ Z-MOVE POTENTIAL ═══
        # Measure of explosive move potential
        
        # Recent volatility vs historical
        if len(pips) >= 20:
            recent_vol = np.std(pips[-5:])
            historical_vol = np.std(pips[:-5])
            
            if historical_vol > 0:
                vol_ratio = recent_vol / historical_vol
                features["z_move_charge_ratio"] = float(vol_ratio)
                
                # Z-Move ready if volatility compressing (low ratio) then might explode
                features["z_move_ready"] = float(1.0 if vol_ratio < 0.5 else 0.0)
        
        # ═══ PRISMATIC SPECTRUM ═══
        # Analyze movement "colors" (different magnitude ranges)
        
        p10 = np.percentile(abs_pips, 10)
        p25 = np.percentile(abs_pips, 25)
        p50 = np.percentile(abs_pips, 50)
        p75 = np.percentile(abs_pips, 75)
        p90 = np.percentile(abs_pips, 90)
        
        # Spectrum bands
        infrared = np.sum(abs_pips <= p10) / len(abs_pips)    # Very small moves
        red = np.sum((abs_pips > p10) & (abs_pips <= p25)) / len(abs_pips)
        yellow = np.sum((abs_pips > p25) & (abs_pips <= p50)) / len(abs_pips)
        green = np.sum((abs_pips > p50) & (abs_pips <= p75)) / len(abs_pips)
        blue = np.sum((abs_pips > p75) & (abs_pips <= p90)) / len(abs_pips)
        ultraviolet = np.sum(abs_pips > p90) / len(abs_pips)  # Very large moves
        
        features["prism_infrared"] = float(infrared)
        features["prism_red"] = float(red)
        features["prism_yellow"] = float(yellow)
        features["prism_green"] = float(green)
        features["prism_blue"] = float(blue)
        features["prism_ultraviolet"] = float(ultraviolet)
        
        # Spectrum entropy (distribution of move sizes)
        spectrum = np.array([infrared, red, yellow, green, blue, ultraviolet])
        spectrum = spectrum[spectrum > 0]
        if len(spectrum) > 0:
            spectrum_entropy = -np.sum(spectrum * np. log2(spectrum + 1e-10))
            features["prism_entropy"] = float(spectrum_entropy)
        
        # ═══ ULTRA BURST POTENTIAL ═══
        # Detect conditions for extreme moves
        
        # Consecutive small moves (compression before expansion)
        small_move_threshold = p25
        small_moves = abs_pips < small_move_threshold
        compression_streaks = _find_line_lengths(small_moves.astype(int))
        
        if compression_streaks:
            features["ultra_burst_compression"] = float(max(compression_streaks))
            features["ultra_burst_potential"] = float(
                max(compression_streaks) * np.std(pips)
            )
        
    except Exception:
        pass
    
    return features


# ═══════════════════════════════════════════════════════════════
# 🎯 ADVANCED FEATURE EXTRACTION (Combined)
# ═══════════════════════════════════════════════════════════════

def extract_advanced_features(prices, pips=None):
    """
    Extract all advanced features from price series (Ultra Dimension Analysis)
    Technical: Combined feature extraction for advanced modules
    
    Args:
        prices: Price series (numpy array or list)
        pips: Optional pips/returns series
        
    Returns:
        dict:  All advanced features
    """
    features = {}
    
    prices = np.asarray(prices, dtype=np.float64)
    
    if len(prices) < 15:
        return features
    
    # Use pips if provided, otherwise calculate
    if pips is None: 
        pips = np.diff(prices) * 10000
    else:
        pips = np.asarray(pips, dtype=np.float64)
    
    # Phase Space
    features. update(phase_space_reconstruction(prices))
    
    # Recurrence (on pips for better results, limited size)
    if len(pips) >= 20:
        features.update(recurrence_features(pips))
    
    # Multifractal
    if len(prices) >= 64:
        features.update(multifractal_features(prices))
    
    # Patterns
    features.update(detect_patterns(prices, pips))
    
    # Photon (Ultra Necrozma)
    features.update(photon_features(prices, pips))
    
    # Z-Crystal (Ultra Necrozma)
    features.update(z_crystal_features(prices, pips))
    
    return features


# ═══════════════════════════════════════════════════════════════
# 🌟 FULL FEATURE EXTRACTION (Core + Advanced)
# ═══════════════════════════════════════════════════════════════

def extract_all_features(prices, pips=None):
    """
    Extract ALL features (Core + Advanced) - Ultra Necrozma Full Power
    Technical: Complete feature extraction pipeline
    
    Args:
        prices: Price series
        pips: Optional pips series
        
    Returns:
        dict: All 500+ features
    """
    # Import core features
    from features_core import extract_core_features
    
    features = {}
    
    # Core features
    features.update(extract_core_features(prices, pips))
    
    # Advanced features
    features.update(extract_advanced_features(prices, pips))
    
    return features


# ═══════════════════════════════════════════════════════════════
# 🎮 TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__": 
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║      ⚡ ULTRA NECROZMA ADVANCED FEATURES TEST ⚡             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Generate test data
    np.random.seed(42)
    n = 500
    prices = 1.10 + np.cumsum(np.random.randn(n) * 0.0001)
    pips = np.diff(prices) * 10000
    
    print(f"📊 Test data:  {n} prices, {len(pips)} pips")
    print()
    
    import time
    
    print("🔬 Testing individual feature groups:")
    print("─" * 50)
    
    # Phase Space
    start = time.time()
    phase_feat = phase_space_reconstruction(prices)
    print(f"   🌌 Phase Space: {len(phase_feat)} features ({time.time()-start:.3f}s)")
    
    # Recurrence
    start = time.time()
    rqa_feat = recurrence_features(pips)
    print(f"   🔄 RQA: {len(rqa_feat)} features ({time.time()-start:.3f}s)")
    
    # Multifractal
    start = time. time()
    mf_feat = multifractal_features(prices)
    print(f"   💎 Multifractal: {len(mf_feat)} features ({time.time()-start:.3f}s)")
    
    # Patterns
    start = time.time()
    pattern_feat = detect_patterns(prices, pips)
    print(f"   🔮 Patterns: {len(pattern_feat)} features ({time.time()-start:.3f}s)")
    
    # Photon
    start = time.time()
    photon_feat = photon_features(prices, pips)
    print(f"   ⚡ Photon:  {len(photon_feat)} features ({time.time()-start:.3f}s)")
    
    # Z-Crystal
    start = time.time()
    z_feat = z_crystal_features(prices, pips)
    print(f"   💎 Z-Crystal: {len(z_feat)} features ({time.time()-start:.3f}s)")
    
    print()
    
    # Test combined
    print("⚡ Testing combined advanced extraction:")
    print("─" * 50)
    
    start = time.time()
    all_advanced = extract_advanced_features(prices, pips)
    total_time = time.time() - start
    
    print(f"   ✅ Total advanced features: {len(all_advanced)}")
    print(f"   ⏱️  Time: {total_time:.3f}s")
    print()
    
    # Show some key features
    print("🎯 Key feature values:")
    print("─" * 50)
    key_features = [
        "correlation_dimension", "recurrence_rate", "determinism",
        "multifractal_width", "crystal_total", "photon_efficiency",
        "z_crystal_resonance_strength", "wave_particle_ratio"
    ]
    for key in key_features:
        if key in all_advanced:
            print(f"   {key}: {all_advanced[key]:.4f}")
    
    print()
    print("✅ Advanced features test complete!")