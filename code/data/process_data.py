import dask.dataframe as dd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import (OneHotEncoder, PolynomialFeatures,
                                   StandardScaler)

# Define default features if not provided
numeric_features = ["feature1", "feature2", "feature3"]
categorical_features = ["category1", "category2"]


class DataEngine:
    def __init__(self, num_features=None, cat_features=None):
        self.numeric_features = num_features if num_features else numeric_features
        self.categorical_features = (
            cat_features if cat_features else categorical_features
        )

        self.preprocessor = make_pipeline(
            ColumnTransformer(
                [
                    ("num", StandardScaler(), self.numeric_features),
                    ("cat", OneHotEncoder(), self.categorical_features),
                ]
            ),
            PolynomialFeatures(degree=2, interaction_only=True),
        )

    def process(self, raw_data):
        try:
            # Assuming raw_data is a path to a parquet file or a list of paths
            ddf = dd.read_parquet(raw_data)
            # Data cleaning: drop rows with any missing values
            ddf = ddf.map_partitions(lambda df: df.dropna())
            return self.preprocessor.fit_transform(ddf)
        except FileNotFoundError as e:
            # Handle missing file error explicitly
            raise FileNotFoundError(f"Data file not found: {raw_data}") from e
        except Exception as e:
            # Handle general data processing errors
            raise ValueError(f"Error processing data from {raw_data}: {e}") from e

    def create_temporal_features(self, df):
        # This function is fine, but I'll check for any syntax/style issues
        # No obvious syntax issues, and it uses pandas-like operations which are fine.
        df["rolling_mean_7"] = df.groupby("entity")["value"].transform(
            lambda x: x.rolling(7).mean()
        )
        return df
