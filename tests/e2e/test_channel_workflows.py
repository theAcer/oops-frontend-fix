"""
M-Pesa Channel Management - E2E Tests

End-to-end tests for complete user workflows using Playwright,
testing the full application stack from user interface to database.
"""

import pytest
from playwright.sync_api import Page, expect, Browser, BrowserContext
import json
import time


# Test Fixtures
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for E2E tests"""
    return {
        **browser_context_args,
        "record_video_dir": "test-results/videos/",
        "record_har_path": "test-results/hars/",
    }


# E2E Test Classes
class TestChannelOnboardingE2E:
    """End-to-end tests for channel onboarding workflow"""

    def test_complete_merchant_registration_flow(self, page: Page):
        """Test complete merchant registration to channel setup flow"""
        # Navigate to become merchant page
        page.goto("/dashboard/become-merchant")

        # Verify page loaded
        expect(page.locator("h1")).to_contain_text("Become a Merchant")
        expect(page.locator("text=Business Details")).to_be_visible()

        # Fill out the form
        page.fill("#businessName", "Test Business Solutions")
        page.fill("#ownerName", "John Doe")
        page.fill("#phone", "254712345678")
        page.select_option("#businessType", "retail")
        page.fill("#mpesaTillNumber", "174379")

        # Submit the form
        page.click("button[type='submit']")

        # Wait for redirect and verify we're on channels page
        expect(page).to_have_url("**/dashboard/channels", timeout=10000)
        expect(page.locator("h1")).to_contain_text("M-Pesa Channels")

        # Verify the channels page loaded correctly
        expect(page.locator("text=Your Channels")).to_be_visible()
        expect(page.locator("text=Add Channel")).to_be_visible()

    def test_channel_creation_workflow(self, page: Page):
        """Test complete channel creation workflow"""
        # Start from channels page
        page.goto("/dashboard/channels")

        # Click add channel button
        page.click("text=Add Channel")

        # Verify we're on the add channel page
        expect(page).to_have_url("**/dashboard/channels/add")
        expect(page.locator("h1")).to_contain_text("Add M-Pesa Channel")

        # Fill out the channel form
        page.fill("#name", "Main PayBill Channel")
        page.select_option("#type", "PayBill")
        page.fill("#shortcode", "174379")
        page.select_option("#environment", "sandbox")
        page.fill("#consumerKey", "sandbox_consumer_key_12345")
        page.fill("#consumerSecret", "sandbox_consumer_secret_67890")

        # Submit the form
        page.click("button[type='submit']")

        # Wait for redirect back to channels list
        expect(page).to_have_url("**/dashboard/channels", timeout=10000)

        # Verify channel appears in the list
        expect(page.locator("table")).to_contain_text("Main PayBill Channel")
        expect(page.locator("table")).to_contain_text("174379")
        expect(page.locator("table")).to_contain_text("Sandbox")

        # Verify initial status is unverified
        expect(page.locator("text=Unverified")).to_be_visible()

    def test_channel_verification_workflow(self, page: Page):
        """Test channel verification workflow"""
        # Start from channels page with existing channel
        page.goto("/dashboard/channels")

        # Find and click verify on a channel
        verify_button = page.locator("text=Verify Channel").first
        expect(verify_button).to_be_visible()

        # Click verify
        verify_button.click()

        # Wait for verification to complete
        expect(page.locator(".toast")).to_contain_text("Channel verification started")

        # Verify status updated to verified
        expect(page.locator("text=Verified")).to_be_visible()

    def test_channel_url_registration_workflow(self, page: Page):
        """Test URL registration workflow"""
        # Start from channels page
        page.goto("/dashboard/channels")

        # Click register URLs on a verified channel
        register_button = page.locator("text=Register URLs").first
        expect(register_button).to_be_visible()

        register_button.click()

        # Wait for registration to complete
        expect(page.locator(".toast")).to_contain_text("URL registration started")

        # Verify status updated to URLs registered
        expect(page.locator("text=URLs Registered")).to_be_visible()


class TestSimulationWorkflowE2E:
    """End-to-end tests for payment simulation workflow"""

    def test_simulation_interface_access(self, page: Page):
        """Test accessing the simulation interface"""
        # Navigate to simulation page
        page.goto("/dashboard/channels/simulate")

        # Verify page loaded
        expect(page.locator("h1")).to_contain_text("Sandbox Simulation")
        expect(page.locator("text=Simulate Payment")).to_be_visible()
        expect(page.locator("text=Simulation Results")).to_be_visible()

    def test_simulation_form_validation(self, page: Page):
        """Test simulation form validation"""
        page.goto("/dashboard/channels/simulate")

        # Try to submit empty form
        page.click("button:has-text('Run Simulation')")

        # Should show validation errors or prevent submission
        # (Depending on HTML5 validation or JavaScript validation)

        # Fill partial form
        page.select_option("#channelId", "1")
        page.fill("#amount", "100.00")

        # Try to submit incomplete form
        page.click("button:has-text('Run Simulation')")

        # Should not proceed with incomplete data
        expect(page.locator("text=Simulation Results")).to_contain_text("Run a simulation to see results here")

    def test_successful_simulation_workflow(self, page: Page):
        """Test complete successful simulation workflow"""
        page.goto("/dashboard/channels/simulate")

        # Fill complete form
        page.select_option("#channelId", "1")
        page.fill("#amount", "100.00")
        page.fill("#customerPhone", "254712345678")
        page.fill("#billRefNumber", "TEST-SIMULATION-001")

        # Submit simulation
        page.click("button:has-text('Run Simulation')")

        # Wait for simulation to complete
        expect(page.locator("text=Simulation Results")).to_be_visible()
        expect(page.locator("text=Success")).to_be_visible()
        expect(page.locator("text=Transaction ID")).to_be_visible()

        # Verify simulation details
        expect(page.locator("text=KES 100.00")).to_be_visible()
        expect(page.locator("text=254712345678")).to_be_visible()
        expect(page.locator("text=TEST-SIMULATION-001")).to_be_visible()

    def test_failed_simulation_handling(self, page: Page):
        """Test handling of failed simulations"""
        page.goto("/dashboard/channels/simulate")

        # Fill form with invalid data (e.g., production channel)
        page.select_option("#channelId", "production_channel")
        page.fill("#amount", "100.00")
        page.fill("#customerPhone", "254712345678")

        page.click("button:has-text('Run Simulation')")

        # Should show error result
        expect(page.locator("text=Failed")).to_be_visible()
        expect(page.locator("text=Simulation only available in sandbox")).to_be_visible()


class TestAnalyticsWorkflowE2E:
    """End-to-end tests for analytics workflow"""

    def test_analytics_page_access(self, page: Page):
        """Test accessing the analytics page"""
        page.goto("/dashboard/channels/analytics")

        # Verify page loaded
        expect(page.locator("h1")).to_contain_text("Transaction Analytics")
        expect(page.locator("text=Total Transactions")).to_be_visible()
        expect(page.locator("text=Total Volume")).to_be_visible()
        expect(page.locator("text=Success Rate")).to_be_visible()

    def test_analytics_data_display(self, page: Page):
        """Test that analytics data is properly displayed"""
        page.goto("/dashboard/channels/analytics")

        # Check for analytics cards
        expect(page.locator("text=Total Transactions")).to_be_visible()
        expect(page.locator("text=Total Volume")).to_be_visible()
        expect(page.locator("text=Average Transaction")).to_be_visible()
        expect(page.locator("text=Success Rate")).to_be_visible()

        # Check for transaction table
        expect(page.locator("text=Recent Transactions")).to_be_visible()
        expect(page.locator("table")).to_be_visible()

        # Check for top customers section
        expect(page.locator("text=Top Customers")).to_be_visible()

    def test_analytics_filtering(self, page: Page):
        """Test analytics filtering functionality"""
        page.goto("/dashboard/channels/analytics")

        # Test channel filtering
        page.select_option("text=All Channels", "1")

        # Verify filter applied (mock data should reflect the filter)
        expect(page.locator("table")).to_contain_text("Main PayBill")

        # Test refresh functionality
        page.click("text=Refresh")

        # Verify refresh triggered (could check for loading state or data update)

    def test_transaction_details_view(self, page: Page):
        """Test viewing transaction details"""
        page.goto("/dashboard/channels/analytics")

        # Click on a transaction ID
        transaction_link = page.locator("text=TXN001").first
        if transaction_link.is_visible():
            transaction_link.click()

            # Should navigate to transaction details or show modal
            # This depends on the specific implementation

    def test_analytics_responsiveness(self, page: Page):
        """Test analytics page responsiveness"""
        page.goto("/dashboard/channels/analytics")

        # Test mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})

        # Should still show key information
        expect(page.locator("text=Total Transactions")).to_be_visible()
        expect(page.locator("text=Total Volume")).to_be_visible()

        # Test tablet viewport
        page.set_viewport_size({"width": 768, "height": 1024})

        # Should show more detailed layout
        expect(page.locator("text=Recent Transactions")).to_be_visible()
        expect(page.locator("text=Top Customers")).to_be_visible()


class TestErrorHandlingE2E:
    """End-to-end tests for error handling"""

    def test_network_error_handling(self, page: Page):
        """Test handling of network errors"""
        # This would require mocking network failures
        # In a real scenario, you might use browser dev tools or service worker

    def test_invalid_data_submission(self, page: Page):
        """Test submission of invalid data"""
        page.goto("/dashboard/channels/add")

        # Submit form without required fields
        page.click("button[type='submit']")

        # Should show validation errors
        # HTML5 validation should prevent submission or show errors

    def test_session_timeout_handling(self, page: Page):
        """Test handling of session timeout"""
        page.goto("/dashboard/channels")

        # Simulate session timeout (this might require backend cooperation)
        # Clear local storage or cookies

        # Try to perform action
        page.click("text=Add Channel")

        # Should redirect to login or show session expired message
        # expect(page).to_have_url("**/login")

    def test_permission_denied_scenarios(self, page: Page):
        """Test permission denied scenarios"""
        # Try to access channel management without proper permissions
        # This would require setting up different user roles

        # Should show access denied message or redirect


class TestPerformanceE2E:
    """Performance-related E2E tests"""

    def test_page_load_performance(self, page: Page):
        """Test page load performance"""
        start_time = time.time()

        page.goto("/dashboard/channels")
        page.wait_for_load_state("networkidle")

        end_time = time.time()
        load_time = end_time - start_time

        # Page should load within acceptable time
        assert load_time < 3.0, f"Page took {load_time:.2f}s to load, should be < 3s"

    def test_form_submission_performance(self, page: Page):
        """Test form submission performance"""
        page.goto("/dashboard/channels/simulate")

        # Fill form
        page.select_option("#channelId", "1")
        page.fill("#amount", "100.00")
        page.fill("#customerPhone", "254712345678")
        page.fill("#billRefNumber", "TEST-001")

        # Measure submission time
        start_time = time.time()
        page.click("button:has-text('Run Simulation')")
        page.wait_for_selector("text=Simulation Results", timeout=10000)
        end_time = time.time()

        submission_time = end_time - start_time

        # Simulation should complete within acceptable time
        assert submission_time < 5.0, f"Simulation took {submission_time:.2f}s, should be < 5s"

    def test_concurrent_user_simulation(self, browser: Browser):
        """Test concurrent user simulation"""
        # Create multiple browser contexts
        contexts = []
        pages = []

        for i in range(3):
            context = browser.new_context()
            page = context.new_page()
            contexts.append(context)
            pages.append(page)

            # Navigate all users to simulation page
            page.goto("/dashboard/channels/simulate")

        # Have all users submit simulations concurrently
        for page in pages:
            page.select_option("#channelId", "1")
            page.fill("#amount", "100.00")
            page.fill("#customerPhone", "254712345678")
            page.fill("#billRefNumber", f"CONCURRENT-TEST-{pages.index(page)}")

        # Submit all at once
        start_time = time.time()
        for page in pages:
            page.click("button:has-text('Run Simulation')")

        # Wait for all to complete
        for page in pages:
            page.wait_for_selector("text=Simulation Results", timeout=15000)

        end_time = time.time()
        total_time = end_time - start_time

        # All simulations should complete successfully
        for page in pages:
            expect(page.locator("text=Success")).to_be_visible()

        # Cleanup
        for context in contexts:
            context.close()


# Test Configuration
class TestConfiguration:
    """Configuration and setup tests"""

    def test_responsive_design(self, page: Page):
        """Test responsive design across different screen sizes"""
        page.goto("/dashboard/channels")

        # Test mobile
        page.set_viewport_size({"width": 375, "height": 667})
        expect(page.locator("h1")).to_be_visible()

        # Test tablet
        page.set_viewport_size({"width": 768, "height": 1024})
        expect(page.locator("table")).to_be_visible()

        # Test desktop
        page.set_viewport_size({"width": 1920, "height": 1080})
        expect(page.locator("text=Add Channel")).to_be_visible()

    def test_accessibility_compliance(self, page: Page):
        """Test accessibility compliance"""
        page.goto("/dashboard/channels")

        # Check for proper heading hierarchy
        expect(page.locator("h1")).to_be_visible()

        # Check for alt text on images (if any)
        # Check for proper form labels
        expect(page.locator("label[for='businessName']")).to_be_visible()

        # Check for keyboard navigation
        page.keyboard.press("Tab")
        # Should focus on interactive elements

    def test_cross_browser_compatibility(self, browser_name: str):
        """Test cross-browser compatibility"""
        # This test would run on different browsers (Chrome, Firefox, Safari)
        # Verify core functionality works across browsers
        pass


# Test Data Management
class TestDataManagement:
    """Test data management and cleanup"""

    def test_test_data_isolation(self, page: Page):
        """Ensure test data doesn't interfere between tests"""
        # Each test should start with clean state
        # No leftover data from previous tests
        pass

    def test_database_cleanup(self):
        """Ensure database is properly cleaned after tests"""
        # Rollback transactions
        # Reset sequences
        # Clean up test data
        pass


# Pytest Configuration
pytest_plugins = ["playwright.plugin"]

# Custom Markers
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.slow,
]

# Test Execution
if __name__ == "__main__":
    pytest.main([
        __file__,
        "--browser=chromium",
        "--headed=false",  # Run headless
        "--video=on",      # Record video
        "--slowmo=100",    # Slow down actions
        "-v"
    ])
