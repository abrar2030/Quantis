"""
Dataset management endpoints
"""
import os
import tempfile
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
import pandas as pd

import database import get_db
importmiddleware.auth import (
    admin_required, readonly_or_above, user_or_admin_required,
    validate_api_key
)
importservices.dataset_service import DatasetService

router = APIRouter()


# Pydantic models
class DatasetCreate(BaseModel):
    name: str
    description: str


class DatasetResponse(BaseModel):
    id: int
    name: str
    description: str
    owner_id: int
    owner_username: str
    file_path: Optional[str]
    file_size: Optional[int]
    row_count: Optional[int]
    columns: Optional[List[str]]
    created_at: str
    updated_at: Optional[str]


class DatasetStats(BaseModel):
    shape: List[int]
    columns: List[str]
    dtypes: dict
    missing_values: dict
    numeric_stats: dict
    categorical_stats: dict


# Dataset CRUD endpoints
@router.post("/datasets", response_model=DatasetResponse)
async def create_dataset(
    dataset_data: DatasetCreate,
    current_user: dict = Depends(user_or_admin_required),
    db: Session = Depends(get_db)
):
    """Create a new dataset."""
    dataset_service = DatasetService(db)
    
    try:
        dataset = dataset_service.create_dataset(
            name=dataset_data.name,
            description=dataset_data.description,
            owner_id=current_user["user_id"]
        )
        
        return DatasetResponse(
            id=dataset.id,
            name=dataset.name,
            description=dataset.description,
            owner_id=dataset.owner_id,
            owner_username=current_user["username"],
            file_path=dataset.file_path,
            file_size=dataset.file_size,
            row_count=dataset.row_count,
            columns=dataset.columns_info.get("columns", []) if dataset.columns_info else [],
            created_at=dataset.created_at.isoformat(),
            updated_at=dataset.updated_at.isoformat() if dataset.updated_at else None
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/datasets/upload", response_model=DatasetResponse)
async def upload_dataset(
    name: str,
    description: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(user_or_admin_required),
    db: Session = Depends(get_db)
):
    """Upload a dataset file."""
    dataset_service = DatasetService(db)
    
    # Validate file type
    allowed_extensions = ['.csv', '.json', '.parquet']
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Create datasets directory if it doesn't exist
        os.makedirs("data/datasets", exist_ok=True)
        
        # Save uploaded file
        file_path = f"data/datasets/{name}_{current_user['user_id']}{file_extension}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Create dataset record
        dataset = dataset_service.create_dataset(
            name=name,
            description=description,
            owner_id=current_user["user_id"],
            file_path=file_path
        )
        
        return DatasetResponse(
            id=dataset.id,
            name=dataset.name,
            description=dataset.description,
            owner_id=dataset.owner_id,
            owner_username=current_user["username"],
            file_path=dataset.file_path,
            file_size=dataset.file_size,
            row_count=dataset.row_count,
            columns=dataset.columns_info.get("columns", []) if dataset.columns_info else [],
            created_at=dataset.created_at.isoformat(),
            updated_at=dataset.updated_at.isoformat() if dataset.updated_at else None
        )
        
    except Exception as e:
        # Clean up file if dataset creation failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to upload dataset: {str(e)}")


@router.get("/datasets", response_model=List[DatasetResponse])
async def get_datasets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """Get datasets for the current user."""
    dataset_service = DatasetService(db)
    
    if current_user["role"] == "admin":
        datasets = dataset_service.get_all_datasets(skip, limit)
    else:
        datasets = dataset_service.get_datasets_by_owner(current_user["user_id"], skip, limit)
    
    # Get owner usernames
    importservices.user_service import UserService
    user_service = UserService(db)
    
    result = []
    for dataset in datasets:
        owner = user_service.get_user_by_id(dataset.owner_id)
        owner_username = owner.username if owner else "Unknown"
        
        result.append(DatasetResponse(
            id=dataset.id,
            name=dataset.name,
            description=dataset.description,
            owner_id=dataset.owner_id,
            owner_username=owner_username,
            file_path=dataset.file_path,
            file_size=dataset.file_size,
            row_count=dataset.row_count,
            columns=dataset.columns_info.get("columns", []) if dataset.columns_info else [],
            created_at=dataset.created_at.isoformat(),
            updated_at=dataset.updated_at.isoformat() if dataset.updated_at else None
        ))
    
    return result


@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: int,
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """Get dataset by ID."""
    dataset_service = DatasetService(db)
    dataset = dataset_service.get_dataset_by_id(dataset_id)
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Check permissions
    if current_user["role"] != "admin" and dataset.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get owner username
    importservices.user_service import UserService
    user_service = UserService(db)
    owner = user_service.get_user_by_id(dataset.owner_id)
    owner_username = owner.username if owner else "Unknown"
    
    return DatasetResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        owner_id=dataset.owner_id,
        owner_username=owner_username,
        file_path=dataset.file_path,
        file_size=dataset.file_size,
        row_count=dataset.row_count,
        columns=dataset.columns_info.get("columns", []) if dataset.columns_info else [],
        created_at=dataset.created_at.isoformat(),
        updated_at=dataset.updated_at.isoformat() if dataset.updated_at else None
    )


@router.put("/datasets/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: int,
    dataset_update: DatasetCreate,
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """Update dataset information."""
    dataset_service = DatasetService(db)
    dataset = dataset_service.get_dataset_by_id(dataset_id)
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Check permissions
    if current_user["role"] != "admin" and dataset.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update dataset
    updated_dataset = dataset_service.update_dataset(
        dataset_id,
        name=dataset_update.name,
        description=dataset_update.description
    )
    
    if not updated_dataset:
        raise HTTPException(status_code=500, detail="Failed to update dataset")
    
    return DatasetResponse(
        id=updated_dataset.id,
        name=updated_dataset.name,
        description=updated_dataset.description,
        owner_id=updated_dataset.owner_id,
        owner_username=current_user["username"],
        file_path=updated_dataset.file_path,
        file_size=updated_dataset.file_size,
        row_count=updated_dataset.row_count,
        columns=updated_dataset.columns_info.get("columns", []) if updated_dataset.columns_info else [],
        created_at=updated_dataset.created_at.isoformat(),
        updated_at=updated_dataset.updated_at.isoformat() if updated_dataset.updated_at else None
    )


@router.delete("/datasets/{dataset_id}")
async def delete_dataset(
    dataset_id: int,
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """Delete dataset."""
    dataset_service = DatasetService(db)
    dataset = dataset_service.get_dataset_by_id(dataset_id)
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Check permissions
    if current_user["role"] != "admin" and dataset.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = dataset_service.delete_dataset(dataset_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete dataset")
    
    return {"message": "Dataset deleted successfully"}


# Dataset analysis endpoints
@router.get("/datasets/{dataset_id}/stats", response_model=DatasetStats)
async def get_dataset_statistics(
    dataset_id: int,
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """Get statistical information about dataset."""
    dataset_service = DatasetService(db)
    dataset = dataset_service.get_dataset_by_id(dataset_id)
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Check permissions
    if current_user["role"] != "admin" and dataset.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    stats = dataset_service.get_dataset_statistics(dataset_id)
    if not stats:
        raise HTTPException(status_code=500, detail="Failed to calculate dataset statistics")
    
    return DatasetStats(**stats)


@router.get("/datasets/{dataset_id}/preview")
async def preview_dataset(
    dataset_id: int,
    rows: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """Get a preview of dataset data."""
    dataset_service = DatasetService(db)
    dataset = dataset_service.get_dataset_by_id(dataset_id)
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Check permissions
    if current_user["role"] != "admin" and dataset.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    data = dataset_service.load_dataset_data(dataset_id)
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to load dataset data")
    
    # Return preview
    preview_data = data.head(rows)
    
    return {
        "columns": list(data.columns),
        "data": preview_data.to_dict('records'),
        "total_rows": len(data),
        "preview_rows": len(preview_data)
    }


@router.get("/datasets/{dataset_id}/download")
async def download_dataset(
    dataset_id: int,
    format: str = Query("csv", regex="^(csv|json|parquet)$"),
    current_user: dict = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """Download dataset in specified format."""
    dataset_service = DatasetService(db)
    dataset = dataset_service.get_dataset_by_id(dataset_id)
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Check permissions
    if current_user["role"] != "admin" and dataset.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    data = dataset_service.load_dataset_data(dataset_id)
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to load dataset data")
    
    # Create temporary file for download
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format}") as tmp_file:
        if format == "csv":
            data.to_csv(tmp_file.name, index=False)
            media_type = "text/csv"
        elif format == "json":
            data.to_json(tmp_file.name, orient="records", indent=2)
            media_type = "application/json"
        elif format == "parquet":
            data.to_parquet(tmp_file.name, index=False)
            media_type = "application/octet-stream"
        
        from fastapi.responses import FileResponse
        return FileResponse(
            tmp_file.name,
            media_type=media_type,
            filename=f"{dataset.name}.{format}"
        )

