# TinyRAG Frontend - React Next.js Application

**Version**: 1.4.1  
**Framework**: Next.js 15.3.3 with TypeScript  
**Styling**: Tailwind CSS  
**State Management**: Zustand + React Query  

## 📋 Overview

TinyRAG Frontend is a modern, responsive web application that provides a comprehensive interface for managing RAG (Retrieval-Augmented Generation) workflows. Built with Next.js and TypeScript, it offers authentication, project management, document processing, and AI-powered content generation capabilities.

## 🏗️ Architecture & Tech Stack

### Core Technologies
- **Framework**: Next.js 15.3.3 with App Router
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS 3.x
- **Icons**: Heroicons
- **HTTP Client**: Axios with React Query
- **State Management**: Zustand + React Query
- **File Upload**: React Dropzone
- **Form Handling**: React Hook Form
- **Development**: Turbopack (Next.js bundler)

### Key Features
- 🔐 **JWT Authentication** with secure token management
- 📊 **Real-time Dashboard** with user analytics
- 📁 **Project Management** with collaboration support
- 📄 **Document Upload** with individual status tracking
- ⚡ **Element Management** for AI templates and tools
- 🤖 **Generation Tracking** with detailed metrics
- 📈 **Evaluation System** for quality assessment
- 🎨 **Responsive Design** with mobile-first approach

## 🛣️ Route Structure

### Authentication Routes
```
/ (root)                          # Landing page with login/register
├── Landing Page                  # Split-screen auth interface
├── Login Form                    # Email/password authentication
└── Register Form                 # User registration with validation
```

### Dashboard Routes
```
/dashboard                        # Main dashboard after login
├── Welcome Header                # Personalized user greeting
├── Quick Actions                 # Fast access to key features
├── Analytics Overview            # User statistics and metrics
├── Recent Activity               # Timeline of recent actions
└── Getting Started Guide        # Onboarding checklist
```

### Project Management Routes
```
/projects                         # Projects listing and management
├── Projects Grid/List View       # Responsive project cards
├── Search & Filters             # Filter by type, status, visibility
├── Project Statistics           # Documents, elements, generations count
└── Collaboration Info           # Team members and permissions

/projects/create                  # Multi-step project creation wizard
├── Step 1: Basic Details        # Name, description, tenant type
├── Step 2: Configuration        # Visibility, keywords, settings
└── Step 3: Confirmation         # Review and create

/projects/[id]                    # Individual project management
├── Overview Tab                 # Project summary and statistics
├── Documents Tab                # Project-specific documents
├── Elements Tab                 # AI templates and tools
├── Generations Tab              # Content generation history
└── Settings Tab                 # Project configuration
```

### Document Management Routes
```
/documents                        # Global document upload and management
├── Project Selection            # Choose target project
├── Enhanced Upload Zone         # Drag-and-drop with progress tracking
├── Individual Status Tracking   # Real-time upload and processing status
├── Batch Processing Actions     # Process all documents for RAG pipeline
├── Supported Formats Info       # PDF, DOCX, TXT, DOC support
├── Processing Pipeline Guide    # Step-by-step workflow explanation
└── Existing Documents List      # Project documents with metadata

/projects/[id]/documents/upload   # Project-specific document upload
└── Same features as global documents page
```

### Element Management Routes
```
/elements                         # Global elements management
├── Elements Grid View           # All user elements across projects
├── Filter by Type & Status      # PROMPT_TEMPLATE, MCP_CONFIG, AGENTIC_TOOL
└── Bulk Operations              # Execute all, archive, delete

/projects/[id]/elements           # Project-specific elements
├── Elements List                # Project elements with execution stats
├── Bulk Actions Toolbar         # Execute all elements for project
└── Element Status Monitoring    # Real-time execution progress

/projects/[id]/elements/create    # Create new element wizard
├── Element Type Selector        # Choose element type
├── Type-specific Forms          # Dynamic form based on element type
├── Template Preview             # Live preview with variable substitution
├── Variables Editor             # Dynamic variable definition
└── Validation & Testing         # Template syntax validation
```

### Generation Management Routes
```
/generations                      # Global generations listing
├── Generations Timeline         # Visual activity timeline
├── Filter & Search              # By element, status, date, model
├── Generation Cards             # Status, metrics, quick actions
└── Export Options               # Data export functionality

/projects/[id]/generations        # Project-specific generations
└── Same features as global generations

/generations/[id]                 # Individual generation details
├── Generation Header            # Status, element, execution time
├── Generated Content            # Formatted text with citations
├── Performance Metrics          # Token usage, cost, timing
├── Source Documents             # Links to source materials
├── Evaluation Actions           # Create quality assessments
└── Metadata Display             # Model used, parameters, etc.
```

### Evaluation Routes
```
/evaluations                      # Global evaluation management
├── Evaluation Queue             # Pending evaluations
├── Batch Evaluation Tools       # Evaluate multiple generations
└── Quality Analytics            # Evaluation statistics

/projects/[id]/evaluations        # Project-specific evaluations
├── Evaluation Interface         # Generation quality assessment
├── Multi-criteria Scoring       # Accuracy, relevance, clarity
├── Source Context Panel         # Original prompts and documents
├── Evaluation Guidelines        # Scoring rubric and instructions
├── Quality Checklist           # Hallucination and accuracy checks
└── Comparative Evaluation       # Side-by-side generation comparison
```

### API Testing Routes
```
/testing                          # Development and testing interface
├── API Test Suite               # Comprehensive API testing
├── Endpoint Testing             # Individual API endpoint tests
├── Authentication Tests         # Login/register functionality
├── Upload Testing               # Document upload validation
└── Integration Tests            # End-to-end workflow testing
```

## 🔧 Component Architecture

### Layout Components
```
src/components/layout/
├── DashboardLayout.tsx          # Main authenticated layout
├── MainLayout.tsx               # Public layout wrapper
├── Header.tsx                   # Navigation and user menu
├── Sidebar.tsx                  # Navigation sidebar
└── StatusBar.tsx                # System status indicator
```

### Feature Components
```
src/components/
├── auth/                        # Authentication components
│   ├── LandingPage.tsx         # Split-screen landing page
│   ├── LoginForm.tsx           # Login form with validation
│   └── RegisterForm.tsx        # Registration form
├── documents/                   # Document management
│   ├── EnhancedDocumentUpload.tsx  # Advanced upload with status
│   ├── DocumentList.tsx        # Document listing component
│   └── DocumentUpload.tsx      # Basic upload component
├── projects/                    # Project management
├── elements/                    # Element management
├── generations/                 # Generation tracking
├── evaluations/                 # Quality assessment
├── common/                      # Shared components
│   └── ErrorBoundary.tsx       # Error handling wrapper
└── ui/                          # Base UI components
    ├── Button.tsx              # Reusable button component
    ├── Card.tsx                # Card layout component
    ├── LoadingSpinner.tsx      # Loading indicators
    └── StatusBadge.tsx         # Status display component
```

## 🚀 Getting Started

### Prerequisites
- Node.js 20+ (managed via nvm)
- npm or yarn package manager
- Docker and Docker Compose (for full stack)

### Development Setup

1. **Install Node.js 20+**
   ```bash
   # Using nvm (recommended)
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   nvm install 20
   nvm use 20
   ```

2. **Install Dependencies**
   ```bash
   cd rag-memo-ui
   npm install
   ```

3. **Environment Configuration**
   ```bash
   # Copy environment template
   cp .env.example .env.local
   
   # Configure API endpoint
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" >> .env.local
   ```

4. **Start Development Server**
   ```bash
   npm run dev
   ```

5. **Access Application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000 (if running backend)

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start

# Or using Docker
docker build -t tinyrag-ui .
docker run -p 3000:3000 tinyrag-ui
```

## 🐳 Docker Configuration

### Development with Docker Compose
```bash
# Start all services (API, UI, databases)
docker-compose up -d

# Rebuild UI without cache
docker-compose build --no-cache tinyrag-ui
docker-compose up -d tinyrag-ui

# View logs
docker-compose logs -f tinyrag-ui
```

### Docker Configuration Files
- `Dockerfile` - Multi-stage production build
- `docker-compose.yml` - Full stack orchestration
- `.dockerignore` - Exclude unnecessary files

## 🔌 API Integration

### API Client Configuration
```typescript
// src/services/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Features:
// - Automatic JWT token management
// - Request/response interceptors
// - Error handling and retries
// - Type-safe API calls
```

### Authentication Flow
1. User submits login credentials
2. API returns JWT access token
3. Token stored in localStorage
4. Automatic token attachment to requests
5. Token refresh on expiration
6. Redirect to login on 401 errors

### Real-time Updates
- React Query for data fetching and caching
- Optimistic updates for better UX
- Background refetching for fresh data
- Error boundaries for graceful failures

## 🎨 Design System

### Color Palette
- **Primary**: Blue (#3B82F6) - Actions, links, highlights
- **Secondary**: Gray (#6B7280) - Text, borders, backgrounds
- **Success**: Green (#10B981) - Completed states, success messages
- **Warning**: Yellow (#F59E0B) - Pending states, warnings
- **Error**: Red (#EF4444) - Failed states, error messages

### Typography
- **Font Family**: Inter (Google Fonts)
- **Headings**: Font weights 600-800
- **Body Text**: Font weight 400-500
- **Responsive Scaling**: Base 16px with rem units

### Component Patterns
- **Cards**: Consistent padding, shadows, rounded corners
- **Forms**: Validation states, error messages, loading states
- **Buttons**: Primary, secondary, danger variants
- **Status Badges**: Color-coded status indicators
- **Loading States**: Skeleton screens and spinners

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 640px (sm)
- **Tablet**: 640px - 1024px (md/lg)
- **Desktop**: > 1024px (xl)

### Mobile-First Approach
- Base styles for mobile devices
- Progressive enhancement for larger screens
- Touch-friendly interface elements
- Optimized navigation for small screens

## 🧪 Testing Strategy

### Testing Tools
- **Unit Tests**: Jest + React Testing Library
- **Integration Tests**: Cypress or Playwright
- **API Tests**: Built-in testing interface at `/testing`
- **Type Checking**: TypeScript strict mode

### Test Coverage Areas
- Authentication flows
- Document upload functionality
- Project management operations
- API integration points
- Error handling scenarios

## 🚀 Performance Optimization

### Build Optimization
- **Turbopack**: Fast development bundling
- **Code Splitting**: Automatic route-based splitting
- **Tree Shaking**: Remove unused code
- **Image Optimization**: Next.js automatic optimization
- **Bundle Analysis**: Built-in bundle analyzer

### Runtime Performance
- **React Query**: Intelligent caching and background updates
- **Lazy Loading**: Components and routes loaded on demand
- **Memoization**: Prevent unnecessary re-renders
- **Virtual Scrolling**: For large data sets

## 🔧 Development Guidelines

### Code Standards
- **TypeScript**: Strict mode enabled
- **ESLint**: Code quality and consistency
- **Prettier**: Automatic code formatting
- **Husky**: Pre-commit hooks for quality checks

### Component Guidelines
- Functional components with hooks
- TypeScript interfaces for all props
- Consistent naming conventions
- Comprehensive JSDoc comments
- Error boundaries for fault tolerance

### State Management
- **Local State**: useState for component-specific state
- **Global State**: Zustand for app-wide state
- **Server State**: React Query for API data
- **Form State**: React Hook Form for complex forms

## 🐛 Troubleshooting

### Common Issues

1. **Port 3000 Already in Use**
   ```bash
   # Kill existing process
   lsof -ti:3000 | xargs kill -9
   
   # Or use different port
   npm run dev -- -p 3001
   ```

2. **API Connection Errors**
   ```bash
   # Check API status
   curl http://localhost:8000/health
   
   # Verify environment variables
   echo $NEXT_PUBLIC_API_URL
   ```

3. **Docker Build Issues**
   ```bash
   # Clear Docker cache
   docker system prune -a
   
   # Rebuild without cache
   docker-compose build --no-cache tinyrag-ui
   ```

4. **Node.js Version Issues**
   ```bash
   # Check current version
   node --version
   
   # Switch to correct version
   nvm use 20
   ```

### Development Tips
- Use React DevTools for component debugging
- Enable React Query DevTools for API debugging
- Check browser console for error messages
- Use network tab to monitor API requests

## 📚 Additional Resources

### Documentation
- [Next.js Documentation](https://nextjs.org/docs)
- [React Query Guide](https://tanstack.com/query/latest)
- [Tailwind CSS Reference](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)

### API Documentation
- Backend API: `/api/docs` (when running)
- API Testing Interface: `/testing`
- Health Check: `/health`

---

**TinyRAG Frontend v1.4.1** - Modern RAG Workflow Management Interface 🚀

Built with ❤️ using Next.js, TypeScript, and Tailwind CSS
