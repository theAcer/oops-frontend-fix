import { MpesaChannel } from "../app/dashboard/channels/page"

// Test that the types are properly defined
const testChannel: MpesaChannel = {
  id: 1,
  name: "Test Channel",
  type: "PayBill",
  shortcode: "174379",
  environment: "sandbox",
  status: "verified",
  urls_registered: true,
  receiving: false,
  created_at: "2024-01-15T10:30:00Z"
}

console.log("✅ MpesaChannel type is working correctly")
console.log("✅ Channels page should compile without errors")
