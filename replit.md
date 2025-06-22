# Overview

This is a bilingual Bible app (Spanish/Tzotzil) with an AI assistant called "Nevin" powered by OpenAI GPT-4. The application consists of a Flask backend with a React Native frontend (using Expo), featuring biblical text access, AI-powered biblical interpretation, and user management with subscription tiers.

# System Architecture

## Backend Architecture
- **Framework**: Flask with Python 3.11
- **Database**: PostgreSQL (via Neon.tech) with SQLAlchemy ORM
- **AI Integration**: OpenAI GPT-4 with FAISS for vector search and knowledge retrieval
- **Authentication**: JWT-based authentication with role-based access control
- **Caching**: Redis for distributed caching with local TTL cache fallback
- **File Storage**: Replit Object Storage for documents and assets

## Frontend Architecture
- **Framework**: React Native with Expo SDK 49.0
- **Navigation**: React Navigation v6
- **UI Library**: React Native Paper for Material Design components
- **State Management**: React Query for server state and async operations
- **Local Storage**: Expo SQLite for offline Bible data
- **Platform Support**: iOS, Android, and Web via Expo

## Database Schema
- **Users**: User authentication and subscription management
- **BibleVerse**: Bilingual biblical text storage (Spanish/Tzotzil)
- **Promise**: Biblical promises with associated images
- **Conversations**: Chat history for Nevin AI interactions

# Key Components

## Nevin AI Assistant
- **Knowledge Base**: FAISS-powered vector search through theological content
- **Response Engine**: Context-aware biblical interpretation with doctrinal validation
- **Content Sources**: Biblical text, Ellen G. White writings, and theological materials
- **Rate Limiting**: Intelligent request throttling to manage OpenAI API usage

## Bible Data Management
- **Bilingual Support**: Spanish and Tzotzil text side-by-side
- **Offline Capability**: Local SQLite database for offline reading
- **Search Functionality**: Advanced text search across both languages
- **Content Validation**: Input sanitization and biblical reference validation

## User Management
- **Subscription Tiers**: Free, Trial, and Premium access levels
- **Access Control**: Role-based permissions for Nevin AI features
- **Profile Management**: User preferences and reading history

## Caching Strategy
- **Multi-level Cache**: Redis for distributed caching with local TTL fallback
- **Cache Keys**: Structured naming for biblical content, AI responses, and user data
- **Cache Invalidation**: Time-based expiration with manual invalidation support

# Data Flow

## Bible Reading Flow
1. User requests biblical content via REST API
2. System checks local cache first (TTL cache → Redis)
3. If cache miss, queries PostgreSQL database
4. Results are cached and returned to frontend
5. React Native displays bilingual text with Paper UI components

## Nevin AI Interaction Flow
1. User submits question through chat interface
2. Backend validates user permissions and rate limits
3. Question is processed through interpretation engine
4. FAISS performs vector similarity search on knowledge base
5. OpenAI GPT-4 generates contextual response with retrieved knowledge
6. Response is validated against doctrinal principles
7. Final answer is cached and returned to user

## Offline Synchronization
1. User initiates database download
2. Backend exports SQLite database with biblical content
3. Frontend downloads and stores locally using Expo FileSystem
4. App switches to local database when offline
5. Online/offline status determines data source

# External Dependencies

## AI and Machine Learning
- **OpenAI API**: GPT-4 for natural language processing and biblical interpretation
- **FAISS**: Local vector search for theological knowledge retrieval
- **NumPy**: Numerical operations for embeddings and vector math

## Database and Storage
- **PostgreSQL**: Primary database via Neon.tech
- **Redis**: Distributed caching layer
- **SQLite**: Local storage for offline functionality

## Authentication and Security
- **JWT**: Token-based authentication
- **Werkzeug**: Password hashing and security utilities
- **Flask-CORS**: Cross-origin resource sharing for web platform

## Mobile Development
- **Expo SDK**: Cross-platform mobile development
- **React Native**: Mobile UI framework
- **Metro**: JavaScript bundler for React Native

# Deployment Strategy

## Backend Deployment
- **Platform**: Replit with Cloud Run deployment target
- **Environment**: Python 3.11 with required dependencies
- **Database**: Managed PostgreSQL via Neon.tech
- **Caching**: Redis instance for production caching

## Frontend Deployment
- **Development**: Expo development server on port 8083
- **Web**: Static web build via Expo webpack
- **Mobile**: Native builds through Expo Application Services (EAS)

## Configuration Management
- **Environment Variables**: Sensitive configuration via Replit secrets
- **Feature Flags**: Subscription-based feature access control
- **Monitoring**: Application logging with structured log format

## Performance Optimization
- **Database**: Connection pooling with pre-ping health checks
- **API**: Rate limiting and request batching for OpenAI calls
- **Caching**: Multi-tier caching strategy with intelligent invalidation
- **Mobile**: Lazy loading and optimized asset bundling

# Changelog
- June 22, 2025. Initial setup
- June 22, 2025. Disabled authentication system for free access to all users, removed login requirements for Nevin AI, fixed duplicate welcome message issue
- June 22, 2025. Fixed Google Play compliance issues: unified package ID to com.chyrris.tzotzilbible, cleaned problematic images, updated app configuration for Play Store approval
- June 22, 2025. Prepared APK build configuration: fixed assets, created build instructions, prepared Play Store submission materials with proper app name "Tzotzil Bible"
- June 22, 2025. Fixed deployment configuration: added root health endpoint, configured Flask app for port 5000, added missing API endpoints for Nevin chat, improved health check endpoints

# User Preferences

Preferred communication style: Simple, everyday language.