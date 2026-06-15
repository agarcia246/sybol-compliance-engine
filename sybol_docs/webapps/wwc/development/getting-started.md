# Getting Started with WWC

Welcome! This guide will take you from zero to a running WWC application in approximately **30 minutes**. By the end, you'll have the application running locally and understand the basic development workflow.

## Prerequisites

Before starting, ensure you have:

- **Node.js** ≥16.0.0 ([Download](https://nodejs.org/))
- **npm** ≥7.0.0 (comes with Node.js)
- **Git** for version control
- A **code editor** (VS Code recommended)
- **Terminal/Command Line** access

### Verify your installation

```bash
node --version  # Should show v16.0.0 or higher
npm --version   # Should show 7.0.0 or higher
```

## Step 1: Clone the Repository

First, clone the WWC repository to your local machine:

```bash
# Navigate to your projects directory
cd ~/Projects

# Clone the repository
git clone <repository-url> wwc
cd wwc
```

## Step 2: Install Dependencies

Install all required npm packages. This may take a few minutes:

```bash
npm install
```

**Troubleshooting:** If you encounter errors:
- Try clearing npm cache: `npm cache clean --force`
- Delete `node_modules` and `package-lock.json`, then run `npm install` again
- Ensure you're using Node.js 16 or higher

## Step 3: Configure Environment Variables

WWC requires configuration for AWS Cognito and backend services. Create your environment file:

```bash
# Copy the example environment file
cp .env.example .env
```

Now edit the `.env` file with your configuration:

```bash
# Open in your editor
code .env  # VS Code
# or
nano .env  # Terminal editor
```

### Option A: Using Mock API (Recommended for First Run)

For quick local testing without AWS setup:

```bash
REACT_APP_MOCK_API=true
REACT_APP_AWS_COGNITO_USER_POOL_ID=mock-pool-id
REACT_APP_AWS_COGNITO_CLIENT_ID=mock-client-id
REACT_APP_API_URL=http://localhost:3000
```

### Option B: Using Real AWS Cognito

If you have AWS Cognito configured:

```bash
REACT_APP_MOCK_API=false
REACT_APP_AWS_COGNITO_USER_POOL_ID=eu-west-1_YourPoolId
REACT_APP_AWS_COGNITO_CLIENT_ID=your-client-id-here
REACT_APP_API_URL=https://api.develop.wallet.sybol.id
```

**Finding your Cognito credentials:**
1. Log in to [AWS Console](https://console.aws.amazon.com/)
2. Navigate to **Cognito** service
3. Select your User Pool
4. User Pool ID is shown at the top
5. Go to **App Integration** → **App clients** for Client ID

## Step 4: Start the Development Server

Launch the application:

```bash
npm start
```

You should see output similar to:

```
Compiled successfully!

You can now view wwc in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.xyz:3000

Note that the development build is not optimized.
To create a production build, use npm run build.

webpack compiled successfully
```

The application will automatically open in your browser at [http://localhost:3000](http://localhost:3000).

## Step 5: Explore the Application

### Welcome Page

You should see the WWC welcome page with login options.

![WWC Welcome Page](images/welcome-page.png)

### Login (Mock Mode)

If using mock mode, you can login with any credentials:
- **Email:** test@example.com
- **Password:** Test123!

The mock authentication will accept any reasonably formatted credentials.

### Login (Real Cognito)

If using real AWS Cognito:
1. Click **Sign In**
2. Enter your Cognito user credentials
3. Complete MFA if enabled
4. You'll be redirected to the Dashboard

### Main Features to Explore

Once logged in, explore these key areas:

1. **Dashboard** (`/dashboard`)
   - View metrics and recent activity
   - Check notifications
   - See connected platforms

2. **Holder** (`/holder/credentials`)
   - View credentials you've received
   - Manage presentations

3. **Issuer** (`/entity/credentials`)
   - Issue new credentials to holders
   - View issued credentials

4. **Catalog** (`/catalog`)
   - Browse available credential types
   - View credential schemas

5. **Settings** (`/settings`)
   - Manage your profile
   - Update preferences
   - Change language (English/Spanish)

## Step 6: Make Your First Change

Let's verify everything works by making a small change:

### 6.1 Open the Dashboard Component

```bash
# Open in your editor
code src/pages/Dashboard/Dashboard.js
```

### 6.2 Modify the Welcome Message

Find the dashboard title (around line 50-60) and change it:

```javascript
// Before
<Typography variant="h4">Dashboard</Typography>

// After
<Typography variant="h4">My Custom Dashboard</Typography>
```

### 6.3 See Hot Reload in Action

Save the file (`Ctrl+S` or `Cmd+S`). The browser will automatically refresh, and you'll see your change immediately!

**Congratulations! 🎉** You've made your first modification to WWC.

## Step 7: Understand the Project Structure

Familiarize yourself with the key directories:

```
wwc/
├── src/
│   ├── app/                 # App initialization and routing
│   │   ├── App.js          # Main application component
│   │   └── DataRouter.js   # Route definitions
│   ├── pages/              # Feature pages
│   │   ├── Dashboard/      # Dashboard feature
│   │   ├── Holder/         # Holder credentials
│   │   └── Issuer/         # Issue credentials
│   ├── components/         # Reusable UI components
│   ├── services/           # API integration
│   │   ├── sybol.js       # Main API service
│   │   ├── cognito.js     # Authentication
│   │   ├── w3c.js         # W3C credentials
│   │   └── veia.js        # VEIA credentials
│   ├── context/           # React Context providers
│   │   ├── AuthContext.js # Authentication state
│   │   └── AppContext.js  # Global app state
│   ├── config/            # Configuration files
│   │   ├── routes.js      # Route configuration
│   │   └── config.js      # App configuration
│   └── helpers/           # Utility functions
├── public/
│   └── locales/           # Translation files (i18n)
│       ├── en/            # English translations
│       └── es/            # Spanish translations
└── docs/                  # Documentation (you are here!)
```

**For a complete breakdown:** See [Folder Structure](architecture/folder-structure.md)

## Step 8: Run Tests

Verify that tests pass:

```bash
npm test
```

Press `a` to run all tests, or `q` to quit.

**Note:** Some test files might be missing. This is normal for the current version. See [Testing Guide](testing-guide.md) to learn how to add tests.

## Step 9: Check Code Quality

Run the linter to check code style:

```bash
npm run lint
```

Auto-fix issues:

```bash
npm run lint:fix
```

## Common First-Time Issues

### Issue: Port 3000 Already in Use

**Error:** `Something is already running on port 3000`

**Solution:**
```bash
# Find and kill the process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use a different port
PORT=3001 npm start
```

### Issue: Module Not Found Errors

**Error:** `Cannot find module '@mui/material'`

**Solution:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Issue: Cognito Authentication Fails

**Error:** `User pool client does not exist`

**Solution:**
1. Verify your `.env` credentials are correct
2. Make sure User Pool and Client ID match
3. Try using `REACT_APP_MOCK_API=true` for local development

### Issue: Webpack Compilation Errors

**Error:** Various webpack errors

**Solution:**
```bash
# Clear webpack cache
rm -rf node_modules/.cache
npm start
```

## Next Steps

Now that you have WWC running, here's what to explore next:

### Learn the Fundamentals
- 📖 [Project Overview](project-overview.md) - Understand what WWC does
- 🏗️ [Architecture Overview](architecture/c4-context.md) - See how it's built
- 🔑 [Authentication Deep Dive](AUTH_IMPLEMENTATION.md) - Master AWS Cognito integration

### Start Developing
- ➕ [Add a New Page](how-to/add-new-page.md) - Create your first feature
- 🎨 [Customize the Theme](how-to/customize-client-theme.md) - Brand the application
- 🌐 [Add a New Language](how-to/add-new-language.md) - Extend i18n support

### Explore the API
- 🔌 [Sybol Service API](api/sybol-service.md) - Main backend integration
- 🔐 [Cognito Service API](api/cognito-service.md) - Authentication methods
- ✅ [W3C Service API](api/w3c-service.md) - Verifiable Credentials

### Contribute
- 🤝 [Contributing Guide](../CONTRIBUTING.md) - Join the development
- 🐛 [Report Issues](https://github.com/your-org/wwc/issues) - Help improve WWC

## Development Workflow

### Daily Development

```bash
# Pull latest changes
git pull origin main

# Install any new dependencies
npm install

# Start development server
npm start

# Make your changes...

# Check code quality
npm run lint:fix

# Commit your work
git add .
git commit -m "feat: add new feature"
```

### Useful Commands Reference

```bash
# Development
npm start              # Start dev server (localhost:3000)
npm run dev            # Start with dev environment preset
npm run sta            # Start with staging environment

# Build
npm run build          # Production build
npm run build:clientB  # Build for CLIENT_B tenant

# Code Quality
npm run lint           # Check code style
npm run lint:fix       # Auto-fix lint issues
npm test               # Run tests
npm test -- --coverage # Run with coverage report

# Internationalization
npm run exportLocale   # Export translations to XML
npm run importLocale   # Import translations from XML
```

## Getting Help

- 📖 **Documentation:** [Full documentation index](index.md)
- 🐛 **Issues:** [GitHub Issues](https://github.com/your-org/wwc/issues)
- 💬 **Questions:** [GitHub Discussions](https://github.com/your-org/wwc/discussions)
- ❓ **FAQ:** [Frequently Asked Questions](glossary/faq.md)
- 🔧 **Troubleshooting:** [Troubleshooting Guide](troubleshooting.md)

## What You've Learned

✅ How to set up the WWC development environment  
✅ Configure environment variables  
✅ Start the development server  
✅ Navigate the application  
✅ Make code changes with hot reload  
✅ Understand the project structure  
✅ Run tests and linting  

**You're now ready to start developing with WWC!** 🚀

---

**Next Tutorial:** [Creating Your First Credential Flow](tutorials/tutorial-02-create-credential-flow.md)

**Questions?** Check the [FAQ](glossary/faq.md) or [open a discussion](https://github.com/your-org/wwc/discussions).
