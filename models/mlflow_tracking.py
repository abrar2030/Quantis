import mlflow


def log_experiment(params, metrics, model):
    with mlflow.start_run():
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        mlflow.pytorch.log_model(model, "model")
        mlflow.log_artifact("data/processed/feature_map.json")


def register_model(model_name, run_id):
    model_uri = f"runs:/{run_id}/model"
    mlflow.register_model(model_uri, model_name)
