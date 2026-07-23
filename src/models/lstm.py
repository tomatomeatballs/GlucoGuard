import torch
import torch.nn as nn

class BiLSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size=1, num_layers=1):
        super(BiLSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # BiLSTM Layer
        # batch_first=True makes input shape (batch, seq, feature)
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                            batch_first=True, bidirectional=True)
        
        # Fully Connected Layer
        # Input to FC is hidden_size * 2 because it's bidirectional
        self.fc = nn.Linear(hidden_size * 2, output_size)
    
    def forward(self, x):
        # x shape: (batch_size, seq_len, input_size)
        
        # Forward propagate LSTM
        # out shape: (batch_size, seq_len, hidden_size*2)
        h0 = torch.zeros(self.num_layers * 2, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers * 2, x.size(0), self.hidden_size).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))
        
        # Decode the hidden state of the last time step
        out = self.fc(out[:, -1, :])
        return out
