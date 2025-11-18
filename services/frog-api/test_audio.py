"""Test the /predict-audio endpoint with a real audio file."""
import requests
import json

def test_audio_prediction(audio_file_path):
    """Send an audio file to the API and display the prediction."""
    url = "http://localhost:8000/predict-audio"
    
    print(f"\n🎵 Testing audio file: {audio_file_path}")
    print("=" * 60)
    
    try:
        with open(audio_file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            
            print("🐸 Prediction Results:")
            print(f"Primary Prediction: {result['prediction']}")
            print("\n📊 Top 3 Species:")
            for i, pred in enumerate(result['top_3'], 1):
                species = pred['species']
                confidence = pred['confidence'] * 100
                print(f"  {i}. {species}: {confidence:.2f}%")
            
            print(f"\n✅ Success! The model predicts: {result['prediction']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.json())
            
    except FileNotFoundError:
        print(f"❌ Error: Audio file not found at {audio_file_path}")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API. Is the server running?")
        print("Start the server with: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_audio_prediction("FowlerDownload-2636520879959417.mp3")
