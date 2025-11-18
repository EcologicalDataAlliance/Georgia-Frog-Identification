"""
Test script for the Frog Sound Classifier API

This script sends sample requests to the API and displays the responses.
Make sure the API server is running before executing this script.

Usage:
    python test_api.py
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"


def test_health():
    """Test the health check endpoint."""
    print("=" * 60)
    print("Testing Health Check Endpoint")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    

def test_root():
    """Test the root endpoint."""
    print("=" * 60)
    print("Testing Root Endpoint")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def test_predict():
    """Test the prediction endpoint with sample features."""
    print("=" * 60)
    print("Testing Prediction Endpoint")
    print("=" * 60)
    
    # Sample feature vector (26 features)
    # These are placeholder values - replace with actual audio feature values
    # Features: centroid_mean, bandwidth_mean, rolloff_mean, mfcc1-13_mean,
    #           mfcc1,3,4,5,7,8,12_std, zcr_mean, rms_mean, rms_std
    sample_features = [
        1500.0,  # centroid_mean
        2000.0,  # bandwidth_mean
        3000.0,  # rolloff_mean
        -200.0, 150.0, 100.0, 50.0, 30.0, 20.0, 10.0, 5.0, 3.0, 2.0, 1.0, 0.5, 0.2,  # mfcc1-13_mean
        50.0, 30.0, 20.0, 15.0, 10.0, 8.0, 5.0,  # mfcc std values
        0.15,  # zcr_mean
        0.05,  # rms_mean
        0.02   # rms_std
    ]
    
    payload = {"features": sample_features}
    
    print(f"Sending {len(sample_features)} features...")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")
    
    try:
        response = requests.post(f"{BASE_URL}/predict", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            print(f"\n🏆 Predicted Class: {result['prediction']}")
            
            if result.get('top_3'):
                print(f"\n📊 Top 3 Predictions:")
                for i, pred in enumerate(result['top_3'], 1):
                    print(f"  {i}. {pred['species']}: {pred['confidence']:.2%}")
            
            if result.get('probabilities'):
                print(f"\n📈 Full Probability Distribution: {result['probabilities']}")
        else:
            print(f"Error Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to the API.")
        print("Make sure the server is running with:")
        print("    uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    
    print()


def test_predict_wrong_dimensions():
    """Test the prediction endpoint with wrong number of features."""
    print("=" * 60)
    print("Testing Error Handling (Wrong Feature Count)")
    print("=" * 60)
    
    # Send only 10 features instead of 26
    wrong_features = [0.0] * 10
    payload = {"features": wrong_features}
    
    print(f"Sending {len(wrong_features)} features (should be 26)...")
    
    try:
        response = requests.post(f"{BASE_URL}/predict", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to the API.\n")


if __name__ == "__main__":
    print("\n🐸 Frog Sound Classifier API Test Suite\n")
    
    try:
        # Run all tests
        test_health()
        test_root()
        test_predict()
        test_predict_wrong_dimensions()
        
        print("=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        print("\nFor interactive testing, visit: http://localhost:8000/docs")
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
