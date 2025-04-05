from feast import FeatureStore, Entity, ValueType  
from datetime import timedelta  

driver = Entity(  
    name="driver_id",  
    value_type=ValueType.INT64,  
    description="Driver identifier"  
)  

fs = FeatureStore(repo_path=".")  

def create_feature_view():  
    fs.apply([  
        FeatureView(  
            name="driver_stats",  
            entities=["driver_id"],  
            ttl=timedelta(days=365),  
            features=[...]  
        )  
    ])  