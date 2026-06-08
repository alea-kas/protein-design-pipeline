#!/usr/bin/env python3
import argparse
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from kan import KAN

def parse_args():
    parser = argparse.ArgumentParser(description="Train KAN regression model and Concrete Autoencoder.")
    parser.add_argument("--dataset", type=str, default="results/ml_features_dataset.csv", help="Input dataset")
    parser.add_argument("--out_dir", type=str, default="results/kan_models", help="Output directory")
    parser.add_argument("--kan_steps", type=int, default=50, help="LBFGS optimization steps for KAN")
    parser.add_argument("--cae_epochs", type=int, default=150, help="Training epochs for Concrete AE")
    return parser.parse_args()

class ConcreteAE(nn.Module):
    def __init__(self, input_dim, k):
        super().__init__()
        self.logits = nn.Parameter(torch.zeros(input_dim, k))
        self.decoder = nn.Sequential(nn.Linear(k, 16), nn.ReLU(), nn.Linear(16, input_dim))
        
    def forward(self, x):
        scores = F.softmax(self.logits, dim=0).unsqueeze(0).expand(x.shape[0], -1, -1)
        z = torch.bmm(scores.transpose(1, 2), x.unsqueeze(2)).squeeze(-1)
        return self.decoder(z), scores

def main():
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    infile = project_root / args.dataset
    out_dir = project_root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(infile).dropna(subset=["motif_rmsd"])
    feature_cols = ["chai_plddt", "seq_length"]
    for pf in ["score_rank", "mpnn_score", "seq_recovery", "chai_score"]:
        if pf in df.columns: 
            feature_cols.append(pf)

    X = df[feature_cols].fillna(0.0).values
    y = df["motif_rmsd"].values.reshape(-1, 1)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
    x_scaler, y_scaler = StandardScaler(), StandardScaler()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    X_train_t = torch.tensor(x_scaler.fit_transform(X_train), dtype=torch.float32).to(device)
    X_test_t = torch.tensor(x_scaler.transform(X_test), dtype=torch.float32).to(device)
    y_train_t = torch.tensor(y_scaler.fit_transform(y_train), dtype=torch.float32).to(device)
    y_test_t = torch.tensor(y_scaler.transform(y_test), dtype=torch.float32).to(device)

    # 1. Base KAN Model
    model = KAN(width=[X_train.shape[1], 8, 1], grid=2, k=3, device=device)
    model.fit(
        {"train_input": X_train_t, "train_label": y_train_t, "test_input": X_test_t, "test_label": y_test_t}, 
        opt="LBFGS", 
        steps=args.kan_steps
    )
    torch.save(model.state_dict(), out_dir / "kan_model_all.pt")

    # 2. Concrete Autoencoder for feature selection
    cae = ConcreteAE(X_train.shape[1], 2).to(device)
    optimizer = torch.optim.Adam(cae.parameters(), lr=1e-3)
    
    for _ in range(args.cae_epochs):
        optimizer.zero_grad()
        loss = F.mse_loss(cae(X_train_t)[0], X_train_t)
        loss.backward()
        optimizer.step()

    scores_np = cae(X_train_t)[1].detach().cpu().numpy()
    selected_indices = np.unique(np.argmax(scores_np, axis=0))
    selected_features = [feature_cols[i] for i in selected_indices]

    with open(out_dir / "concrete_ae_selected_features.txt", "w") as f:
        f.write("\n".join(selected_features))

    # 3. KAN on selected features
    if len(selected_indices) >= 1:
        X_train_sel = X_train[:, selected_indices]
        X_test_sel = X_test[:, selected_indices]
        
        X_train_sel_t = torch.tensor(StandardScaler().fit_transform(X_train_sel), dtype=torch.float32).to(device)
        X_test_sel_t = torch.tensor(StandardScaler().fit_transform(X_test_sel), dtype=torch.float32).to(device)
        
        model_sel = KAN(width=[len(selected_indices), 4, 1], grid=2, k=3, device=device)
        model_sel.fit(
            {"train_input": X_train_sel_t, "train_label": y_train_t, "test_input": X_test_sel_t, "test_label": y_test_t}, 
            opt="LBFGS", 
            steps=args.kan_steps
        )
        torch.save(model_sel.state_dict(), out_dir / "kan_model_selected.pt")

if __name__ == "__main__":
    main()
