import mlflow.pyfunc
import torch
from fastapi import APIRouter

router = APIRouter()


class ModelWrapper(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        self.model = torch.load(context.artifacts["model_path"])

    def predict(self, context, model_input):
        return self.model(torch.Tensor(model_input)).detach().numpy()


@router.post("/model/deploy")
async def deploy_model(model_registry_path: str):
    mlflow.pyfunc.save_model(
        path="model_serving",
        python_model=ModelWrapper(),
        artifacts={"model_path": model_registry_path},
    )
    return {"status": "deployed"}
