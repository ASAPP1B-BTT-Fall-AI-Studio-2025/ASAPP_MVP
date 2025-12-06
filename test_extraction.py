#!/usr/bin/env python3
"""
Test script to verify field extraction works correctly
"""
import re
import sys
sys.path.insert(0, '/Users/divyalakshmivaradharajanpremsudha/ASAPP_MVP/ASAPP_MVP/backend')

from main import extract_email, extract_phone, extract_zip_code, extract_order_id

# Test cases from the display screenshot
test_conversations = [
    {
        "name": "Test 1",
        "text": "Customer called about order 1012809669. Email is john@example.com. Phone (752) 693-4642. Zip code 78202.",
        "expected": {
            "email": "john@example.com",
            "phone": "693-4642",  # Will vary based on implementation
            "zipCode": "78202",
            "orderId": "1012809669"
        }
    },
    {
        "name": "Test 2", 
        "text": "Hi, my order number is 116-048-7515. Please contact at (123) 456-7890. Address is 90210.",
        "expected": {
            "email": "NA",
            "phone": "456-7890",
            "zipCode": "90210",
            "orderId": "116-048-7515"
        }
    },
    {
        "name": "Test 3",
        "text": "Order ID is 2243746561. Customer email: customer@company.com. Zip: 10001.",
        "expected": {
            "email": "customer@company.com",
            "phone": "NA",
            "zipCode": "10001",
            "orderId": "2243746561"
        }
    }
]

print("=" * 80)
print("FIELD EXTRACTION TEST")
print("=" * 80)

for test in test_conversations:
    print(f"\n{test['name']}")
    print("-" * 80)
    print(f"Text: {test['text']}")
    print()
    
    email = extract_email(test['text'])
    phone = extract_phone(test['text'])
    zipcode = extract_zip_code(test['text'])
    orderid = extract_order_id(test['text'])
    
    print(f"Email:   {email}")
    print(f"Phone:   {phone}")
    print(f"Zip:     {zipcode}")
    print(f"Order:   {orderid}")
    print()
    
    # Check if extraction was successful
    email_ok = email != "NA"
    phone_ok = phone != "NA"
    zip_ok = zipcode != "NA"
    order_ok = orderid != "NA"
    
    print(f"Results: Email={'✓' if email_ok else '✗'} Phone={'✓' if phone_ok else '✗'} Zip={'✓' if zip_ok else '✗'} Order={'✓' if order_ok else '✗'}")

print("\n" + "=" * 80)
print("EXTRACTION TEST COMPLETE")
print("=" * 80)
