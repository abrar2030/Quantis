import dask.dataframe as dd  
from sklearn.pipeline import make_pipeline  
from sklearn.compose import ColumnTransformer  

class DataEngine:  
    def __init__(self):  
        self.preprocessor = make_pipeline(  
            ColumnTransformer([  
                ('num', StandardScaler(), numeric_features),  
                ('cat', OneHotEncoder(), categorical_features)  
            ]),  
            PolynomialFeatures(degree=2, interaction_only=True)  
        )  

    def process(self, raw_data):  
        ddf = dd.read_parquet(raw_data)  
        ddf = ddf.map_partitions(lambda df: df.dropna())  
        return self.preprocessor.fit_transform(ddf)  

    def create_temporal_features(self, df):  
        df['rolling_mean_7'] = df.groupby('entity')['value'].transform(  
            lambda x: x.rolling(7).mean()  
        )  
        return df  