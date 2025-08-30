#!/usr/bin/env python3
"""
Test script to show example API response with new structured prediction format
"""

import json

def show_example_api_response():
    """Show what the API response will look like with structured predictions"""
    
    # Example response that would be returned from the API
    api_response = {
        "predictions": [
            {
                "prediction": 1.5,
                "model_type": "SingleSeason",
                "prediction_index": 0,
                "features": {
                    "homeTeam": "TeamA",
                    "awayTeam": "TeamB"
                },
                "predicted_label": "margin"
            },
            {
                "prediction": 2.3,
                "model_type": "SingleSeason", 
                "prediction_index": 1,
                "features": {
                    "homeTeam": "TeamC",
                    "awayTeam": "TeamD"
                },
                "predicted_label": "margin"
            },
            {
                "prediction": -0.8,
                "model_type": "SingleSeason",
                "prediction_index": 2,
                "features": {
                    "homeTeam": "TeamE", 
                    "awayTeam": "TeamF"
                },
                "predicted_label": "margin"
            }
        ],
        "model_run_id": 123,
        "model_name": "naive-linear-regression",
        "status": "success"
    }
    
    print("Example API Response Structure:")
    print(json.dumps(api_response, indent=2))
    
    print("\n" + "="*50)
    print("Key improvements:")
    print("✓ Predictions are now a list of dictionaries/objects")
    print("✓ Each prediction includes the original feature names and values")
    print("✓ Each prediction includes the predicted label name")
    print("✓ Each prediction includes model metadata (type, index)")
    print("✓ Structure is consistent and easily parseable")
    print("✓ Response includes feature names for traceability")

if __name__ == "__main__":
    show_example_api_response()