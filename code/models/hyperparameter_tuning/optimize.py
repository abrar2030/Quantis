import optuna
# from optuna.integration import PyTorchLightningPruningCallback # F401: Unused import
from pytorch_forecasting.models import TemporalFusionTransformer

from ..train_model import train_and_validate  # From ../train_model.py


def objective(trial):
    params = {
        "learning_rate": trial.suggest_loguniform("lr", 1e-5, 1e-2),
        "hidden_size": trial.suggest_categorical("hidden", [256, 512, 1024]),
        "dropout": trial.suggest_uniform("dropout", 0.1, 0.5),
    }
    model = TemporalFusionTransformer(**params)
    return train_and_validate(model)


study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100, timeout=3600)
