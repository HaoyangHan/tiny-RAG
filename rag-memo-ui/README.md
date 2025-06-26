# TinyRAG v1.4.1 Frontend - Next.js UI

**Modern React Frontend for TinyRAG Platform**

A comprehensive Next.js 14 frontend providing a complete user interface for the TinyRAG platform, featuring project management, document processing, element creation, and real-time monitoring.

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Backend API** running on `http://localhost:8000`
- **Modern Browser** (Chrome, Firefox, Safari, Edge)

### 1. Install Dependencies

```bash
cd rag-memo-ui
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

### 3. Access the Frontend

Open your browser and navigate to:

**🌐 Frontend URL**: [http://localhost:3000](http://localhost:3000)

## 📱 Application Pages & Features

### 🏠 **Main Application Routes**

| **Route** | **Description** | **Features** |
|-----------|-----------------|--------------|
| **`/`** | Landing Page | Authentication forms, welcome interface |
| **`/dashboard`** | Main Dashboard | Project overview, statistics, quick actions |
| **`/projects`** | Project Management | Create, list, filter, and manage projects |
| **`/projects/create`** | Project Creation | Multi-step project wizard |
| **`/projects/[id]`** | Project Details | Detailed project view with tabs |
| **`/documents`** | Document Upload | Drag & drop file upload with progress |
| **`/elements`** | Element Management | Template and tool creation |
| **`/elements/create`** | Element Creation | Type-specific element forms |
| **`/generations`** | Generation Monitoring | Real-time execution tracking |
| **`/generations/[id]`** | Generation Details | Detailed generation inspection |
| **`/evaluations`** | Quality Assessment | LLM evaluation results |
| **`/testing`** | API Test Suite | Built-in API testing interface |

### 🔐 **Authentication Flow**

1. **Landing Page** (`/`) - Choose to login or register
2. **Registration** - Create new account with email/username/password
3. **Login** - Authenticate with email/username and password
4. **Dashboard** - Automatic redirect after successful authentication
5. **Logout** - Secure session termination

### 🎨 **UI Components & Design**

- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS for responsive design
- **Components**: Radix UI for accessible, modern components
- **Icons**: Heroicons for consistent iconography
- **Typography**: Inter font for optimal readability
- **Theme**: Light/dark mode support (planned)

## 🛠️ Development

### Available Scripts

```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Type checking
npm run type-check

# Linting
npm run lint

# Linting with auto-fix
npm run lint:fix
```

### Project Structure

```
rag-memo-ui/
├── src/
│   ├── app/                    # Next.js 14 App Router
│   │   ├── dashboard/         # Dashboard pages
│   │   ├── projects/          # Project management
│   │   ├── documents/         # Document upload
│   │   ├── elements/          # Element management
│   │   ├── generations/       # Generation tracking
│   │   └── evaluations/       # Evaluation results
│   ├── components/            # Reusable UI components
│   │   ├── auth/             # Authentication components
│   │   ├── layout/           # Layout components
│   │   ├── projects/         # Project-specific components
│   │   ├── documents/        # Document components
│   │   ├── elements/         # Element components
│   │   ├── generations/      # Generation components
│   │   ├── evaluations/      # Evaluation components
│   │   ├── common/           # Common components
│   │   └── ui/               # Base UI components
│   ├── services/             # API client and services
│   ├── stores/               # State management (Zustand)
│   ├── types/                # TypeScript type definitions
│   ├── hooks/                # Custom React hooks
│   └── utils/                # Utility functions
├── public/                   # Static assets
└── docs/                     # Documentation
```

### Key Technologies

- **Next.js 14**: React framework with App Router
- **TypeScript**: Full type safety
- **Tailwind CSS**: Utility-first CSS framework
- **Radix UI**: Accessible component primitives
- **Zustand**: Lightweight state management
- **Axios**: HTTP client for API communication
- **React Hook Form**: Form handling and validation

## 🔌 API Integration

### Backend Configuration

The frontend expects the TinyRAG API to be running on:

```
API Base URL: http://localhost:8000
Health Check: http://localhost:8000/health
Documentation: http://localhost:8000/docs
```

### Authentication

- **JWT Tokens**: Stored in localStorage
- **Auto-refresh**: Automatic token renewal
- **Interceptors**: Axios interceptors for auth headers
- **Error Handling**: Automatic logout on auth failures

### API Client Features

- **Centralized Configuration**: Single API client setup
- **Type Safety**: Full TypeScript integration
- **Error Handling**: Comprehensive error responses
- **Loading States**: Built-in loading indicators
- **Retry Logic**: Automatic retry for failed requests

## 🎯 Key Features

### 📊 **Dashboard**
- Project statistics and overview
- Recent activity timeline
- Quick action buttons
- User profile management

### 🏗️ **Project Management**
- Create projects with different tenant types
- List and filter projects
- Project collaboration features
- Detailed project views with tabs

### 📄 **Document Processing**
- Drag & drop file upload
- Multiple file format support
- Upload progress tracking
- Batch processing capabilities

### 🧩 **Element System**
- Create prompt templates
- MCP configuration management
- Agentic tool definitions
- Template execution interface

### ⚡ **Real-time Features**
- Generation progress tracking
- Live status updates
- WebSocket integration (planned)
- Notification system

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file in the frontend directory:

```bash
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# App Configuration
NEXT_PUBLIC_APP_NAME=TinyRAG
NEXT_PUBLIC_APP_VERSION=1.4.1

# Feature Flags
NEXT_PUBLIC_ENABLE_TESTING=true
NEXT_PUBLIC_ENABLE_ANALYTICS=false
```

### Customization

- **Themes**: Modify `tailwind.config.js` for custom themes
- **Components**: Extend base components in `src/components/ui/`
- **API**: Configure endpoints in `src/services/api.ts`
- **Types**: Add custom types in `src/types/index.ts`

## 🚀 Production Deployment

### Build for Production

```bash
# Create optimized production build
npm run build

# Start production server
npm start
```

### Docker Deployment

The frontend is included in the main TinyRAG Docker setup:

```bash
# From project root
./scripts/start-tinyrag.sh

# Frontend will be available at http://localhost:3000
```

### Deployment Platforms

- **Vercel**: Recommended for Next.js applications
- **Netlify**: Static site deployment
- **Docker**: Container-based deployment
- **Traditional Hosting**: Any Node.js hosting provider

## 🔍 Testing

### Manual Testing

1. **Start Backend**: Ensure API is running on port 8000
2. **Start Frontend**: Run `npm run dev`
3. **Open Browser**: Navigate to `http://localhost:3000`
4. **Test Authentication**: Register/login with test credentials
5. **Test Features**: Navigate through all main pages

### Test User Credentials

```
Email: tester3@example.com
Username: tester3
Password: TestPassword123!
```

### Built-in Testing

- **API Test Suite**: Available at `/testing` route
- **Component Testing**: Jest and React Testing Library
- **Type Checking**: TypeScript compiler validation
- **Linting**: ESLint for code quality

## 🤝 Contributing

1. **Follow Standards**: Adhere to `.cursorrules` in project root
2. **Type Safety**: All components must be fully typed
3. **Component Structure**: Use consistent component patterns
4. **Testing**: Add tests for new features
5. **Documentation**: Update README for significant changes

### Code Style

- **TypeScript**: Strict mode enabled
- **ESLint**: Configured with Next.js rules
- **Prettier**: Code formatting (if configured)
- **Components**: Functional components with hooks
- **State**: Zustand for global state, useState for local

## 📞 Support

- **Documentation**: Available in `/docs` when running
- **API Docs**: http://localhost:8000/docs
- **Issues**: GitHub Issues
- **Development**: Check main project README

---

**TinyRAG Frontend v1.4.1** - Modern React Interface for AI Workflows! 🚀

🔗 **Quick Access**: [http://localhost:3000](http://localhost:3000) (after starting dev server)
