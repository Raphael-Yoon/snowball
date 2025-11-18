"""
Test script for population upload functionality
"""
import requests
import json

# Test parameters
url = 'http://127.0.0.1:5001/api/operation-evaluation/upload-population'
test_file = 'test_population.xlsx'

# Prepare form data
files = {
    'population_file': ('test_population.xlsx', open(test_file, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
}

data = {
    'control_code': 'C-EL-RA-08-01',
    'rcm_id': '1',  # Adjust as needed
    'design_evaluation_session': 'TEST_SESSION',
    'field_mapping': json.dumps({
        'number': 0,  # Column index for '번호'
        'description': 1  # Column index for '설명'
    })
}

print("Testing population upload API...")
print(f"URL: {url}")
print(f"Control Code: {data['control_code']}")
print(f"File: {test_file}")
print(f"Field Mapping: {data['field_mapping']}")
print("")

try:
    # Note: This requires authentication/session, so it might fail
    response = requests.post(url, files=files, data=data)

    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.text}")

    if response.status_code == 200:
        result = response.json()
        print("\nSuccess!")
        print(f"  Population Count: {result.get('population_count')}")
        print(f"  Sample Size: {result.get('sample_size')}")
        print(f"  Line ID: {result.get('line_id')}")
    else:
        print("\nFailed!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
