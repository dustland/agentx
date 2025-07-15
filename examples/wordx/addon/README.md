# WordX Office.js Add-in

This is the Office.js add-in component for WordX that integrates with Microsoft Word.

## Setup

The add-in uses a simple static file server instead of the deprecated `office-addin-dev-server`.

### Install Dependencies

```bash
pnpm install  # or npm install
```

### Generate HTTPS Certificates (Recommended)

Office Add-ins work best with HTTPS. Generate local certificates:

```bash
pnpm run generate-cert  # or npm run generate-cert
```

This will create `localhost.crt` and `localhost.key` files for HTTPS development.

### Start the Server

With HTTPS (recommended):

```bash
pnpm start  # or npm start
```

Without HTTPS (fallback):

```bash
pnpm run start:http  # or npm run start:http
```

The add-in will be served at:

- HTTPS: `https://localhost:7778`
- HTTP: `http://localhost:7778`

## Files

- `manifest.xml` - Office Add-in manifest file
- `taskpane.html` - Main UI for the task pane
- `src/taskpane.js` - JavaScript code for the add-in
- `assets/` - Icons and images
- `function-file/` - Function file for command execution

## Loading in Word

1. Open Microsoft Word
2. Go to **Insert** → **My Add-ins** → **Upload My Add-in**
3. Browse and select the `manifest.xml` file
4. The WordX add-in will appear in the ribbon

## Development

The add-in communicates with the backend API at `http://localhost:7779`. Make sure the backend is running before using the add-in.

## Troubleshooting

- **Certificate errors**: If you see HTTPS certificate warnings, you may need to trust the generated certificate in your system
- **CORS issues**: Ensure the backend has proper CORS configuration for the add-in origin
- **Add-in not loading**: Check that the manifest URLs match your server configuration
