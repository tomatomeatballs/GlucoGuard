import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import sys
from vmdpy import VMD
from src.optimization.noa import NOA
from src.fitness import train_evaluate_bilstm, predict_final
from src.utils.metrics import calculate_errors, clarke_error_grid

# -----------------------------------------------------------
# Plotting Font Configuration (Prioritize Arial for stability)
# -----------------------------------------------------------
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def process_dataset(file_path, horizon_label):
    """
    Main function to process a single dataset.
    Pipeline: Load Data -> Global Parameters Optimization -> VMD Decomposition 
              -> Component-wise Modeling -> Results Aggregation -> Visualization
    """
    print(f"\n{'#'*60}")
    print(f"Processing Scenario: {horizon_label}")
    print(f"File Source: {file_path}")
    print(f"{'#'*60}")
    
    # =======================================================
    # 1. Data Loading and Preprocessing
    # =======================================================
    try:
        # Read Excel assuming no header row (header=None) if data starts at row 1
        df = pd.read_excel(file_path, header=None)
    except Exception as e:
        print(f"[Error] Failed to load {file_path}: {e}")
        return

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
    
    for i in range(K):
        # Extract the i-th structural IMF vector
        imf_col = u[i, :].reshape(-1, 1)
        
        # Array shape alignment validation slice
        min_len = min(X_aux.shape[0], imf_col.shape[0])
        
        # Merge structural base features side by side with the active variant component
        component_dataset = np.hstack((X_aux[:min_len, :], imf_col[:min_len, :]))
        
        # Invoke forecasting pipeline using the globally optimized hyperparameters
        # predict_final partitions train/test datasets internally, outputting test predictions
        y_test_imf, y_pred_imf = predict_final(best_pos, component_dataset, kim=look_back, zim=1, device='cpu')
        
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
    
    # Save performance evaluation metrics to CSV
    results_path = os.path.join("results", f"metrics_{horizon_label}.csv")
    pd.DataFrame({
        'Metric': ['RMSE', 'MAE', 'MAPE'],
        'Value': [rmse, mae, mape]
    }).to_csv(results_path, index=False)

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
    
    output_excel_path = os.path.join("results", f"Final_Prediction_{horizon_label}.xlsx")
    
    print(f"   > Writing Excel to: {os.path.abspath(output_excel_path)}")
    result_df_clean.to_excel(output_excel_path, index=False)
    print(f"   > success! Saved {horizon_label} Excel file.")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    
    # Ensure standard evaluation paths are mounted
    os.makedirs(os.path.join("results", "plots"), exist_ok=True)
    
    # Systematically search for target tracking matrices using localized 'min' markers
    files = glob.glob(os.path.join(data_dir, "*min*.xlsx"))
    
    if not files:
        print(f"[Warning] No excel files matching '*min*.xlsx' found in {data_dir}")
        print("Please check your file names and location.")
        return
        
    print(f"Found {len(files)} datasets to process.")
    
    for f_path in files:
        filename = os.path.basename(f_path)
        try:
            # Isolate base tracking labels: "15min_data.xlsx" -> "15min"
            label = filename.split('_')[0] 
        except:
            label = filename
            
        process_dataset(f_path, label)
        
    print("\nAll tasks completed successfully.")

if __name__ == "__main__":
    main()