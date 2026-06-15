# WWC - Web Wallet for Verifiable Credentials

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Node](https://img.shields.io/badge/node-%3E%3D16-brightgreen.svg)](https://nodejs.org)
[![React](https://img.shields.io/badge/react-18.3.1-blue.svg)](https://reactjs.org)
[![Material-UI](https://img.shields.io/badge/Material--UI-6.2.0-blue.svg)](https://mui.com)

A modern, secure digital identity wallet for managing W3C Verifiable Credentials and VEIA-standard credentials. Built with React 18, AWS Cognito authentication, and designed for multi-tenant deployments.

## 🎯 What is WWC?

WWC (Web Wallet for Credentials) is a production-ready web application that enables:

- **Holders** to receive, store, and present verifiable credentials
- **Issuers** to create and issue digital credentials to holders
- **Verifiers** to request and validate credential presentations

Built on W3C Verifiable Credentials and VEIA trust framework standards, WWC provides a comprehensive solution for decentralized digital identity management with blockchain integration.

## ✨ Key Features

- 🔐 **Secure Authentication** - AWS Cognito with MFA, social login, and password recovery
- 📜 **W3C Verifiable Credentials** - Full support for W3C VC data model with JSON-LD
- 🔗 **Blockchain Integration** - Ethereum-based credential verification and immutability
- 🏢 **Multi-Tenant Architecture** - Customizable themes and configuration per client
- 🌍 **Internationalization** - Multi-language support (English, Spanish) with i18next
- ✍️ **Digital Signatures** - PAdES-compliant document signing
- 🗳️ **Balloting System** - Secure electronic voting capabilities
- 📊 **Dashboard & Analytics** - Comprehensive activity tracking and metrics
- 📱 **Responsive Design** - Material-UI components optimized for all devices

## 🚀 Quick Start

### Prerequisites

- Node.js ≥16.0.0
- npm ≥7.0.0
- AWS account with Cognito configured (or use mock mode)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd wwc

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your AWS Cognito credentials

# Start development server
npm start
```

The application will open at [http://localhost:3000](http://localhost:3000)

### Quick Commands

```bash
npm start              # Development mode
npm run build          # Production build
npm test               # Run tests
npm run lint:fix       # Fix code style issues
```

## 📚 Documentation

| Category | Description | Location |
|----------|-------------|----------|
| **Getting Started** | Setup guide, first steps | [docs/getting-started.md](docs/getting-started.md) |
| **Architecture** | System design, C4 diagrams, ADRs | [docs/architecture/](docs/architecture/) |
| **API Reference** | Service layer documentation | [docs/api/](docs/api/) |
| **How-To Guides** | Common tasks and workflows | [docs/how-to/](docs/how-to/) |
| **Operations** | Deployment, monitoring, troubleshooting | [docs/operations/](docs/operations/) |

📖 **Full documentation index:** [docs/index.md](docs/index.md)

### Key Documentation

- 🏗️ [Project Overview](docs/project-overview.md) - What WWC solves and how
- 🔑 [Authentication Implementation](docs/AUTH_IMPLEMENTATION.md) - AWS Cognito integration guide
- 🎨 [Multi-Tenant Architecture](docs/multi-tenant-architecture.md) - Client customization
- 🐛 [Troubleshooting Guide](docs/troubleshooting.md) - Common issues and solutions
- 🚢 [Deployment Guide](docs/deployment-guide.md) - Docker and production setup

## 🏗️ Technology Stack

### Core
- **React 18.3.1** - UI framework with concurrent features
- **Material-UI v6** - Component library and design system
- **React Router v6** - Client-side routing
- **i18next** - Internationalization with HTTP backend

### Authentication & Security
- **AWS Cognito** - User authentication and authorization
- **AWS SDK v3** - Cloud services integration
- **jose** - JWT operations and verification

### Standards & Blockchain
- **W3C Verifiable Credentials** - Standard credential format
- **VEIA Trust Framework** - JWT-based credential alternative
- **Ethers.js** - Ethereum blockchain integration
- **jsonld** - JSON-LD processing

### Development
- **React Testing Library** - Component testing
- **Jest** - Test runner
- **ESLint** - Code quality and style
- **Docker** - Containerization and deployment

## 🔧 Configuration

WWC uses environment variables for configuration. See [.env.example](.env.example) for all options.

### Required Variables

```bash
REACT_APP_AWS_COGNITO_USER_POOL_ID=your-user-pool-id
REACT_APP_AWS_COGNITO_CLIENT_ID=your-client-id
REACT_APP_API_URL=https://api.your-domain.com
```

### Optional Variables

```bash
REACT_APP_CLIENT_TYPE=CLIENT_B           # Multi-tenant client selection
REACT_APP_MOCK_API=true                  # Enable mock API for development
REACT_APP_DIGITAL_SIGNATURE=true         # Show/hide digital signature feature
```

📋 Complete configuration reference: [docs/environment-configuration.md](docs/environment-configuration.md)

## 🐳 Docker Deployment

```bash
# Build image
docker build -t wwc:latest \
  --build-arg REACT_APP_API_URL=https://api.your-domain.com \
  .

# Run container
docker run -p 80:80 wwc:latest
```

See [Deployment Guide](docs/deployment-guide.md) for production setup.

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch
```

See [Testing Guide](docs/testing-guide.md) for testing strategy and examples.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development workflow
- Code style guidelines
- Pull request process
- Testing requirements

## 🔒 Security

Security is critical for digital identity systems. If you discover a vulnerability:

- **DO NOT** open a public issue
- Review our [Security Policy](SECURITY.md)
- Report privately to the security team

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Project Structure

```
wwc/
├── src/
│   ├── app/              # Application bootstrap and routing
│   ├── components/       # Reusable UI components
│   ├── config/           # Configuration files
│   ├── context/          # React Context providers
│   ├── helpers/          # Utility functions
│   ├── layouts/          # Page layout components
│   ├── pages/            # Feature pages
│   └── services/         # API integration layer
├── public/               # Static assets
│   └── locales/          # Translation files
├── docs/                 # Documentation
├── scripts/              # Utility scripts
└── Dockerfile            # Container configuration
```

## 🔗 Related Projects

- **Sybol Backend API** - Backend services for WWC
- **Sybol Infrastructure** - AWS CDK infrastructure as code
- **PAdES Lambda** - Digital signature service

## 📞 Support

- 📖 Documentation: [docs/](docs/)
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/wwc/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-org/wwc/discussions)

## 🗺️ Roadmap

- [ ] Storybook component library
- [ ] E2E test suite with Playwright
- [ ] Offline mode with service workers
- [ ] Mobile native apps (React Native)
- [ ] DIDComm protocol support
- [ ] Advanced analytics dashboard

---

**Built with ❤️ by the Sybol Team**

For AI agents: See [llms.txt](llms.txt) for machine-readable project information.
