import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import sys
import pickle
import torch
from vmdpy import VMD
from src.optimization.noa import NOA
from src.fitness import train_evaluate_bilstm, predict_final
from src.utils.metrics import calculate_errors, clarke_error_grid

# [KYLE] 2026-07-24 -- DATABASE INTEGRATION START
# This script used to be a standalone subprocess that only knew about the local
# `data/` and `results/` folders. Problem: two users training at the same time would
# both write to the SAME local file (e.g. data/15min_data.xlsx), overwriting each
# other -- this only works for one person on one laptop, not once deployed with real
# users. Fix: this subprocess now takes a --user-id argument (passed by app.py when it
# launches the subprocess) and reads its 3 training files + writes its 6 result files
# straight from/to the `user_files` table in glucoguard.db, scoped to that user_id.
# No more shared local filenames -- everyone's data stays in their own DB rows.
import argparse
import io
from db import get_latest_user_file_content, save_user_file
# [KYLE] DATABASE INTEGRATION END (imports)

# -----------------------------------------------------------
# Plotting Font Configuration (Prioritize Arial for stability)
# -----------------------------------------------------------
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# [KYLE] 2026-07-24 -- process_dataset() used to take a local `file_path` and read it
# with pd.read_excel(file_path). It now takes an already-loaded DataFrame (`df`) plus
# the `user_id` it belongs to, because the caller (main(), below) now loads that
# DataFrame straight out of the database instead of off disk. Everything from Step 2
# onwards is UNCHANGED algorithm logic -- only how data comes IN (top of this function)
# and how results go OUT (Steps 5-6, near the bottom) were touched.
def process_dataset(df, horizon_label, user_id):
    """
    Main function to process a single dataset.
    Pipeline: Load Data -> Global Parameters Optimization -> VMD Decomposition
              -> Component-wise Modeling -> Results Aggregation -> Visualization
    """
    print(f"\n{'#'*60}")
    print(f"Processing Scenario: {horizon_label}")
    print(f"User ID: {user_id}")
    print(f"{'#'*60}")

    # =======================================================
    # 1. Data Validation (data itself now arrives already-loaded from the database)
    # =======================================================
    rows, cols = df.shape
    print(f"Data Loaded. Shape: ({rows}, {cols})")
    
    # Logical Check: Last column is Target Glucose, preceding columns are Features
    if cols < 2:
        print("[Error] Data must have at least 2 columns (Feature + Target).")
        return

    # Automatically derive the input sequence length (look-back window)
    # Mapping rule: 15-min (4 cols) = 3 steps + 1; 30-min (7 cols) = 6 steps + 1; 50-min (11 cols) = 10 steps + 1
    look_back = cols - 1
    print(f"Configured Input Sequence Length (Look-back): {look_back} steps")
    
    # Isolate independent features and target array
    # X_aux: Raw auxiliary features (First N-1 columns)
    # full_data_raw: Entire matrix utilized for structural global optimization
    X_aux = df.iloc[:, :-1].values 
    full_data_raw = df.values 
    
    target_series = df.iloc[:, -1].values
    
    # Basic data cleaning and parsing
    try:
        target_series = pd.to_numeric(target_series, errors='coerce')
        if np.isnan(target_series).any():
            print("Warning: NaNs found in target series. Filling with forward fill (ffill).")
            target_series = pd.Series(target_series).fillna(method='ffill').values
    except:
        print("[Error] Non-numeric data encountered in the target column.")
        return

    # =======================================================
    # 2. Global NOA Hyperparameter Optimization
    # Objective: Identify ideal BiLSTM structural constants on raw data matrices
    # =======================================================
    print(f"\n[{horizon_label}] Step 2: Global NOA Parameter Optimization...")
    
    # Structural search boundary spaces: [HiddenUnits, MaxEpochs, LearningRate]
    lb = [100, 100, 0.001]
    ub = [200, 200, 0.02]
    
    # Current testing setup optimized for velocity (Iterations = 5)
    # Production Suggestion: pop_size = 5, max_iter_noa = 20
    pop_size = 5 
    max_iter_noa = 5 
    
    # Define optimization wrapper metric
    def fitness_func_global(params):
        # Evaluate model configuration on full scale raw tracking instances
        return train_evaluate_bilstm(params, full_data_raw, kim=look_back, zim=1, device='cpu')
    
    # Initialize and execute Nutcracker Optimization Algorithm sequence
    noa = NOA(fitness_func_global, dim=3, lb=lb, ub=ub, search_agents_no=pop_size, max_iter=max_iter_noa)
    best_score, best_pos, conv_curve = noa.optimize()
    
    print(f"[{horizon_label}] Optimal Params Found:")
    print(f"   > Hidden Units:  {int(best_pos[0])}")
    print(f"   > Epochs:        {int(best_pos[1])}")
    print(f"   > Learning Rate: {best_pos[2]:.5f}")
    print(f"   > Best RMSE (Global Target): {best_score:.4f}")

    # =======================================================
    # 3. Variational Mode Decomposition (VMD)
    # Objective: Deconstruct non-stationary glucose waves into K distinct IMFs
    # =======================================================
    print(f"\n[{horizon_label}] Step 3: Running VMD Decomposition...")
    alpha = 2000
    tau = 0
    K = 5
    DC = 0
    init = 1
    tol = 1e-7
    
    # u represents the decomposed sub-signals matrix (K modes x N points)
    u, u_hat, omega = VMD(target_series, alpha, tau, K, DC, init, tol)

    # =======================================================
    # 4. Component-wise Deep Modeling
    # Core Logic: Model each IMF mode independently by passing [Aux_Features + Current_IMF]
    # =======================================================
    print(f"\n[{horizon_label}] Step 4: Component-wise BiLSTM Prediction...")
    
    total_y_test = None
    total_y_pred = None
    imf_models = []  # Store model artifacts for each IMF

    for i in range(K):
        # Extract the i-th structural IMF vector
        imf_col = u[i, :].reshape(-1, 1)

        # Array shape alignment validation slice
        min_len = min(X_aux.shape[0], imf_col.shape[0])

        # Merge structural base features side by side with the active variant component
        component_dataset = np.hstack((X_aux[:min_len, :], imf_col[:min_len, :]))

        # Invoke forecasting pipeline using the globally optimized hyperparameters
        # predict_final partitions train/test datasets internally, outputting test predictions
        result = predict_final(best_pos, component_dataset, kim=look_back, zim=1, device='cpu')
        y_test_imf = result['y_test']
        y_pred_imf = result['y_pred']

        # Store model artifacts for later persistence
        imf_models.append({
            'state_dict': {k: v.cpu().clone() for k, v in result['model_state'].items()},
            'scaler_X': result['scaler_X'],
            'scaler_y': result['scaler_y'],
            'input_size': result['input_size'],
            'hidden_size': result['hidden_size'],
        })

        # Aggregate signal fragments back onto the tracking metrics matrix
        if total_y_test is None:
            total_y_test = np.zeros_like(y_test_imf)
            total_y_pred = np.zeros_like(y_pred_imf)

        # Matrix slice padding boundary protection
        common_len = min(len(total_y_test), len(y_test_imf))
        total_y_test = total_y_test[:common_len] + y_test_imf[:common_len]
        total_y_pred = total_y_pred[:common_len] + y_pred_imf[:common_len]

        print(f"   > IMF {i+1}/{K} processed.")

    # =======================================================
    # 5. Error Metrics Evaluation and Persistence
    # =======================================================
    mae, rmse, mape, error = calculate_errors(total_y_test.flatten(), total_y_pred.flatten())
    print(f"\n{'='*40}")
    print(f"FINAL RESULTS ({horizon_label})")
    print(f"{'='*40}")
    print(f"   RMSE: {rmse:.4f}")
    print(f"   MAE:  {mae:.4f}")
    print(f"   MAPE: {mape:.2f}%")
    
    # [KYLE] 2026-07-24 -- was: pd.DataFrame(...).to_csv(results_path) writing straight
    # to the shared local results/ folder. Now: build the CSV in memory (io.StringIO
    # instead of a real file on disk) and save those bytes into this user's own row in
    # user_files, via the same save_user_file() the rest of the app already uses for the
    # Management page. file_type='metrics_{horizon}' matches what app.py's Integrated
    # Performance Analytics section now reads back (see app.py changes).
    metrics_csv_buffer = io.StringIO()
    pd.DataFrame({
        'Metric': ['RMSE', 'MAE', 'MAPE'],
        'Value': [rmse, mae, mape]
    }).to_csv(metrics_csv_buffer, index=False)
    save_user_file(
        user_id, f'metrics_{horizon_label}', f'metrics_{horizon_label}.csv',
        metrics_csv_buffer.getvalue().encode('utf-8')
    )
    print(f"   > Metrics saved to database (user_id={user_id}, file_type=metrics_{horizon_label}).")

    # =======================================================
    # 6. Save Extended Dataset (Original Array + Prediction Features)
    # Objective: Concat predictions onto structural evaluation points
    # =======================================================
    print(f"[{horizon_label}] Saving extended dataset with predictions...")
    
    kim = look_back
    zim = 1
    num_samples = len(target_series)
    
    # Compute actual usable sequence boundaries matching LSTM layers
    len_samples_lstm = num_samples - kim - zim + 1
    
    # Define training vs testing data split configuration index (60/40)
    train_size = int(0.6 * len_samples_lstm)
    
    # Locate exact index tracking match relative to the primary array
    start_idx_original = train_size + kim + zim - 1
    
    # Instantiate empty NaN baseline tracking arrays
    full_predictions = np.full(num_samples, np.nan)
    
    pred_len = len(total_y_pred)
    end_idx_original = start_idx_original + pred_len
    
    # Dimension padding array boundary enforcement
    if end_idx_original > num_samples:
         end_idx_original = num_samples
         full_predictions[start_idx_original : end_idx_original] = total_y_pred.flatten()[:end_idx_original - start_idx_original]
    else:
         full_predictions[start_idx_original : end_idx_original] = total_y_pred.flatten()
         
    # Append localized tracking arrays onto structural tables
    result_df = df.copy()
    result_df['Predicted_Glucose'] = full_predictions
    
    # Filter training slices by systematically dropping NaN observations, isolating pure test records
    result_df_clean = result_df.dropna(subset=['Predicted_Glucose'])
    
    # [KYLE] 2026-07-24 -- was: result_df_clean.to_excel(output_excel_path) writing to
    # the shared local results/ folder (this is exactly the file two concurrent users
    # would have collided on). Now: build the Excel file in memory (io.BytesIO instead
    # of a real path) and save it into this user's own row in user_files. Same pattern
    # as the metrics CSV above -- see save_user_file() in db.py.
    excel_buffer = io.BytesIO()
    result_df_clean.to_excel(excel_buffer, index=False)
    save_user_file(
        user_id, f'prediction_{horizon_label}', f'Final_Prediction_{horizon_label}.xlsx',
        excel_buffer.getvalue()
    )
    print(f"   > success! Saved {horizon_label} prediction to database (user_id={user_id}).")

    # =======================================================
    # 7. Save Trained Model Package (.pkl) for Deployment
    # =======================================================
    # [KYLE] 2026-07-24 -- deliberately LEFT ON LOCAL DISK, not moved to the database
    # like Steps 5-6 above. Reasoning: the 10-files-per-user spec (raw upload + 3
    # training files + 6 result files) never included the trained model file -- only
    # the *data* needed per-user isolation to stop users colliding on the same
    # filename. The model itself stays one shared/global set of weights (whoever
    # trains most recently updates it for everyone), same as it already behaved before
    # this change. Making models per-user too would mean storing multi-MB blobs per
    # user and loading them on every prediction -- real cost for no requirement asking
    # for it. If "each user gets their own personalized model" is wanted later, this is
    # the block to change (same save_user_file() pattern as Steps 5-6, just bigger blobs).
    model_package = {
        'best_params': best_pos,
        'vmd_params': {'alpha': alpha, 'tau': tau, 'K': K, 'DC': DC, 'init': init, 'tol': tol},
        'look_back': look_back,
        'models': imf_models,
    }

    model_dir = 'models'
    os.makedirs(model_dir, exist_ok=True)
    pkl_path = os.path.join(model_dir, f'vmd_noa_bilstm_{horizon_label}.pkl')
    with open(pkl_path, 'wb') as f:
        pickle.dump(model_package, f)
    print(f"   > Model saved to: {os.path.abspath(pkl_path)}")


# [KYLE] 2026-07-24 -- main() rewritten for DB-driven multi-user training.
# BEFORE: glob.glob('data/*min*.xlsx') -- grabs WHATEVER training files happen to be
#         sitting in the local data/ folder, no idea whose they are. Two users training
#         "at the same time" (or even minutes apart, before someone re-uploads) would
#         silently read/overwrite each other's files.
# AFTER:  takes --user-id on the command line (app.py passes st.session_state.user_id
#         when it launches this script -- see the subprocess.Popen cmd list in app.py's
#         model_training_page()), and looks up exactly that user's 3 newest training
#         files in the database via get_latest_user_file_content(). No shared filenames
#         left in this path at all -- every user's training run is isolated by user_id.
def main():
    parser = argparse.ArgumentParser(description="Train VMD-NOA-BiLSTM models for one user's uploaded data.")
    parser.add_argument('--user-id', type=int, required=True, help="The users.id this training run belongs to.")
    args = parser.parse_args()
    user_id = args.user_id

    print(f"Starting training pipeline for user_id={user_id} (reading from database)...")

    horizons = ['15min', '30min', '50min']
    processed_any = False

    for horizon_label in horizons:
        file_type = f'{horizon_label}_data'
        # Pull this user's newest 15min_data / 30min_data / 50min_data straight out of
        # user_files -- no local file path involved at all.
        file_name, file_content = get_latest_user_file_content(user_id, file_type)

        if file_content is None:
            print(f"[Warning] No '{file_type}' found in the database for user_id={user_id}. "
                  f"Skipping {horizon_label} (complete Step 2 in Model Training first).")
            continue

        # io.BytesIO lets pandas read the DB-stored bytes exactly as if they were a
        # real file on disk -- this is the trick that avoids ever writing to local disk.
        df = pd.read_excel(io.BytesIO(file_content), header=None)
        print(f"Loaded '{file_name}' for user_id={user_id}, horizon={horizon_label}. Shape: {df.shape}")

        process_dataset(df, horizon_label, user_id)
        processed_any = True

    if not processed_any:
        print(f"[Warning] No training data found in the database for user_id={user_id} at all. "
              f"Nothing was processed.")
        return

    print("\nAll tasks completed successfully.")

if __name__ == "__main__":
    main()