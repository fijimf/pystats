#!/usr/bin/env python3
"""
Test script to verify the new structured prediction format
"""

import pandas as pd
from unittest.mock import Mock
from app.services.ml_prediction_service import MLPredictionService
from app.statistical.sample_linear_model import SampleLinearModel
import numpy as np

def test_prediction_formatting():
    """Test that predictions are formatted as list of dictionaries"""
    
    # Create mock objects
    db = Mock()
    ModelRun = Mock()
    model_registry = Mock()
    
    # Create service
    service = MLPredictionService(db, ModelRun, model_registry)
    
    # Create sample model
    model = SampleLinearModel()
    
    # Create sample predictions
    predictions = np.array([1.5, 2.3, -0.8])
    
    # Create sample features dataframe
    features_df = pd.DataFrame([
        {"homeTeam": "TeamA", "awayTeam": "TeamB"},
        {"homeTeam": "TeamC", "awayTeam": "TeamD"},
        {"homeTeam": "TeamE", "awayTeam": "TeamF"}
    ])
    
    # Test formatting
    formatted = service._format_predictions(predictions, model, features_df)
    
    print("Formatted predictions:")
    print(f"Type: {type(formatted)}")
    print(f"Length: {len(formatted)}")
    
    for i, pred in enumerate(formatted):
        print(f"\nPrediction {i}:")
        print(f"  Structure: {pred}")
        print(f"  Type: {type(pred)}")
        print(f"  Keys: {list(pred.keys())}")
    
    # Verify structure
    assert isinstance(formatted, list), "Predictions should be a list"
    assert len(formatted) == 3, "Should have 3 predictions"
    
    for pred in formatted:
        assert isinstance(pred, dict), "Each prediction should be a dictionary"
        assert 'prediction' in pred, "Should contain 'prediction' key"
        assert 'model_type' in pred, "Should contain 'model_type' key"
        assert 'prediction_index' in pred, "Should contain 'prediction_index' key"
        assert 'features' in pred, "Should contain 'features' key"
        assert 'predicted_label' in pred, "Should contain 'predicted_label' key"
    
    print("\n✓ All tests passed! Predictions are correctly formatted as list of dictionaries.")
    return formatted

if __name__ == "__main__":
    test_prediction_formatting()