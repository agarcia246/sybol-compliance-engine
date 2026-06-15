# OnBoardingWeb

A modern React-based web application for SYBOL's KYB (Know Your Business) onboarding process. This project features a clean, modular architecture with comprehensive internationalization support, responsive layouts, and an innovative **Status Follow Sidebar** for real-time tracking of user progression through onboarding workflows.

## 📋 Table of Contents

- [🏗️ Project Architecture](#️-project-architecture)
- [🔄 Application State Management](#-application-state-management)
- [🏗️ Deployment Configuration](#️-deployment-configuration)
- [📊 Status Follow Sidebar](#-status-follow-sidebar)  
- [🌍 Internationalization (i18n)](#-internationalization-i18n)
- [🎨 Styling Architecture](#-styling-architecture)
- [📐 Layout Architecture](#-layout-architecture)
- [🗝️ Key Elements and Features](#️-key-elements-and-features)
- [📦 Dependencies and Libraries](#-dependencies-and-libraries)
- [🚀 Getting Started](#-getting-started)
- [🔧 Configuration](#-configuration)
- [🌟 Best Practices](#-best-practices)

## 🏗️ Project Architecture

### File Structure

```text
OnBoardingWeb/
├── public/
│   ├── images/
│   │   └── logo_dark.png          # Brand logo assets
│   └── locales/
│       ├── en/
│       │   └── translation.json   # English translations
│       └── es/
│           └── translation.json   # Spanish translations
├── src/
│   ├── app/
│   │   └── DataRouter.js           # Main routing configuration
│   ├── components/
│   │   ├── Header/
│   │   │   ├── Header.js           # Main header component
│   │   │   ├── Header.css          # Header styles
│   │   │   └── index.js            # Export file
│   │   ├── Footer/
│   │   │   ├── Footer.js           # Main footer component
│   │   │   ├── Footer.css          # Footer styles
│   │   │   └── index.js            # Export file
│   │   └── Sidebar/
│   │       ├── Sidebar.js          # Status follow sidebar component
│   │       ├── Sidebar.css         # Sidebar styles and animations
│   │       └── index.js            # Export file
│   ├── context/
│   │   └── AppContext.js           # Global application state context
│   ├── hooks/
│   │   └── useSidebarStatus.js     # Custom hook for sidebar status management
│   ├── layouts/
│   │   ├── header+main+footer.js       # Main layout component
│   │   ├── header+main+footer.css      # Layout positioning styles
│   │   ├── header+sidebar+main+footer.js # Sidebar layout component
│   │   └── header+sidebar+main+footer.css # Sidebar layout styles
│   └── pages/
│       ├── Welcome/
│       │   ├── Welcome.js          # Welcome page component
│       │   ├── Welcome.css         # Welcome page styles
│       │   └── index.js            # Export file
│       ├── Kyb/
│       │   ├── Kyb.js              # KYB verification page
│       │   ├── Kyb.css             # KYB page styles
│       │   └── index.js            # Export file
│       ├── Register/
│       │   ├── Register.js         # User registration page
│       │   ├── Register.css        # Registration page styles
│       │   └── index.js            # Export file
│       ├── Mfa/
│       │   ├── Mfa.js              # Multi-factor authentication page
│       │   ├── Mfa.css             # MFA page styles
│       │   └── index.js            # Export file
│       ├── TermsOfService/
│       │   ├── TermsOfService.js   # Terms of service page
│       │   ├── TermsOfService.css  # Terms page styles
│       │   └── index.js            # Export file
│       ├── PrivacyPolicy/
│       │   ├── PrivacyPolicy.js    # Privacy policy page
│       │   ├── PrivacyPolicy.css   # Privacy page styles
│       │   └── index.js            # Export file
│       ├── ExampleSidebarPage/
│       │   ├── ExampleSidebarPage.js # Sidebar demo page
│       │   ├── ExampleSidebarPage.css # Demo page styles
│       │   └── index.js            # Export file
│       └── StatusSidebarExample/
│           ├── StatusSidebarExample.js # Advanced sidebar example
│           └── index.js            # Export file
├── package.json
├── config-overrides.js            # Webpack configuration override
├── .gitignore
└── README.md
```

### Architecture Overview

The project follows a three-tier architecture pattern with a modular, folder-based structure:

#### 1. Layout Layer (`/layouts`)

- **Purpose**: Defines the overall page structure and positioning
- **Responsibility**: Header, main content, and footer positioning
- **Key Features**:
  - Fixed header and footer positioning
  - Responsive viewport management
  - CSS-only styling (no colors/fonts, only positioning)
  - Dynamic Content Centering: Automatic horizontal centering of main content area
  - Smooth transitions during window resizing

#### 2. Page Layer (`/pages`)

- **Purpose**: Business logic and page-specific functionality
- **Responsibility**: Data handling, user interactions, and page composition
- **Structure**: Each page is organized in its own folder with component and styles

#### 3. Component Layer (`/components`)

- **Purpose**: Reusable UI components
- **Responsibility**: Isolated functionality and styling
- **Structure**: Each component has its own folder with JS, CSS, and export files

### Component Structure Pattern

Each component follows this consistent pattern:

```text
ComponentName/
├── ComponentName.js    # React component logic
├── ComponentName.css   # Component-specific styles
└── index.js           # Clean export interface
```

## 🔄 Application State Management

The project implements a simple, centralized state management system using React Context for sharing data across all components during the onboarding process.

### State Management Architecture

#### Context Provider (`/src/context/AppContext.js`)

- **Purpose**: Centralized state management for the entire application
- **Approach**: React Context API (simplest solution)
- **Scope**: Application-wide state persistence across page navigation

#### State Structure

```javascript
const appState = {
  // User registration data
  userRegistration: {
    name: '',
    company: '',
    email: '',
    isRegistered: false
  },
  
  // MFA setup status
  mfaSetup: {
    method: null,           // 'authenticator' | 'email' | null
    isCompleted: false
  },
  
  // KYB verification status
  kybVerification: {
    isStarted: false,
    isCompleted: false
  },
  
  // Sidebar status items (shared across all pages)
  sidebarItems: [],
  
  // Current page/step tracking
  currentStep: 'welcome'    // 'welcome' | 'register' | 'mfa' | 'kyb'
};
```

### Usage

#### Accessing State

```javascript
import { useAppState } from '../../context/AppContext';

const MyComponent = () => {
  const { 
    appState, 
    updateUserRegistration, 
    addSidebarItem,
    setCurrentStep 
  } = useAppState();

  // Access any state value
  customLog(appState.userRegistration.name);
  customLog(appState.currentStep);
  
  return <div>...</div>;
};
```

#### Available Functions

- **`updateUserRegistration(userData)`** - Update registration information
- **`updateMfaSetup(mfaData)`** - Update MFA setup data
- **`updateKybVerification(kybData)`** - Update KYB verification status
- **`addSidebarItem(item)`** - Add or update sidebar progress items
- **`clearSidebarItems()`** - Clear all sidebar items
- **`setCurrentStep(step)`** - Update current step/page
- **`resetAppState()`** - Reset entire application state

#### Example Implementation

```javascript
const Register = () => {
  const { appState, updateUserRegistration, addSidebarItem } = useAppState();
  
  const handleSubmit = (formData) => {
    // Save to global state
    updateUserRegistration({
      name: formData.name,
      company: formData.company,
      email: formData.email,
      isRegistered: true
    });
    
    // Update progress in sidebar
    addSidebarItem({
      title: 'Registration',
      status: 'completed',
      icon: '✓',
      timestamp: new Date().toLocaleTimeString()
    });
    
    navigate('/mfa');
  };
};
```

### State Management Benefits

- **Persistent State**: Data survives page navigation and component unmounts
- **Shared Data**: All components can access and update the same information
- **Simple API**: Easy-to-use helper functions for common operations
- **Sidebar Integration**: Automatic sidebar progress tracking across pages
- **No External Dependencies**: Uses only React's built-in Context API

## 🏗️ Deployment Configuration

The Infrastructure Setup page collects and stores comprehensive deployment configuration data. When a user completes the deployment process, all selected options are stored in `localStorage` under the key `sybol_deployment_config`.

### Configuration Structure

The deployment configuration follows this structured format:

```javascript
{
  // Pricing Tier Selection
  "selectedTier": "growth",              // "basic" | "growth" | "enterprise"
  
  // Instance Configuration
  "instanceName": "my-sybol-instance",   // User-defined instance name
  "cloudProvider": "aws",                // "aws" | "gcp" | "azure"
  "region": "eu-west-1",                 // Selected deployment region
  "tags": [                              // Resource tags array
    {
      "key": "Environment",
      "value": "Production"
    },
    {
      "key": "Team", 
      "value": "DevOps"
    }
  ],
  
  // Quick Setup Options
  "preloadCredentials": true,            // Boolean: Preload API credentials
  "generateWorkflow": false,             // Boolean: Generate CI/CD workflow
  
  // Metadata
  "timestamp": "2025-01-27T10:30:00.000Z", // ISO timestamp of deployment
  "userId": "user_12345"                 // User ID from AppContext (or 'anonymous')
}
```

### Configuration Storage

The deployment configuration is automatically stored when the user clicks "Deploy":

- **Storage Location**: `localStorage` with key `sybol_deployment_config`
- **Format**: JSON string that can be parsed back to the configuration object
- **Persistence**: Survives browser sessions and page refreshes
- **Retrieval**: Use `getStoredDeploymentConfig()` helper function

### Usage Example

```javascript
// Retrieving stored deployment configuration
const getStoredDeploymentConfig = () => {
  try {
    const stored = localStorage.getItem('sybol_deployment_config');
    return stored ? JSON.parse(stored) : null;
  } catch (error) {
    console.error('Error retrieving deployment config:', error);
    return null;
  }
};

// Example usage
const config = getStoredDeploymentConfig();
if (config) {
  customLog(`Instance: ${config.instanceName}`);
  customLog(`Tier: ${config.selectedTier}`);
  customLog(`Provider: ${config.cloudProvider}`);
  customLog(`Region: ${config.region}`);
}
```

### Integration Points

- **API Calls**: Use this configuration for actual infrastructure provisioning
- **Billing**: Reference `selectedTier` for pricing calculations
- **Monitoring**: Use `tags` for resource tracking and organization
- **User Dashboard**: Display deployment status and configuration details
- **Support**: Include configuration in support tickets for troubleshooting

## 📊 Status Follow Sidebar

The project includes a sophisticated **Status Follow Sidebar** that tracks user progression through onboarding steps. This component displays a stack-based timeline where each step is added to the bottom as the user progresses.

### Architecture

#### Core Components

1. **Sidebar Component** (`/components/Sidebar/Sidebar.js`)
   - Accepts `statusItems` prop as external array
   - Renders vertical timeline with status indicators
   - Displays connecting lines between progress steps
   - Responsive design with mobile optimizations

2. **Status Management Hook** (`/hooks/useSidebarStatus.js`)
   - Manages status items state and operations
   - Provides methods for adding, updating, and completing items
   - Auto-generates IDs and timestamps
   - Handles auto-progression logic

### Status Item Structure

Each status item follows this simplified schema:

```javascript
const statusItem = {
  id: "auto-generated-id",        // Unique identifier (auto-generated)
  title: "Step Title",            // Primary display text
  icon: "🏠",                    // Visual indicator (emoji/icon)
  status: "pending",              // Current state
  timestamp: "2025-08-06..."      // Auto-generated timestamp
};
```

### Status States

The sidebar supports five distinct status states with visual coding:

- **`pending`** - ⚫ Gray indicator for upcoming steps
- **`active`** - 🔵 Blue indicator with glow effect for current step
- **`completed`** - 🟢 Green indicator for finished steps
- **`error`** - 🔴 Red indicator for failed steps
- **`warning`** - 🟡 Yellow indicator for skipped/cautionary steps

### Implementation Example

#### Basic Usage

```javascript
import { useSidebarStatus } from '../hooks/useSidebarStatus';
import Sidebar from '../components/Sidebar';
import SidebarLayout from '../layouts/header+sidebar+main+footer';

const MyPage = () => {
  const { statusItems, addStatusItem, completeItem } = useSidebarStatus();
  
  // Add status when component mounts
  useEffect(() => {
    const stepId = addStatusItem({
      title: "Document Upload",
      icon: "📎",
      status: "active"
    });
    
    // Later, complete the step
    setTimeout(() => completeItem(stepId), 5000);
  }, [addStatusItem, completeItem]);
  
  return (
    <SidebarLayout
      sidebarComponent={<Sidebar statusItems={statusItems} />}
      contentComponent={<MyContent />}
      // ... other props
    />
  );
};
```

#### Available Hook Methods

```javascript
const {
  statusItems,        // Array of current status items
  addStatusItem,      // (item) => id - Add new item to bottom
  updateStatusItem,   // (id, updates) => void - Update existing item
  completeItem,       // (id) => void - Mark as completed, activate next
  removeStatusItem,   // (id) => void - Remove specific item
  clearStatusItems,   // () => void - Clear all items
  getActiveItem,      // () => item - Get currently active item
  setStatusItems      // (items) => void - Replace all items
} = useSidebarStatus(initialItems);
```

### Auto-Progression Logic

The sidebar implements intelligent auto-progression:

1. **New items** are added with `pending` status by default
2. **Active items** are highlighted with special styling
3. **Completing an item** automatically:
   - Marks the item as `completed`
   - Finds the next `pending` item
   - Sets the next item to `active` status
   - Updates timestamps

### Responsive Design

The sidebar adapts to different screen sizes:

- **Desktop (>768px)**: Fixed sidebar with full content display
- **Tablet (≤768px)**: Collapsible sidebar with overlay
- **Mobile (≤480px)**: Full-width overlay with touch-optimized indicators

### Key Benefits

1. **Stack-based Progression**: Items stack chronologically (newest at bottom)
2. **External Injection**: Each page controls its own status items
3. **Visual Timeline**: Connected progress indicators show progression
4. **Real-time Updates**: Immediate visual feedback for status changes
5. **Persistent State**: Status maintained throughout user session
6. **Accessibility**: ARIA labels and semantic markup
7. **Mobile Optimized**: Touch-friendly interactions and responsive layout

### Demo Pages

- **`/example-sidebar`** - Interactive demo with add/complete/clear controls
- **Status integration examples** in onboarding flow pages

## 🌍 Internationalization (i18n)

The application supports **three language modes**:

- **English (EN)**: Full English translations
- **Spanish (ES)**: Full Spanish translations  
- **Developer Mode (DEV)**: Shows translation keys for marketing teams

### Language Features

- **Dynamic Language Switching**: Click the language toggle button in the header to cycle through EN → ES → DEV → EN
- **Persistent Language Selection**: Language preference is saved in session storage
- **Real-time Updates**: All text updates immediately when language is changed
- **Translation Key Visibility**: DEV mode shows `{{translation.key.path}}` format for easy identification

### Dev Mode for Marketing Teams

Dev mode provides a special interface for marketing teams to:

- **Identify Translation Keys**: See exactly which translation key corresponds to each text element
- **Visual Indicators**: Orange theme with dashed borders and warning banner when active
- **Translation Management**: Easily locate and update content in translation files

See the [Marketing Translation Guide](./MARKETING_TRANSLATION_GUIDE.md) for detailed instructions.

### Translation File Structure

```text
public/locales/
├── en/translation.json     # English translations
├── es/translation.json     # Spanish translations
└── dev/translation.json    # Translation keys (auto-generated)
```

### Adding New Translations

1. Add the key-value pair to both `en/translation.json` and `es/translation.json`
2. Use the key in your component: `{t('your.new.key')}`
3. The dev translation file will automatically show the key path
