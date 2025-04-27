import mlflow
import mlflow.sklearn

def start_experiment(experiment_name: str):
    """Crea o setea un experimento de MLflow."""
    mlflow.set_experiment(experiment_name)

def start_run(run_name: str = None):
    """Inicia un run de MLflow."""
    return mlflow.start_run(run_name=run_name)

def log_params(params: dict):
    """Loguea los parámetros."""
    for key, value in params.items():
        mlflow.log_param(key, value)

def log_metrics(metrics: dict):
    """Loguea las métricas."""
    for key, value in metrics.items():
        mlflow.log_metric(key, value)

def log_model(model, artifact_path: str = "model"):
    """Loguea el modelo."""
    mlflow.sklearn.log_model(model, artifact_path)
