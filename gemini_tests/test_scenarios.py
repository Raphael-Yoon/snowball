import pytest
from playwright.sync_api import Page, expect

# Base URL for the application
BASE_URL = "http://localhost:5001"

def test_main_page(page: Page):
    """Test that the main page loads and has the correct title."""
    print("\n[Test] Visiting Main Page...")
    page.goto(BASE_URL)
    
    # Check title
    expect(page).to_have_title(lambda t: "SnowBall" in t or "ITGC" in t)
    
    # Check for main elements
    print("  - Checking for main navigation cards...")
    expect(page.locator(".card").first).to_be_visible()
    
    print("[PASS] Main Page loaded successfully.")

def test_login_flow(page: Page):
    """Test the login flow using Admin Login."""
    print("\n[Test] Starting Login Flow...")
    page.goto(f"{BASE_URL}/login")
    
    # Click Admin Login Button
    print("  - Clicking '관리자 로그인' button...")
    # Try to find the button by text or value
    # Based on user request, there is a button.
    # We'll try a few selectors to be robust.
    admin_btn = page.locator("button[value='admin_login']")
    if not admin_btn.is_visible():
        admin_btn = page.locator("text=관리자 로그인")
        
    expect(admin_btn).to_be_visible()
    admin_btn.click()
    
    # Verify Login Success
    print("  - Checking login success...")
    # Should redirect to index and show logout button or user name
    expect(page).to_have_url(f"{BASE_URL}/")
    # Check for logout link to confirm we are logged in
    expect(page.locator("a[href='/logout']")).to_be_visible()
    
    print("[PASS] Login Flow completed successfully.")

def test_interview_flow(page: Page):
    """Test the interview flow (Link 2)."""
    print("\n[Test] Starting Interview Flow...")
    
    # Login first (using Admin Login)
    page.goto(f"{BASE_URL}/login")
    if page.locator("button[value='admin_login']").is_visible() or page.locator("text=관리자 로그인").is_visible():
        print("  - Logging in for interview test...")
        # Try button value first, then text
        if page.locator("button[value='admin_login']").is_visible():
            page.click("button[value='admin_login']")
        else:
            page.click("text=관리자 로그인")
        page.wait_for_url(f"{BASE_URL}/")

    # Go to Interview Page
    print("  - Navigating to Interview (Link 2)...")
    page.goto(f"{BASE_URL}/link2?reset=1")
    
    # Check if we are on the interview page
    expect(page.locator("form")).to_be_visible()
    
    # Answer a few questions
    # Question 1 (Index 0) - Email (should be auto-filled or we fill it)
    print("  - Answering Question 1...")
    
    # Click Next
    # Try finding a button with type submit
    next_button = page.locator("button[type='submit']")
    if next_button.is_visible():
        next_button.click()
    else:
        # Try finding a button with text 'Next' or similar
        page.click("text=Next")
        
    # Wait for next question
    page.wait_for_load_state("networkidle")
    
    # Question 2
    print("  - Answering Question 2...")
    # Fill some dummy text if there's a text input
    inputs = page.locator("input[type='text']")
    if inputs.count() > 0:
        inputs.first.fill("Test Answer")
    
    # Click Next
    page.locator("button[type='submit']").click()
    
    print("[PASS] Interview Flow (partial) completed successfully.")
