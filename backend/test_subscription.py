"""
Quick test script to verify subscription endpoint works after migration.
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_subscription():
    """Test the subscription endpoint."""
    
    print("=" * 60)
    print("TESTING SUBSCRIPTION ENDPOINT")
    print("=" * 60)
    
    # Test 1: Subscribe to Free plan
    print("\n[Test 1] Subscribing to Free plan...")
    response = requests.post(
        f"{API_URL}/pricing/user/subscribe",
        json={
            "user_id": "test_user_123",
            "plan_code": "free",
            "billing_period": "monthly"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS!")
        print(f"   Plan: {data['subscription']['plan_name']}")
        print(f"   Status: {data['subscription']['status']}")
        print(f"   Period: {data['subscription']['billing_period']}")
    else:
        print(f"❌ FAILED: {response.status_code}")
        print(f"   Error: {response.text}")
        return False
    
    # Test 2: Subscribe to Pro plan
    print("\n[Test 2] Upgrading to Pro plan...")
    response = requests.post(
        f"{API_URL}/pricing/user/subscribe",
        json={
            "user_id": "test_user_123",
            "plan_code": "pro",
            "billing_period": "yearly"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS!")
        print(f"   Plan: {data['subscription']['plan_name']}")
        print(f"   Status: {data['subscription']['status']}")
        print(f"   Period: {data['subscription']['billing_period']}")
        print(f"   Price: ${data['subscription']['price_cents'] / 100:.2f}")
    else:
        print(f"❌ FAILED: {response.status_code}")
        print(f"   Error: {response.text}")
        return False
    
    # Test 3: Get current plan
    print("\n[Test 3] Getting current plan...")
    response = requests.get(
        f"{API_URL}/pricing/user/current-plan",
        params={"user_id": "test_user_123"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS!")
        print(f"   Current Plan: {data['plan_name']}")
        print(f"   Status: {data['status']}")
        print(f"   Period: {data['billing_period']}")
    else:
        print(f"❌ FAILED: {response.status_code}")
        print(f"   Error: {response.text}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        test_subscription()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to backend server")
        print("   Make sure backend is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

