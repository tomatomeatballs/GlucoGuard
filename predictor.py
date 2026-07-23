"""
GlucoGuard - VMD-NOA-BiLSTM Predictor Module
Loads pre-trained models, converts raw 2-col Excel data to sliding-window format,
and runs inference for 15min / 30min / 50min glucose predictions.
"""
import os
import pickle
import numpy as np
import pandas as pd
import torch
from vmdpy import VMD
from src.models.lstm import BiLSTMModel


class GlucosePredictor:
    """
    Loads three horizon-specific VMD-NOA-BiLSTM model packages and
    predicts the next glucose value for each prediction horizon.
    """

    HORIZONS = ['15min', '30min', '50min']

    def __init__(self, model_dir='models'):
        self.horizon_models = {}
        for horizon in self.HORIZONS:
            pkl_path = os.path.join(model_dir, f'vmd_noa_bilstm_{horizon}.pkl')
            if not os.path.exists(pkl_path):
                raise FileNotFoundError(
                    f"Model file not found: {pkl_path}. "
                    f"Please run VMD_NOA_BILSTM.py to generate trained models."
                )
            with open(pkl_path, 'rb') as f:
                self.horizon_models[horizon] = pickle.load(f)

    # ------------------------------------------------------------------
    # Safe VMD wrapper
    # ------------------------------------------------------------------
    @staticmethod
    def _safe_vmd(signal, vmd_params):
        """
        Run VMD with fallback: if the default parameters cause a
        division-by-zero (common with short / near-constant signals),
        retry with tiny noise injection to stabilise the frequency update.
        """
        try:
            with np.errstate(all='raise'):
                u, _, _ = VMD(
                    signal,
                    vmd_params['alpha'], vmd_params['tau'], vmd_params['K'],
                    vmd_params['DC'], vmd_params['init'], vmd_params['tol']
                )
            return u
        except (FloatingPointError, ZeroDivisionError):
            # Fallback: inject tiny noise proportional to signal std
            sig_std = np.std(signal) if np.std(signal) > 1e-6 else 1e-4
            noisy = signal + np.random.randn(len(signal)) * sig_std * 1e-4
            with np.errstate(all='raise'):
                u, _, _ = VMD(
                    noisy,
                    vmd_params['alpha'], vmd_params['tau'], vmd_params['K'],
                    vmd_params['DC'], vmd_params['init'], vmd_params['tol']
                )
            return u

    # ------------------------------------------------------------------
    # Single-horizon prediction
    # ------------------------------------------------------------------
    def predict_single(self, horizon_label, X_aux, target_series):
        """
        Run inference for one horizon.

        Parameters
        ----------
        horizon_label : str  - '15min', '30min', or '50min'
        X_aux : np.ndarray, shape (M, 10)  - sliding-window glucose history
        target_series : np.ndarray, shape (M,)  - column-10 glucose sequence

        Returns
        -------
        float  - predicted next glucose value
        """
        package = self.horizon_models[horizon_label]
        look_back = package['look_back']
        vmd_params = package['vmd_params']

        # ---- Signal validation ----
        ts = target_series.astype(np.float64).copy()
        if len(ts) < 10:
            raise ValueError(
                f"After window construction, only {len(ts)} data points available. "
                f"VMD needs at least 10 points. "
                f"Please upload an Excel with at least 19 glucose readings."
            )
        if np.std(ts) < 1e-8:
            raise ValueError(
                "Glucose values are constant - no variation to model. "
                "Please check the uploaded data."
            )

        # ---- 1. VMD decomposition (with fallback) ----
        u = self._safe_vmd(ts, vmd_params)          # (K, M)

        K = vmd_params['K']
        pred_imfs = []

        for i in range(K):
            imf_model = package['models'][i]

            # 2. Build component_dataset: [X_aux + this IMF]
            imf_col = u[i, :].reshape(-1, 1)                # (M, 1)
            min_len = min(X_aux.shape[0], imf_col.shape[0])
            component_dataset = np.hstack((
                X_aux[:min_len, :],
                imf_col[:min_len, :]
            ))                                                # (M, 11)

            if component_dataset.shape[0] < look_back:
                raise ValueError(
                    f"Insufficient data rows ({component_dataset.shape[0]}) "
                    f"for look_back={look_back}."
                )

            # 3. Last `look_back` rows -> flatten -> single sample
            last_window = component_dataset[-look_back:, :]   # (10, 11)
            flat_input = last_window.flatten().reshape(1, -1) # (1, 110)

            # 4. Scale (guard against zero-range)
            if np.ptp(flat_input) < 1e-10:
                flat_input = flat_input + np.random.randn(*flat_input.shape) * 1e-8
            X_scaled = imf_model['scaler_X'].transform(flat_input)

            # 5. Reshape for BiLSTM: (batch=1, seq_len=1, features)
            X_tensor = torch.FloatTensor(X_scaled).reshape(1, 1, -1)

            # 6. Build model and load weights
            model = BiLSTMModel(imf_model['input_size'], imf_model['hidden_size'])
            model.load_state_dict(imf_model['state_dict'])
            model.eval()

            # 7. Forward pass
            with torch.no_grad():
                pred_scaled = model(X_tensor).cpu().numpy()

            # 8. Inverse scale
            pred = imf_model['scaler_y'].inverse_transform(pred_scaled)
            pred_imfs.append(float(pred[0, 0]))

        # 9. Sum all IMF predictions -> final glucose
        return sum(pred_imfs)

    # ------------------------------------------------------------------
    # Multi-horizon prediction
    # ------------------------------------------------------------------
    def predict_all_horizons(self, X_aux, target_series):
        """
        Predict for all three horizons.

        Returns
        -------
        dict  - {'15min': float, '30min': float, '50min': float}
        """
        results = {}
        for horizon in self.HORIZONS:
            results[horizon] = self.predict_single(horizon, X_aux, target_series)
        return results

    # ------------------------------------------------------------------
    # Excel conversion
    # ------------------------------------------------------------------
    @staticmethod
    def excel_to_11col(df_2col):
        """
        Convert a 2-column Excel DataFrame (glucose_value, timestamp)
        to the 11-column sliding-window format expected by the model.

        Parameters
        ----------
        df_2col : pd.DataFrame with 2 columns [glucose_value, timestamp]

        Returns
        -------
        X_aux : np.ndarray, shape (N-9, 10)
        target_series : np.ndarray, shape (N-9,)
        raw_series : np.ndarray, shape (N,)
        timestamps : np.ndarray, shape (N,)
        """
        df = df_2col.copy()
        df.columns = ['glucose', 'timestamp']
        df = df.sort_values('timestamp').reset_index(drop=True)

        raw_series = df['glucose'].values.astype(float)
        timestamps = df['timestamp'].values
        n = len(raw_series)

        if n < 10:
            raise ValueError(
                f"Need at least 10 glucose readings for sliding-window construction. "
                f"Only {n} provided."
            )

        # Build 11-column sliding window: [glu(t-9), ..., glu(t), glu(t)]
        rows = []
        for i in range(9, n):
            row = list(raw_series[i - 9:i + 1]) + [raw_series[i]]
            rows.append(row)

        df_11col = pd.DataFrame(rows)
        X_aux = df_11col.iloc[:, :-1].values          # (N-9, 10)
        target_series = df_11col.iloc[:, -1].values    # (N-9,)

        return X_aux, target_series, raw_series, timestamps
