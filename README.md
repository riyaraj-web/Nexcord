# Nexcord - Real-Time Chat Application

A modern real-time chat application with AI-powered content moderation.

## Features

- Real-time messaging with WebSocket
- User authentication (JWT)
- Public/Private channels
- Direct messaging
- File sharing
- AI content moderation (optional)
- Analytics dashboard
- Rate limiting

## Tech Stack

**Backend:** FastAPI, PostgreSQL, Redis, RabbitMQ  
**Frontend:** Next.js 14, TypeScript, TailwindCSS, shadcn/ui  
**DevOps:** Docker, Kubernetes, Terraform, GitHub Actions

## Quick Start

### Prerequisites
- Docker Desktop
- Git

### Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/nexcord.git
cd nexcord
```

2. Create environment files
```bash
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

3. Start with Docker
```bash
docker compose up -d
```

4. Access the application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://chatuser:chatpass@localhost:5432/chatapp
REDIS_URL=redis://localhost:6379
RABBITMQ_URL=amqp://guest:guest@localhost:5672
JWT_SECRET=your-secret-key-change-in-production
OPENAI_API_KEY=your-openai-key  # Optional
AWS_ACCESS_KEY_ID=your-aws-key  # Optional
AWS_SECRET_ACCESS_KEY=your-aws-secret  # Optional
AWS_S3_BUCKET=your-bucket-name  # Optional
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Project Structure

```
nexcord/
├── backend/          # FastAPI backend
├── frontend/         # Next.js frontend
├── infrastructure/   # K8s & Terraform
└── .github/         # CI/CD workflows
```

## Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Deployment

### Deploy with Docker

The easiest way to deploy Nexcord is using Docker:

```bash
# 1. Clone repository
git clone https://github.com/riyaraj-web/Nexcord.git
cd Nexcord

# 2. Setup environment
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# 3. Edit environment files with production values
nano backend/.env
nano frontend/.env.local

# 4. Start all services
docker compose up -d

# 5. Check status
docker compose ps

# 6. View logs
docker compose logs -f
```

**Services running:**
- Frontend: http://your-server:3000
- Backend: http://your-server:8000
- PostgreSQL: Port 5432
- Redis: Port 6379
- RabbitMQ: Port 5672, Management UI: Port 15672

### Deploy on VPS (DigitalOcean, AWS EC2, Linode)

1. **Setup server**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo apt-get install docker-compose-plugin
```

2. **Clone and start**
```bash
git clone https://github.com/riyaraj-web/Nexcord.git
cd Nexcord
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
# Edit .env files
docker compose up -d
```

3. **Setup domain (optional)**
- Point domain to server IP
- Setup Nginx reverse proxy
- Add SSL with Certbot

### Deploy on Cloud Platforms

**Render.com / Railway.app:**
1. Connect GitHub repository
2. Add environment variables
3. Deploy backend and frontend separately
4. Add PostgreSQL and Redis add-ons

**Vercel (Frontend) + Render (Backend):**
- Frontend: Deploy to Vercel
- Backend: Deploy to Render with PostgreSQL
- Update CORS and API URLs

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.
