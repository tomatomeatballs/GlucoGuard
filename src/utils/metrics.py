import numpy as np

def calculate_errors(y_true, y_pred):
    """
    Calculate performance error metrics: RMSE, MAE, MAPE
    """
    error = y_pred - y_true
    rmse = np.sqrt(np.mean(error**2))
    mae = np.mean(np.abs(error))
    
    # Prevent division by zero scenarios
    with np.errstate(divide='ignore', invalid='ignore'):
        mape = np.mean(np.abs(error / y_true)) * 100
        mape = np.nan_to_num(mape) # Handle potential nans if y_true has zeros

    return mae, rmse, mape, error

def clarke_error_grid(ref_values, pred_values, title_string="Clarke Error Grid Analysis", filename="Clarke_Error_Grid.png"):
    """
    Generate and save a Clarke Error Grid analysis plot
    """
    import matplotlib.pyplot as plt
    
    # Force alignment to flattened numpy arrays
    ref_values = np.array(ref_values).flatten()
    pred_values = np.array(pred_values).flatten()

    assert len(ref_values) == len(pred_values), "Unequal length arrays passed to metric evaluator"

    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Scatter plot initialization
    ax.scatter(ref_values, pred_values, color='blue', s=8, alpha=0.6, label='Prediction Points')
    
    # Set axis limits (standard glucose range mg/dL converts to approx 0-25 mmol/L if mmol, 
    # but Clarke is usually defined for mg/dL (0-400). 
    # VAE data looks like mmol/L (values ~5-8). 
    # Need to handle unit scale or standard lines. 
    # If data is < 30, assume mmol/L and multiply by 18 for plotting, then divide back labels?
    # Or just plot relative lines. Clarke regions are relative percentages mostly.
    # The standard graph is 0-400 mg/dL.
    # If using mmol/L, limits are 0-22.2.
    
    # Check max value boundary to automatically infer unit configurations
    max_val = max(np.max(ref_values), np.max(pred_values))
    if max_val < 30: # Assume mmol/L and convert to mg/dL for standardized tracking lines
        conversion = 18.0182
        units = "mmol/L"
        # Scale for plotting logic (Clarke is defined on mg/dL scale)
        ref_plot = ref_values * conversion
        pred_plot = pred_values * conversion
        limit = 400
    else:
        units = "mg/dL"
        ref_plot = ref_values
        pred_plot = pred_values
        limit = 400

    # Clear previous scatter and re-plot with scaled values if needed for correct region lines
    ax.clear()
    ax.scatter(ref_plot, pred_plot, color='blue', s=8, alpha=0.6, label='Prediction')
    ax.set_title(title_string + f" ({units})")
    ax.set_xlabel(f'Reference Glucose ({units})')
    ax.set_ylabel(f'Predicted Glucose ({units})')
    ax.set_xlim(0, limit)
    ax.set_ylim(0, limit)
    ax.set_aspect('equal')

    # Plot Reference Lines
    # 1. Perfect Line (45 degree target vector)
    ax.plot([0, limit], [0, limit], 'k--', label='Perfect')

    # Zone A Lines ( +/- 20% acceptable boundaries )
    # Upper boundary: y = x + 0.2x = 1.2x
    # Lower boundary: y = x - 0.2x = 0.8x
    # Standard simplified definition configuration setup:
    ax.plot([0, limit], [0, limit*1.2], 'g-', linewidth=1) # Upper A
    ax.plot([0, limit], [0, limit*0.8], 'g-', linewidth=1) # Lower A
    
    # Add textual zone annotations to canvas
    ax.text(limit*0.5, limit*0.5, 'A', fontsize=20, color='green')
    
    # Complete chart presentation and disk save execution
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.savefig(filename)
    plt.close()
    
    return "Plot Saved"