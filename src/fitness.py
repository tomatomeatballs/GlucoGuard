import pandas as pd
from vmdpy import VMD
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from src.models.lstm import BiLSTMModel
from sklearn.preprocessing import MinMaxScaler
import time

def train_evaluate_bilstm(params, X_data, kim=3, zim=1, device='cpu'):
    """
    Objective function for optimization
    X_data: Input matrix (Samples x Features). 
            Logic: Uses 'kim' history of ALL features to predict NEXT step of LAST feature.
    """
    # Unpack parameters
    num_hidden = int(round(params[0]))
    num_hidden = max(1, num_hidden)
    max_epochs = int(round(params[1]))
    max_epochs = max(1, max_epochs)
    learning_rate = params[2]
    
    num_samples = X_data.shape[0]
    
    # Construct Samples
    X_list = []
    y_list = []
    
    for i in range(num_samples - kim - zim + 1):
        # Input: kim steps of ALL columns flattened
        hist_window = X_data[i : i + kim, :] 
        X_list.append(hist_window.flatten()) 
        
        # Output: The LAST column (Glucose) at target step
        target_val = X_data[i + kim + zim - 1, -1]
        y_list.append(target_val)
        
    X_arr = np.array(X_list) 
    y_arr = np.array(y_list).reshape(-1, 1)
    
    # Train/Test Split
    train_size = int(0.6 * len(X_arr))
    X_train_raw = X_arr[:train_size]
    y_train_raw = y_arr[:train_size]
    
    # Normalization
    scaler_X = MinMaxScaler(feature_range=(0, 1))
    scaler_y = MinMaxScaler(feature_range=(0, 1))
    
    X_train_scaled = scaler_X.fit_transform(X_train_raw)
    y_train_scaled = scaler_y.fit_transform(y_train_raw)
    
    # Reshape for BiLSTM: (Batch, Seq_Len=1, Features)
    # Why Seq_Len=1? Because we flattened the time window into features to match MATLAB structure strictly.
    seq_len = 1
    input_size = X_train_scaled.shape[1]
    
    X_train_t = torch.FloatTensor(X_train_scaled).reshape(-1, seq_len, input_size).to(device)
    y_train_t = torch.FloatTensor(y_train_scaled).to(device)
    
    # Model
    model = BiLSTMModel(input_size, num_hidden).to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    model.train()
    for img in range(max_epochs):
        optimizer.zero_grad()
        outputs = model(X_train_t)
        loss = criterion(outputs, y_train_t)
        loss.backward()
        optimizer.step()
        
    model.eval()
    with torch.no_grad():
        train_pred = model(X_train_t)
        loss_val = criterion(train_pred, y_train_t)
        
    return torch.sqrt(loss_val).item()

def predict_final(best_params, X_data, kim=3, zim=1, device='cpu'):
    """
    Run final prediction with best parameters
    """
    num_hidden = int(round(best_params[0]))
    max_epochs = int(round(best_params[1]))
    learning_rate = best_params[2]
    
    num_samples = X_data.shape[0]
    
    X_list, y_list = [], []
    for i in range(num_samples - kim - zim + 1):
        hist_window = X_data[i : i + kim, :] 
        X_list.append(hist_window.flatten()) 
        target_val = X_data[i + kim + zim - 1, -1]
        y_list.append(target_val)
        
    X_arr = np.array(X_list)
    y_arr = np.array(y_list).reshape(-1, 1)
    
    train_size = int(0.6 * len(X_arr))
    X_train = X_arr[:train_size]
    y_train = y_arr[:train_size]
    X_test = X_arr[train_size:]
    y_test = y_arr[train_size:]
    
    scaler_X = MinMaxScaler((0,1))
    scaler_y = MinMaxScaler((0,1))
    
    X_train_s = scaler_X.fit_transform(X_train)
    y_train_s = scaler_y.fit_transform(y_train)
    X_test_s = scaler_X.transform(X_test)
    y_test_s = scaler_y.transform(y_test)
    
    seq_len = 1
    input_size = X_train_s.shape[1]
    
    X_train_t = torch.FloatTensor(X_train_s).reshape(-1, seq_len, input_size).to(device)
    y_train_t = torch.FloatTensor(y_train_s).to(device)
    X_test_t = torch.FloatTensor(X_test_s).reshape(-1, seq_len, input_size).to(device)
    
    model = BiLSTMModel(input_size, num_hidden).to(device)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()
    
    model.train()
    for _ in range(max_epochs):
        optimizer.zero_grad()
        out = model(X_train_t)
        loss = criterion(out, y_train_t)
        loss.backward()
        optimizer.step()
        
    model.eval()
    with torch.no_grad():
        test_pred_s = model(X_test_t).cpu().numpy()
        
    test_pred = scaler_y.inverse_transform(test_pred_s)
    
    return {
        'y_test': y_test,
        'y_pred': test_pred,
        'model_state': model.state_dict(),
        'scaler_X': scaler_X,
        'scaler_y': scaler_y,
        'input_size': input_size,
        'hidden_size': num_hidden,
    }

