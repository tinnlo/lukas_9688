# Vertex AI API Usage Guide

## Overview

This guide explains how to use Google Vertex AI API for image and text generation with Gemini models.

## Prerequisites

1. **Google Cloud Account**: Active GCP account with Vertex AI API enabled
2. **gcloud CLI**: Installed and configured
3. **Project Access**: Access to the Vertex AI project

## Authentication

### Setup

The Vertex AI API requires OAuth 2.0 authentication, not API keys.

```bash
# Set the correct Google account
gcloud config set account tinnluo@gmail.com

# Authenticate if needed
gcloud auth login

# Verify authentication
gcloud auth list
```

### Get Access Token

```bash
# Get a fresh access token (valid for ~1 hour)
ACCESS_TOKEN=$(gcloud auth print-access-token)
```

## Project Configuration

From `.env` file:

```
VERTEX_PROJECT_ID=vertex-ai-trial-482611
VERTEX_CLOUD_REGION=us-central1
```

### Available Models

**Image Generation Models:**
- `gemini-2.5-flash-image` - Fast, standard quality
- `gemini-3-pro-image-preview` - High quality (Nano Banana Pro)

**Video Generation Models:**
- `veo-3.1-generate-001` - High quality (Pro)
- `veo-3.1-fast-generate-001` - Fast (Flash)

## API Endpoint Structure

```
https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/publishers/google/models/{MODEL_ID}:generateContent
```

Example:
```
https://us-central1-aiplatform.googleapis.com/v1/projects/vertex-ai-trial-482611/locations/us-central1/publishers/google/models/gemini-2.5-flash-image:generateContent
```

## Image Generation Example

### Using cURL

```bash
# Get access token
ACCESS_TOKEN=$(gcloud auth print-access-token)

# Make API request
curl -X POST \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/vertex-ai-trial-482611/locations/us-central1/publishers/google/models/gemini-2.5-flash-image:generateContent" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [{
        "text": "Generate an image of a futuristic city"
      }]
    }],
    "generation_config": {
      "temperature": 0.9,
      "maxOutputTokens": 2048
    }
  }' > response.json
```

### Response Format

The API returns JSON with base64-encoded image data:

```json
{
  "candidates": [
    {
      "content": {
        "role": "model",
        "parts": [
          {
            "text": "Here's your generated image!"
          },
          {
            "inlineData": {
              "mimeType": "image/png",
              "data": "iVBORw0KGgo... (base64 encoded image)"
            }
          }
        ]
      }
    }
  ]
}
```

## Extracting and Saving Images

### Using Python

```python
import json
import base64

# Read the API response
with open('response.json', 'r') as f:
    data = json.load(f)

# Extract base64 image data
img_data = data['candidates'][0]['content']['parts'][1]['inlineData']['data']

# Decode and save
with open('output.png', 'wb') as f:
    f.write(base64.b64decode(img_data))

print("Image saved to output.png")
```

### Using Bash Script

```bash
#!/bin/bash

# Generate image
ACCESS_TOKEN=$(gcloud auth print-access-token)
curl -s -X POST \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/vertex-ai-trial-482611/locations/us-central1/publishers/google/models/gemini-2.5-flash-image:generateContent" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [{
        "text": "'"$1"'"
      }]
    }],
    "generation_config": {
      "temperature": 0.9
    }
  }' > /tmp/response.json

# Extract and decode
python3 << 'EOF'
import json, base64
with open('/tmp/response.json', 'r') as f:
    data = json.load(f)
img_data = data['candidates'][0]['content']['parts'][1]['inlineData']['data']
with open('output.png', 'wb') as f:
    f.write(base64.b64decode(img_data))
print("Image saved to output.png")
EOF
```

Usage:
```bash
chmod +x generate_image.sh
./generate_image.sh "Generate a futuristic robot"
```

## Text Generation Example

```bash
ACCESS_TOKEN=$(gcloud auth print-access-token)

curl -X POST \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/vertex-ai-trial-482611/locations/us-central1/publishers/google/models/gemini-2.5-flash:generateContent" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [{
        "text": "Explain quantum computing in simple terms"
      }]
    }]
  }'
```

## Generation Parameters

Common parameters in `generation_config`:

- `temperature`: 0.0-1.0 (creativity level, higher = more creative)
- `maxOutputTokens`: Maximum response length
- `topK`: Top-K sampling
- `topP`: Top-P (nucleus) sampling

Example:
```json
{
  "generation_config": {
    "temperature": 0.9,
    "maxOutputTokens": 2048,
    "topK": 40,
    "topP": 0.95
  }
}
```

## Error Handling

### Common Errors

**401 Unauthorized:**
```json
{
  "error": {
    "code": 401,
    "message": "Request had invalid authentication credentials..."
  }
}
```
Solution: Refresh access token with `gcloud auth print-access-token`

**403 Permission Denied:**
```json
{
  "error": {
    "code": 403,
    "message": "Permission 'aiplatform.endpoints.predict' denied..."
  }
}
```
Solution: Ensure you're using the correct Google account with project access

**404 Not Found:**
- Check project ID is correct
- Verify model ID exists and is available in your region

## Rate Limits and Quotas

- Access tokens expire after ~1 hour
- API quotas depend on your GCP project tier
- Check quotas in GCP Console: IAM & Admin > Quotas

## Best Practices

1. **Token Management**: Cache access tokens and refresh before expiry
2. **Error Handling**: Always check response status codes
3. **Response Size**: Image data can be large; save directly to files
4. **Cost Monitoring**: Track API usage in GCP Console
5. **Security**: Never commit access tokens to version control

## Important Notes

- **No Direct URLs**: Vertex AI returns images as base64 data, not URLs
- **Account Required**: Must use `tinnluo@gmail.com` for this project
- **Region Specific**: Ensure model availability in your region
- **Token Expiry**: Refresh tokens hourly for long-running processes

## Testing the Setup

Quick test:
```bash
# Verify authentication
gcloud auth list

# Test API call
ACCESS_TOKEN=$(gcloud auth print-access-token)
curl -X POST \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/vertex-ai-trial-482611/locations/us-central1/publishers/google/models/gemini-2.5-flash:generateContent" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"role":"user","parts":[{"text":"Say hello"}]}]}'
```

## Resources

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Gemini API Reference](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini)
- [Authentication Guide](https://cloud.google.com/docs/authentication)

---

**Last Updated**: 2025-12-29
**Project**: vertex-ai-trial-482611
**Authorized Account**: tinnluo@gmail.com
