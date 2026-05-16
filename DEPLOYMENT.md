# Deployment Guide - SHL Assessment Recommender

This guide explains how to deploy the SHL Assessment Recommender to Render.com (recommended free tier option).

## Prerequisites

- GitHub account
- Render.com account (free tier available)
- Repository URL (after pushing to GitHub)

## Step 1: Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add -A

# Commit
git commit -m "SHL Assessment Recommender - Ready for deployment"

# Create new repository on GitHub and add remote
git remote add origin https://github.com/YOUR_USERNAME/shl-recommender
git branch -M main
git push -u origin main
```

## Step 2: Deploy to Render

### Option A: Direct Render Deployment (Recommended)

1. **Visit Render Dashboard:**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"

2. **Connect GitHub Repository:**
   - Select "GitHub"
   - Authorize Render to access your GitHub account
   - Select the `shl-recommender` repository

3. **Configure Service:**
   - **Name:** `shl-assessment-recommender` (or your preferred name)
   - **Environment:** Python 3
   - **Region:** Select closest to you (us-east-1 recommended)
   - **Branch:** main

4. **Build & Deploy Settings:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port 8000`

5. **Environment Variables (Optional):**
   - Leave blank for defaults
   - Or set `HF_TOKEN` if you have HuggingFace account (speeds up model downloads)

6. **Advanced Settings:**
   - **Auto-Deploy:** Toggle ON (auto-redeploy on GitHub push)
   - **Health Check Path:** `/health`
   - **Health Check Interval:** 30 seconds

7. **Click "Create Web Service"**

### Option B: Docker Deployment

If you prefer using Docker:

1. **Build Docker image locally:**
   ```bash
   docker build -t shl-recommender:latest .
   ```

2. **Test locally:**
   ```bash
   docker run -p 8000:8000 shl-recommender:latest
   curl http://localhost:8000/health
   ```

3. **Push to Docker Hub:**
   ```bash
   docker tag shl-recommender:latest YOUR_DOCKER_USERNAME/shl-recommender:latest
   docker push YOUR_DOCKER_USERNAME/shl-recommender:latest
   ```

4. **Deploy on Render:**
   - Select "Docker" when creating new Web Service
   - Point to your Docker Hub image

## Step 3: Verify Deployment

Once deployment completes (typically 2-5 minutes):

### Check Health Endpoint
```bash
curl https://YOUR_SERVICE_NAME.onrender.com/health
# Expected: {"status":"ok"}
```

### Test Chat Endpoint
```bash
curl -X POST https://YOUR_SERVICE_NAME.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I am hiring a Java developer mid-level"}
    ]
  }'
```

### Expected Response
```json
{
  "reply": "For a Mid-level Developer focused on Technical, I recommend:I found 10 relevant assessment(s) for you.",
  "recommendations": [
    {
      "name": "Java 8 (New)",
      "url": "https://www.shl.com/solutions/products/java/",
      "test_type": "K"
    },
    ...
  ],
  "end_of_conversation": false
}
```

## Step 4: Monitor Deployment

### View Logs
- Render Dashboard → Select your service
- Click "Logs" tab to see build and runtime logs

### Common Issues

**Issue: 502 Bad Gateway**
- Check logs for errors
- Ensure `uvicorn` command is correct
- Verify Python version compatibility

**Issue: Slow Cold Start**
- Normal: Rendering server loads embedding model (~45 seconds on first request)
- Subsequent requests: <500ms
- Consider upgrading to paid tier if many cold starts are problematic

**Issue: Model Download Fails**
- Set `HF_TOKEN` environment variable for faster downloads
- Or pre-build image with model included

## Deployment Verification Checklist

- [ ] Repository pushed to GitHub
- [ ] GitHub repository connected to Render
- [ ] Build command set to: `pip install -r requirements.txt`
- [ ] Start command set to: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [ ] Deployment completed successfully
- [ ] `/health` endpoint returns `{"status":"ok"}`
- [ ] `/chat` endpoint accepts POST requests and returns valid JSON
- [ ] URLs in recommendations point to `https://www.shl.com/`
- [ ] No URLs are hallucinated (all from catalog)

## Performance Expectations

| Metric | Value |
|--------|-------|
| Cold Start | ~45-60 seconds (model load) |
| Warm Request | 300-800 ms |
| Memory Usage | ~300 MB |
| Max Catalog Size | 1000+ assessments |
| Max Turns | 8 per conversation |
| Response Timeout | 30 seconds |

## Production Considerations

### Rate Limiting
Consider adding rate limiting if deploying to production:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

### Monitoring
Set up uptime monitoring:
- Render built-in monitoring
- Or use external service like Uptime Robot
- Monitor `/health` endpoint every 5 minutes

### Logging
Current setup logs to stdout (visible in Render logs).
For production, consider:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Datadog
- New Relic

### Scaling
- Free tier: Limited to 1 instance, shared resources
- Paid tier: Can scale to multiple instances with load balancing

## Rolling Back

If a deployment has issues:

1. **Via GitHub:**
   - Go to Render dashboard
   - Select your service
   - Click "Manual Deploy"
   - Choose previous commit/branch

2. **Via Docker:**
   - Push previous image version to Docker Hub
   - Update Render service to use previous tag

## Next Steps

After successful deployment:

1. **Test in Production:** Try various conversation scenarios
2. **Monitor Performance:** Watch logs for errors or slow requests
3. **Gather Feedback:** If integrated with hiring system, collect user feedback
4. **Iterate:** Tune retrieval weights, update prompts based on real usage

## Support

For issues during deployment:
- Check Render documentation: https://render.com/docs
- Review logs in Render dashboard
- Verify all environment variables are set
- Ensure catalog.json is in correct location

## Submission

Once deployed, submit the following:
- **Public API Endpoint URL:** `https://YOUR_SERVICE_NAME.onrender.com`
- **Approach Document:** [APPROACH.md](APPROACH.md)
- Submit via the provided form

---

**Estimated Deployment Time:** 10-15 minutes (including GitHub setup)  
**Estimated Monthly Cost:** $0 (free tier) or ~$7/month (basic tier)
