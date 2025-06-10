"""
Dataset service for data management operations
"""
import os
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
import pandas as pd

import models


class DatasetService:
    def __init__(self, db: Session):
        self.db = db

    def create_dataset(self, name: str, description: str, owner_id: int, 
                      file_path: str = None, data: pd.DataFrame = None) -> models.Dataset:
        """Create a new dataset"""
        # Validate owner exists
        owner = self.db.query(models.User).filter(models.User.id == owner_id).first()
        if not owner:
            raise ValueError("Owner not found")
        
        # Analyze data if provided
        columns_info = None
        row_count = None
        file_size = None
        
        if data is not None:
            columns_info = {
                "columns": list(data.columns),
                "dtypes": {col: str(dtype) for col, dtype in data.dtypes.items()},
                "null_counts": data.isnull().sum().to_dict(),
                "sample_data": data.head(5).to_dict('records')
            }
            row_count = len(data)
            
            # Save data to file if not provided
            if not file_path:
                os.makedirs("data/datasets", exist_ok=True)
                file_path = f"data/datasets/{name}_{owner_id}.csv"
                data.to_csv(file_path, index=False)
        
        if file_path and os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            
            # If data not provided but file exists, analyze it
            if data is None:
                try:
                    data = pd.read_csv(file_path)
                    columns_info = {
                        "columns": list(data.columns),
                        "dtypes": {col: str(dtype) for col, dtype in data.dtypes.items()},
                        "null_counts": data.isnull().sum().to_dict(),
                        "sample_data": data.head(5).to_dict('records')
                    }
                    row_count = len(data)
                except Exception as e:
                    print(f"Error analyzing dataset file: {e}")
        
        # Create dataset record
        dataset = models.Dataset(
            name=name,
            description=description,
            owner_id=owner_id,
            file_path=file_path,
            file_size=file_size,
            columns_info=columns_info,
            row_count=row_count
        )
        
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        return dataset

    def get_dataset_by_id(self, dataset_id: int) -> Optional[models.Dataset]:
        """Get dataset by ID"""
        return self.db.query(models.Dataset).filter(
            and_(Dataset.id == dataset_id, Dataset.is_active == True)
        ).first()

    def get_datasets_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[models.Dataset]:
        """Get datasets by owner"""
        return self.db.query(models.Dataset).filter(
            and_(Dataset.owner_id == owner_id, Dataset.is_active == True)
        ).offset(skip).limit(limit).all()

    def get_all_datasets(self, skip: int = 0, limit: int = 100) -> List[models.Dataset]:
        """Get all datasets (admin only)"""
        return self.db.query(models.Dataset).filter(Dataset.is_active == True).offset(skip).limit(limit).all()

    def update_dataset(self, dataset_id: int, **kwargs) -> Optional[models.Dataset]:
        """Update dataset information"""
        dataset = self.get_dataset_by_id(dataset_id)
        if not dataset:
            return None
        
        for key, value in kwargs.items():
            if hasattr(dataset, key) and key not in ['id', 'owner_id', 'created_at']:
                setattr(dataset, key, value)
        
        self.db.commit()
        self.db.refresh(dataset)
        return dataset

    def delete_dataset(self, dataset_id: int) -> bool:
        """Delete dataset (soft delete)"""
        dataset = self.get_dataset_by_id(dataset_id)
        if not dataset:
            return False
        
        dataset.is_active = False
        self.db.commit()
        return True

    def load_dataset_data(self, dataset_id: int) -> Optional[pd.DataFrame]:
        """Load dataset data as pandas DataFrame"""
        dataset = self.get_dataset_by_id(dataset_id)
        if not dataset or not dataset.file_path:
            return None
        
        try:
            if dataset.file_path.endswith('.csv'):
                return pd.read_csv(dataset.file_path)
            elif dataset.file_path.endswith('.json'):
                return pd.read_json(dataset.file_path)
            elif dataset.file_path.endswith('.parquet'):
                return pd.read_parquet(dataset.file_path)
            else:
                return None
        except Exception as e:
            print(f"Error loading dataset {dataset_id}: {e}")
            return None

    def get_dataset_statistics(self, dataset_id: int) -> Optional[Dict[str, Any]]:
        """Get statistical information about dataset"""
        data = self.load_dataset_data(dataset_id)
        if data is None:
            return None
        
        try:
            stats = {
                "shape": data.shape,
                "columns": list(data.columns),
                "dtypes": {col: str(dtype) for col, dtype in data.dtypes.items()},
                "missing_values": data.isnull().sum().to_dict(),
                "numeric_stats": data.describe().to_dict() if len(data.select_dtypes(include=['number']).columns) > 0 else {},
                "categorical_stats": {}
            }
            
            # Add categorical statistics
            categorical_cols = data.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                stats["categorical_stats"][col] = {
                    "unique_count": data[col].nunique(),
                    "top_values": data[col].value_counts().head(10).to_dict()
                }
            
            return stats
        except Exception as e:
            print(f"Error calculating statistics for dataset {dataset_id}: {e}")
            return None

