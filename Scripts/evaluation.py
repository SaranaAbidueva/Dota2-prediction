from loguru import logger
import mlflow
import argparse
import pandas as pd


logger.info('Evaluation started')

parser = argparse.ArgumentParser()
parser.add_argument("--eval-dataset", type=str)
eval_dataset = pd.read_csv(parser.parse_args().eval_dataset)

with mlflow.start_run() as run:
    eval_dataset = mlflow.data.from_pandas(
        eval_dataset, targets="target"
    )
    last_version = mlflow.MlflowClient().get_registered_model('CancerModel').latest_versions[0].version
    mlflow.evaluate(
        data=eval_dataset, model_type="classifier", model=f'models:/CancerModel/{last_version}'
    )
    logger.success('Evaluation finished')
