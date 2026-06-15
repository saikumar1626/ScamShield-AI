import requests
import sys
import xml.etree.ElementTree as ET
# Base URL of local FastAPI server
SERVER_URL = "http://127.0.0.1:8000/api/sms-webhook"
STATS_URL = "http://127.0.0.1:8000/api/stats"
# Test Cases
TEST_SMS_MESSAGES = [
    {
        "Body": "Congratulations! You won a cash reward of ₹15,499 from PhonePe. Claim your prize instantly at http://bit.ly/pay-upi-ref",
        "From": "+919876543210",
        "expected_label": "scam"
    },
    {
        "Body": "Dear Customer, your SBI account XXXX4921 has been credited with ₹5,000 via UPI. Ref: 61092819028. - State Bank of India",
        "From": "+918877665544",
        "expected_label": "safe"
    }
]
def run_sms_webhook_tests():
    print("Executing Twilio Webhook Simulator Integration Tests...")
    
    # Check current stats to monitor delta updates
    try:
        initial_stats = requests.get(STATS_URL).json()
        print("Initial stats loaded. SMS count:", initial_stats.get("source_distribution", {}).get("sms", 0))
    except Exception as e:
        print(f"Error: Server not running on {STATS_URL}. Start 'python -m src.main' first! ({e})")
        sys.exit(1)
        
    sms_delta = 0
    for idx, test in enumerate(TEST_SMS_MESSAGES, 1):
        print(f"\n--- Running Test Case {idx}: {test['expected_label'].upper()} Message ---")
        
        # Prepare form parameters (url-encoded payload format from Twilio)
        payload = {
            "Body": test["Body"],
            "From": test["From"],
            "To": "+1234567890",
            "MessageSid": f"SMtestcase000000000000000000000{idx}"
        }
        
        # Twilio sends form-encoded POST
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            resp = requests.post(SERVER_URL, data=payload, headers=headers)
            print(f"Status Code: {resp.status_code}")
            assert resp.status_code == 200, f"Expected 200 OK, got {resp.status_code}"
            
            # Assert media type is XML
            content_type = resp.headers.get("content-type", "")
            print(f"Content-Type: {content_type}")
            assert "application/xml" in content_type or "text/xml" in content_type, f"Expected XML Content-Type, got {content_type}"
            
            xml_content = resp.text
            print(f"TwiML XML Output:\n{xml_content}")
            
            # Parse XML response
            root = ET.fromstring(xml_content)
            assert root.tag == "Response", f"Root tag should be 'Response', got '{root.tag}'"
            
            msg_node = root.find("Message")
            assert msg_node is not None, "TwiML response is missing <Message> node"
            
            reply_text = msg_node.text
            print(f"Reply Text: \"{reply_text}\" (Length: {len(reply_text)})")
            
            # Constraints Verification
            assert len(reply_text) <= 320, f"Reply text exceeds 320 character limit ({len(reply_text)})"
            
            if test["expected_label"] == "scam":
                assert "⚠️" in reply_text, "Scam warning prefix '⚠️' missing"
                assert "SCAM" in reply_text, "Scam keyword warning missing"
            else:
                assert "✅" in reply_text, "Safe prefix '✅' missing"
                assert "safe" in reply_text, "Safe keyword confirmation missing"
                
            sms_delta += 1
            print(f"Test Case {idx} passed successfully!")
            
        except AssertionError as e:
            print(f"Assertion Failure in Test Case {idx}: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Exception during Test Case {idx}: {e}")
            sys.exit(1)
    # Verify Database source updates
    print("\n--- Verifying Database Stats Tracking ---")
    try:
        updated_stats = requests.get(STATS_URL).json()
        initial_sms = initial_stats.get("source_distribution", {}).get("sms", 0)
        updated_sms = updated_stats.get("source_distribution", {}).get("sms", 0)
        
        print(f"Initial SMS Count: {initial_sms}")
        print(f"Updated SMS Count: {updated_sms} (Expected: {initial_sms + sms_delta})")
        
        assert updated_sms == initial_sms + sms_delta, "SMS count did not increment correctly in SQLite stats!"
        print("Database stats validation passed successfully!")
        
    except Exception as e:
        print(f"Stats validation failed: {e}")
        sys.exit(1)
        
    print("\nAll Twilio simulator integration tests passed successfully!")
if __name__ == "__main__":
    run_sms_webhook_tests()
