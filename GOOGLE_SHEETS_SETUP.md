# Google Sheets Integration Setup

Google Sheets delivery requires authentication. There are two ways to set this up:

## Option 1: Service Account (Recommended for Production)

### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API for your project

### Step 2: Create Service Account
1. Go to **IAM & Admin** > **Service Accounts**
2. Click **Create Service Account**
3. Enter a name (e.g., "Leadex Sheets Integration")
4. Click **Create and Continue**
5. Skip role assignment (click **Continue**)
6. Click **Done**

### Step 3: Create and Download Key
1. Click on the service account you just created
2. Go to the **Keys** tab
3. Click **Add Key** > **Create New Key**
4. Choose **JSON** format
5. Click **Create** - this downloads the credentials file
6. **Rename the file to `credentials.json`**
7. **Move it to your project root**: `/root/leadex-project/credentials.json`

### Step 4: Share Your Google Sheet
1. Open your Google Sheet
2. Click **Share** button (top right)
3. Paste the service account email (found in credentials.json as `client_email`)
4. Grant **Editor** access
5. Click **Share**

### Step 5: Test
- Try sending a lead manually
- Check the Google Sheet for the new row
- Check logs: `tail -f /tmp/leadex.log | grep -i sheet`

---

## Option 2: Google Apps Script Web App (Simple Alternative)

If you don't want to deal with service accounts, you can use a Google Apps Script webhook.

### Step 1: Open Your Google Sheet
1. Go to your Google Sheet
2. Click **Extensions** > **Apps Script**

### Step 2: Add Script Code
Replace any existing code with this:

```javascript
function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Leads');

    // Create Leads sheet if it doesn't exist
    if (!sheet) {
      sheet = SpreadsheetApp.getActiveSpreadsheet().insertSheet('Leads');
      // Add headers
      sheet.appendRow([
        'Lead ID', 'Mobile', 'Name', 'Email', 'Client',
        'Date', 'IP', 'Referrer', 'Geo', 'UTM'
      ]);
    }

    // Parse incoming data
    var data = JSON.parse(e.postData.contents);

    // Append the row
    sheet.appendRow(data.values);

    // Return success
    return ContentService.createTextOutput(JSON.stringify({
      'success': true,
      'message': 'Lead added to row ' + sheet.getLastRow()
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      'success': false,
      'error': error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}
```

### Step 3: Deploy as Web App
1. Click **Deploy** > **New deployment**
2. Click the gear icon ⚙️ next to "Select type"
3. Select **Web app**
4. Fill in:
   - **Description**: "Leadex Integration"
   - **Execute as**: Me
   - **Who has access**: Anyone
5. Click **Deploy**
6. **Copy the Web App URL** (looks like: `https://script.google.com/macros/s/...../exec`)

### Step 4: Configure in Leadex
1. Go to **Client Management** in Leadex admin
2. Edit your client
3. **UNCHECK** Google Sheets checkbox
4. **CHECK** Webhook checkbox
5. **Paste the Web App URL** in the Webhook URL field
6. Click **Save**

### Step 5: Test
- Try sending a lead manually
- Check the Google Sheet for the new row
- The lead data should appear instantly

---

## Troubleshooting

### "Credentials file not found"
- Make sure `credentials.json` exists at `/root/leadex-project/credentials.json`
- Check file permissions: `chmod 644 /root/leadex-project/credentials.json`

### "Permission denied" or "The caller does not have permission"
- Make sure you shared the sheet with the service account email
- The service account email is in credentials.json: `client_email` field

### Web App returns error
- Make sure you deployed as "Anyone can access"
- Check the Apps Script execution logs: **View** > **Logs** in Apps Script editor
- Make sure the sheet name is "Leads" or update the script

### Leads not appearing
- Check server logs: `tail -f /tmp/leadex.log | grep -i sheet`
- Try manual resend to test delivery
- Verify the client has Google Sheets or Webhook enabled

---

## Current Setup Status

Your Google Sheet ID: `1FWqI4kF59HKSRTE8Tk_O5SnStJw_Keb0K8-gUB1ZZCI`

**Recommendation**: Use Option 2 (Google Apps Script Web App) for quick setup without service account configuration.
