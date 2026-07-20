# WhatsApp Integration Setup Guide

## Current Status
✅ **WhatsApp API credentials configured in system**
- META_ACCESS_TOKEN: Configured
- META_PHONE_NUMBER_ID: Configured
- META_BUSINESS_ACCOUNT_ID: Configured
- META_VERIFY_TOKEN: Configured

❌ **Missing**: Client-level WhatsApp configuration

## What You Need

WhatsApp Business API integration requires a Meta Business Account with WhatsApp Business Platform access.

### Prerequisites
1. Meta Business Account
2. WhatsApp Business Platform access
3. A phone number for WhatsApp Business
4. Verified Business Account

## Step-by-Step Setup

### Step 1: Meta Business Account Setup

If you haven't already:

1. Go to [Meta Business Suite](https://business.facebook.com/)
2. Create or select your Business Account
3. Navigate to **Business Settings**

### Step 2: WhatsApp Business Platform Setup

1. In Business Settings, go to **Accounts** > **WhatsApp Accounts**
2. Click **Add** to create a new WhatsApp Business Account
3. Follow the setup wizard:
   - Choose your business phone number
   - Verify the phone number (you'll receive an SMS code)
   - Accept WhatsApp Business Terms

### Step 3: Get Your API Credentials

You need 4 pieces of information:

#### 1. **Phone Number ID**
- Go to **WhatsApp** > **API Setup**
- Copy the **Phone Number ID** (looks like: `123456789012345`)
- This is already set in your system: `META_PHONE_NUMBER_ID`

#### 2. **WhatsApp Business Account ID**
- In **WhatsApp Manager**, find your **WhatsApp Business Account ID**
- This is already set: `META_BUSINESS_ACCOUNT_ID`

#### 3. **Access Token**
- Go to **System Users** in Business Settings
- Create a System User or select existing
- Click **Generate New Token**
- Select permissions:
  - ✅ `whatsapp_business_messaging`
  - ✅ `whatsapp_business_management`
- Copy the token - This is already set: `META_ACCESS_TOKEN`

#### 4. **Webhook Verify Token**
- Create a random string (e.g., `my_webhook_verify_token_2024`)
- Save it securely - This is already set: `META_VERIFY_TOKEN`

### Step 4: Configure Webhooks

1. In **WhatsApp** > **Configuration**
2. Click **Edit** next to Webhook
3. Set Callback URL: `http://213.21.235.48:8000/api/webhooks/whatsapp`
4. Set Verify Token: Use the same token from Step 3.4
5. Subscribe to webhook fields:
   - ✅ `messages`
   - ✅ `message_status`

### Step 5: Test Your Setup

Run this test command:

```bash
cd /root/leadex-project
source venv/bin/activate
python3 << 'EOF'
from app.services.delivery.whatsapp_delivery import WhatsAppDeliveryService
from app.core.config import settings

# Test message
result = WhatsAppDeliveryService.deliver(
    phone_number="+1234567890",  # Replace with your test number
    message="Test message from Leadex",
    whatsapp_token=settings.META_ACCESS_TOKEN,
    whatsapp_phone_id=settings.META_PHONE_NUMBER_ID
)

print(f"Success: {result['success']}")
print(f"Status: {result['status_code']}")
print(f"Response: {result['response_body']}")
EOF
```

### Step 6: Configure a Client for WhatsApp Delivery

Currently, the system sends WhatsApp notifications to the configured phone number. To enable WhatsApp delivery:

**Option 1: Use Phone Number from Client Model**
```python
# In admin panel, when creating/editing client
client.phone_number = "+1234567890"  # Client's WhatsApp number
```

**Option 2: Add WhatsApp-Specific Fields (Requires DB Migration)**

Add to Client model:
```python
whatsapp_enabled = Column(Boolean, default=False)
whatsapp_phone = Column(String(50), nullable=True)
```

## How WhatsApp Delivery Works

### Message Format
When a lead is sent via WhatsApp, the client receives:

```
🎯 *New Lead for [Client Name]*

📱 Mobile: +1234567890
👤 Name: John Doe
📧 Email: john@example.com

🆔 Lead ID: abc-123-def
📅 Date: 2024-12-17 10:30:00
```

### Delivery Flow
1. Lead assigned to client
2. System checks if client should receive via WhatsApp
3. Formats message using `WhatsAppDeliveryService.format_message()`
4. Sends via Meta Business API
5. Logs delivery status

## Current System Configuration

Your system has these settings in `/root/leadex-project/app/core/config.py`:

```python
# Meta WhatsApp Business API
META_ACCESS_TOKEN: str = "[CONFIGURED]"
META_PHONE_NUMBER_ID: str = "[CONFIGURED]"
META_BUSINESS_ACCOUNT_ID: str = "[CONFIGURED]"
META_VERIFY_TOKEN: str = "[CONFIGURED]"
```

## Troubleshooting

### Error: "Invalid phone number"
- Phone numbers must be in E.164 format: `+[country code][number]`
- Example: `+971501234567` (UAE), `+966501234567` (Saudi Arabia)

### Error: "Message failed to send"
- Check if the phone number is registered with WhatsApp
- Verify your access token hasn't expired
- Check Meta Business Manager for account status

### Error: "Permission denied"
- Verify your access token has `whatsapp_business_messaging` permission
- Check if your Business Account is verified

### No messages received
- Check if the recipient phone number has WhatsApp installed
- Verify the phone number format (E.164)
- Check WhatsApp Business Manager > Message Logs

## Production Checklist

Before going live:

- [ ] Meta Business Account verified
- [ ] WhatsApp Business Account approved
- [ ] Phone number verified
- [ ] Access token has correct permissions
- [ ] Webhook configured and verified
- [ ] Test messages sent successfully
- [ ] Message templates approved (if using templates)
- [ ] Rate limits understood (1000 messages/day for tier 1)

## Rate Limits

WhatsApp Business API has tiered rate limits:

- **Tier 1**: 1,000 unique customers/day
- **Tier 2**: 10,000 unique customers/day
- **Tier 3**: 100,000 unique customers/day

Your tier increases automatically based on message quality and volume.

## Next Steps

1. Verify your current credentials work with a test message
2. Decide if you want to add WhatsApp-specific fields to Client model
3. Configure which clients should receive WhatsApp notifications
4. Test end-to-end delivery flow

## Support

- Meta WhatsApp Business Docs: https://developers.facebook.com/docs/whatsapp
- WhatsApp Business Platform: https://business.whatsapp.com/
