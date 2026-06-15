# Authentication Implementation Guide

This document describes the AWS Cognito authentication implementation added to the wwc application.

## Files Added

### 1. Cognito Service (`src/services/cognito.js`)
Complete AWS Cognito service layer providing:
- User registration and verification
- Authentication (sign in/sign out)
- Password recovery
- MFA setup (TOTP and Email)
- Token management
- JWT decoding
- Error handling with i18n keys

### 2. Authentication Context (`src/context/AuthContext.js`)
React Context provider managing global authentication state:
- User information
- Authentication tokens
- Loading state
- Authentication status
- Sign out functionality
- Auth state updates
- Automatic redirects for protected routes

### 3. Route Guard (`src/components/RouteGuard/RouteGuard.js`)
Navigation protection component:
- Prevents authenticated users from accessing login/register
- Tracks last visited route in sessionStorage
- Manages onboarding flow progression
- Smart redirects based on user state

## Integration

### App Structure
```
BrowserRouter
└── AppStateProvider
    └── ThemeProvider
        └── CookieManager
            └── AuthProvider
                └── RouteGuard
                    └── DataRouter
```

### Public Routes
Routes accessible without authentication (defined in AuthContext.js):
```javascript
const PUBLIC_ROUTES = [
  '/',
  '/login',
  '/register',
  '/forgot-password',
  '/reset-password',
  '/confirm-email',
  '/privacy-policy',
  '/terms-of-service',
  '/legal',
  '/cookies-policy'
];
```

## Configuration

### Environment Variables
Create a `.env` file based on `.env.example`:
```bash
REACT_APP_COGNITO_REGION=eu-west-1
REACT_APP_COGNITO_USER_POOL_ID=your-pool-id
REACT_APP_COGNITO_CLIENT_ID=your-client-id
```

### Customization

#### Update Public Routes
Edit `PUBLIC_ROUTES` in `src/context/AuthContext.js` to match your application's routes.

#### Update Flow Progression
Edit `FLOW_ORDER` in `src/components/RouteGuard/RouteGuard.js` to define your onboarding sequence:
```javascript
const FLOW_ORDER = [
  '/',
  '/register',
  '/mfa',
  '/kyb',
  '/review'
];
```

#### Change Redirect Destination
By default, unauthenticated users are redirected to `/register`. To change this, update the redirect in `AuthContext.js`:
```javascript
navigate('/register', { replace: true });
// Change to:
navigate('/login', { replace: true });
```

## Usage in Components

### Using the Auth Hook
```javascript
import { useAuth } from '../context/AuthContext';

function MyComponent() {
  const { user, isAuthenticated, signOut, updateAuth } = useAuth();

  const handleLogout = async () => {
    await signOut();
  };

  return (
    <div>
      {isAuthenticated && (
        <>
          <p>Welcome, {user?.email}</p>
          <button onClick={handleLogout}>Logout</button>
        </>
      )}
    </div>
  );
}
```

### Login Implementation
```javascript
import { signIn } from '../services/cognito';
import { useAuth } from '../context/AuthContext';

function LoginPage() {
  const { updateAuth } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (email, password) => {
    try {
      const result = await signIn(email, password);
      
      if (result.success) {
        updateAuth(); // Refresh auth state
        navigate('/dashboard');
      } else if (result.challengeName) {
        // Handle MFA challenge
        navigate('/mfa');
      }
    } catch (error) {
      console.error(error.message); // Will be an i18n key
    }
  };

  return <form onSubmit={handleSubmit}>...</form>;
}
```

### Registration Implementation
```javascript
import { signUp, confirmSignUp } from '../services/cognito';

// Step 1: Sign up
const handleSignUp = async (email, password, name) => {
  try {
    await signUp({ email, password, name });
    // Show verification code input
  } catch (error) {
    console.error(error.message); // i18n key like 'auth.error.userExists'
  }
};

// Step 2: Verify and auto-login
const handleVerify = async (email, code, password) => {
  try {
    const result = await confirmSignUp(email, code, password);
    if (result.authResult) {
      // User is automatically logged in
      updateAuth();
      navigate('/dashboard');
    }
  } catch (error) {
    console.error(error.message);
  }
};
```

## Error Handling

All Cognito errors are mapped to i18n translation keys. Add these translations to your translation files:

```json
{
  "auth": {
    "error": {
      "generic": "An error occurred. Please try again.",
      "userExists": "An account with this email already exists.",
      "userNotFound": "User not found.",
      "invalidCredentials": "Invalid email or password.",
      "invalidCode": "Invalid verification code.",
      "passwordLowercase": "Password must contain lowercase letters.",
      "passwordUppercase": "Password must contain uppercase letters.",
      "passwordNumeric": "Password must contain numbers.",
      "passwordSymbol": "Password must contain special characters.",
      "passwordLength": "Password must be at least 8 characters.",
      "codeMismatch": "Verification code does not match.",
      "codeExpired": "Verification code has expired.",
      "tooManyAttempts": "Too many attempts. Please try again later."
    }
  }
}
```

## Token Storage

- Tokens are stored in **sessionStorage** (cleared on tab close)
- To use localStorage for persistent sessions, update `cognito.js`:
  ```javascript
  // In signIn function, replace:
  sessionStorage.setItem('accessToken', tokens.accessToken);
  // with:
  localStorage.setItem('accessToken', tokens.accessToken);
  ```

## MFA Support

The implementation includes full TOTP (authenticator app) and Email MFA support:

```javascript
import { 
  setupAuthenticatorMFA, 
  completeAuthenticatorMFASetup 
} from '../services/cognito';

// Step 1: Get QR code
const { secretCode, qrCodeUrl } = await setupAuthenticatorMFA(accessToken);

// Step 2: Verify and enable
await completeAuthenticatorMFASetup(accessToken, verificationCode);
```

## Dependencies

Required npm packages (already installed):
- `@aws-sdk/client-cognito-identity-provider` - AWS Cognito SDK v3
- `react-router-dom` - For navigation and routing

## Next Steps

1. **Update environment variables** with your Cognito pool credentials
2. **Add auth translations** to your i18n files
3. **Create login/register pages** using the Cognito service methods
4. **Customize public routes** for your application
5. **Test authentication flow** end-to-end

## Security Notes

- Never commit `.env` file to version control
- Use `.env.example` as a template
- Tokens are cleared on sign out
- Session storage is cleared when browser tab closes
- All AWS Cognito communication is encrypted via HTTPS
