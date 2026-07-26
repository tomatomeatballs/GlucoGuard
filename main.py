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
# Plotting Font Settings (Prevents fallback issues, favors English)
# -----------------------------------------------------------
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def process_dataset(file_path, horizon_label):
    """
    Main function to process a single dataset.
    Pipeline: Load Data -> Global Parameter Optimization -> VMD Decomposition -> Component-wise Modeling -> Results Aggregation -> Plotting
    """
    print(f"\n{'#'*60}")
    print(f"Processing Scenario: {horizon_label}")
    print(f"File Source: {file_path}")
    print(f"{'#'*60}")
    
    # =======================================================
    # 1. Data Loading and Preprocessing
    # =======================================================
    try:
        # Read Excel assuming no header (header=None) if the first row contains data
        df = pd.read_excel(file_path, header=None)
    except Exception as e:
        print(f"[Error] Failed to load {file_path}: {e}")
        return

    rows, cols = df.shape
    print(f"Data Loaded. Shape: ({rows}, {cols})")
    
    # Logical check: the last column is the target glucose value, preceding columns are features
    if cols < 2:
        print("[Error] Data must have at least 2 columns (Feature + Target).")
        return

    # Automatically derive the input sequence length (look_back/kim)
    # Rationale: 15 mins (4 cols) = 3 steps + 1; 30 mins (7 cols) = 6 steps + 1; 50 mins (11 cols) = 10 steps + 1
    look_back = cols - 1
    print(f"Configured Input Sequence Length (Look-back): {look_back} steps")
    
    # Separate features and target
    # X_aux: Original auxiliary features (first N-1 columns)
    # target_series: Original glucose signal (last column)
    X_aux = df.iloc[:, :-1].values 
    full_data_raw = df.values # Complete raw data used for global optimization
    
    target_series = df.iloc[:, -1].values
    
    # Simple data cleaning
    try:
        target_series = pd.to_numeric(target_series, errors='coerce')
        if np.isnan(target_series).any():
            print("Warning: NaNs found in target. Filling with forward fill.")
            target_series = pd.Series(target_series).ffill().values
    except:
        print("[Error] Non-numeric data in target column.")
        return

    # =======================================================
    # 2. Global NOA Optimization (Global Optimization)
    # Purpose: Search for optimal BiLSTM hyperparameters on raw data to apply to all components
    # =======================================================
    print(f"\n[{horizon_label}] Step 2: Global NOA Parameter Optimization...")
    
    # Parameter bounds [HiddenUnits, MaxEpochs, LearningRate]
    lb = [100, 100, 0.001]
    ub = [200, 200, 0.02]
    # Note: For faster experimental validation, iterations are set to 5. Recommended configuration for production: pop=5, max_iter=20
    pop_size = 5 
    max_iter_noa = 5 
    
    # Define global fitness function
    def fitness_func_global(params):
        # Evaluate performance using the full raw dataset
        return train_evaluate_bilstm(params, full_data_raw, kim=look_back, zim=1, device='cpu')
    
    # Run optimization
    noa = NOA(fitness_func_global, dim=3, lb=lb, ub=ub, search_agents_no=pop_size, max_iter=max_iter_noa)
    best_score, best_pos, conv_curve = noa.optimize()
    
    print(f"[{horizon_label}] Optimal Params Found:")
    print(f"  > Hidden Units: {int(best_pos[0])}")
    print(f"  > Epochs:       {int(best_pos[1])}")
    print(f"  > Learning Rate:{best_pos[2]:.5f}")
    print(f"  > Best RMSE (Global): {best_score:.4f}")

    # =======================================================
    # 3. VMD Signal Decomposition
    # Purpose: Decompose the non-stationary target glucose signal into K IMF components
    # =======================================================
    print(f"\n[{horizon_label}] Step 3: Running VMD Decomposition...")
    alpha = 2000
    tau = 0
    K = 5
    DC = 0
    init = 1
    tol = 1e-7
    
    # u represents the decomposed component matrix (K x N)
    u, u_hat, omega = VMD(target_series, alpha, tau, K, DC, init, tol)
    
    # Plot decomposition results
    plt.figure(figsize=(10, 8))
    plt.subplot(K+1, 1, 1)
    plt.plot(target_series, 'b')
    plt.title(f"Original Signal ({horizon_label})")
    for i in range(K):
        plt.subplot(K+1, 1, i+2)
        plt.plot(u[i, :], 'g')
        plt.ylabel(f"IMF {i+1}")
    plt.tight_layout()
    plot_dir = os.path.join("results", "plots")
    os.makedirs(plot_dir, exist_ok=True)
    plt.savefig(os.path.join(plot_dir, f"VMD_Decomposition_{horizon_label}.png"))
    plt.close()
    print("VMD plots saved.")

    # =======================================================
    # 4. Component-wise Modeling
    # Core Logic: For each IMF component, construct [Original Features + Current IMF Component] as the inputs for prediction
    # =======================================================
    print(f"\n[{horizon_label}] Step 4: Component-wise BiLSTM Prediction...")
    
    total_y_test = None
    total_y_pred = None
    
    for i in range(K):
        # Prepare data for the current component
        # Extract the i-th IMF component (serving as both target and partial feature for this round)
        imf_col = u[i, :].reshape(-1, 1)
        
        # Ensure row counts match (VMD decomposition should match lengths, using min() as a failsafe)
        min_len = min(X_aux.shape[0], imf_col.shape[0])
        
        # Construct hybrid dataset: original auxiliary variables followed by the current IMF column
        # This strictly mirrors the MATLAB logic: X_imf=[X(:,1:end-1) imf(d,:)']
        component_dataset = np.hstack((X_aux[:min_len, :], imf_col[:min_len, :]))
        
        # Predict using global optimal parameters
        # predict_final handles train/test splitting internally and returns ground truth (y_test) and predictions (y_pred) for the test set
        y_test_imf, y_pred_imf = predict_final(best_pos, component_dataset, kim=look_back, zim=1, device='cpu')
        
        # Accumulate results
        if total_y_test is None:
            total_y_test = np.zeros_like(y_test_imf)
            total_y_pred = np.zeros_like(y_pred_imf)
        
        # Shape alignment protection (prevents 1-row clipping discrepancies between components)
        common_len = min(len(total_y_test), len(y_test_imf))
        total_y_test = total_y_test[:common_len] + y_test_imf[:common_len]
        total_y_pred = total_y_pred[:common_len] + y_pred_imf[:common_len]
        
        print(f"  > IMF {i+1}/{K} processed.")

    # =======================================================
    # 5. Error Evaluation and Visualization
    # =======================================================
    mae, rmse, mape, error = calculate_errors(total_y_test.flatten(), total_y_pred.flatten())
    print(f"\n{'='*40}")
    