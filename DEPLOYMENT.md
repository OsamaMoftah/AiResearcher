# Deployment Guide

This guide covers various deployment options for AiResearcher.

## Prerequisites

- Python 3.10 or higher
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

## Local Deployment

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/OsamaMoftah/AiResearcher.git
cd AiResearcher
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run app.py
# Or use the convenient script:
./run.sh
```

5. Open your browser at `http://localhost:8501`

## Docker Deployment

### Build and Run with Docker

1. Build the Docker image:
```bash
docker build -t airesearcher:latest .
```

2. Run the container:
```bash
docker run -d \
  --name airesearcher \
  -p 8501:8501 \
  -e GOOGLE_API_KEY=your_api_key_here \
  airesearcher:latest
```

3. Access the application at `http://localhost:8501`

### Using Docker Compose

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  airesearcher:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with:
```bash
docker-compose up -d
```

## Cloud Deployment

### Streamlit Community Cloud

1. Push your code to GitHub
2. Go to [Streamlit Community Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Add `GOOGLE_API_KEY` to secrets
5. Deploy!

### Google Cloud Run

1. Install Google Cloud SDK

2. Build and push to Container Registry:
```bash
gcloud builds submit --tag gcr.io/[PROJECT-ID]/airesearcher
```

3. Deploy to Cloud Run:
```bash
gcloud run deploy airesearcher \
  --image gcr.io/[PROJECT-ID]/airesearcher \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your_api_key
```

### AWS Elastic Beanstalk

1. Install EB CLI:
```bash
pip install awsebcli
```

2. Initialize EB:
```bash
eb init -p docker airesearcher
```

3. Create environment and deploy:
```bash
eb create airesearcher-env
eb setenv GOOGLE_API_KEY=your_api_key
```

### Azure Container Instances

1. Build and push to Azure Container Registry:
```bash
az acr build --registry myregistry --image airesearcher:latest .
```

2. Deploy to ACI:
```bash
az container create \
  --resource-group myResourceGroup \
  --name airesearcher \
  --image myregistry.azurecr.io/airesearcher:latest \
  --dns-name-label airesearcher \
  --ports 8501 \
  --environment-variables GOOGLE_API_KEY=your_api_key
```

## Production Considerations

### Security

1. **API Key Management**: Never commit API keys to git. Use environment variables or secrets management.

2. **HTTPS**: Enable HTTPS in production. Use a reverse proxy like Nginx or cloud provider's SSL.

3. **Rate Limiting**: Implement rate limiting to prevent API abuse:
   - Use API Gateway for cloud deployments
   - Implement middleware for custom deployments

4. **Authentication**: Add user authentication if needed:
   ```python
   # In app.py
   import streamlit_authenticator as stauth
   ```

### Performance

1. **Caching**: Streamlit provides built-in caching:
   ```python
   @st.cache_data
   def expensive_operation():
       ...
   ```

2. **Concurrent Users**: For high traffic:
   - Use multiple container instances
   - Configure load balancing
   - Consider upgrading Gemini API quota

3. **Memory Management**: Monitor memory usage:
   - Set container memory limits
   - Use smaller paper batch sizes if needed

### Monitoring

1. **Health Checks**: The Dockerfile includes health checks

2. **Logging**: Configure logging:
   ```bash
   docker logs -f airesearcher
   ```

3. **Metrics**: Use cloud provider monitoring:
   - Google Cloud Monitoring
   - AWS CloudWatch
   - Azure Monitor

### Backup and Recovery

1. **Configuration Backup**: Keep `.env.example` updated

2. **Version Control**: Tag releases:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Change port in docker run:
   docker run -p 8502:8501 ...
   ```

2. **API Key not found**:
   - Verify `.env` file exists
   - Check environment variable is set
   - Restart the application

3. **Memory errors**:
   - Reduce batch size in analysis
   - Increase container memory limit

4. **Slow response times**:
   - Check API quota limits
   - Enable caching
   - Reduce number of papers analyzed

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Google Gemini API key |
| `STREAMLIT_SERVER_PORT` | No | Port (default: 8501) |
| `STREAMLIT_SERVER_ADDRESS` | No | Address (default: localhost) |

## Scaling

For production scale:

1. **Horizontal Scaling**: Deploy multiple instances behind a load balancer

2. **Database**: For persistent storage, integrate a database:
   - PostgreSQL for structured data
   - MongoDB for document storage

3. **Queue System**: For async processing:
   - Redis for job queue
   - Celery for background tasks

## Support

For issues and questions:
- GitHub Issues: https://github.com/OsamaMoftah/AiResearcher/issues
- Documentation: https://github.com/OsamaMoftah/AiResearcher/blob/main/README.md
