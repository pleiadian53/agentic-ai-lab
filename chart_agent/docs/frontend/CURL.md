# cURL Tutorial - Chart Agent API

## What is cURL?

**cURL** (Client URL) is a command-line tool for transferring data with URLs. It's pre-installed on most systems and perfect for:

- Testing APIs
- Automation scripts
- CI/CD pipelines
- Quick debugging
- Shell scripting

## Basic Syntax

```bash
curl [options] [URL]
```

**Common options:**
- `-X` - HTTP method (GET, POST, PUT, DELETE)
- `-H` - Add header
- `-d` - Send data (request body)
- `-o` - Save output to file
- `-v` - Verbose (show details)
- `-s` - Silent mode
- `-i` - Include response headers

## Chart Agent API Examples

### 1. Health Check

```bash
curl http://localhost:8003/health
```

**Response:**
```json
{
  "status": "healthy",
  "datasets_available": 3,
  "output_directory": "/path/to/output"
}
```

### 2. List Datasets

```bash
curl http://localhost:8003/datasets
```

**Response:**
```json
{
  "datasets": [
    {
      "path": "data/splice_sites_enhanced.tsv",
      "name": "splice_sites_enhanced",
      "size_mb": 25.4,
      "cached": false
    }
  ],
  "total": 1,
  "cached": 0
}
```

### 3. Generate Chart Code

```bash
curl -X POST http://localhost:8003/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/splice_sites_enhanced.tsv",
    "question": "Show the top 20 genes with the most splice sites",
    "context": "Focus on standard chromosomes only",
    "model": "gpt-4o-mini"
  }'
```

**Response:**
```json
{
  "code": "import matplotlib.pyplot as plt\nimport pandas as pd\n...",
  "explanation": "Generated bar chart using matplotlib",
  "libraries_used": ["matplotlib", "pandas"]
}
```

### 4. Execute Chart Code

```bash
# Save the code to a variable first
CODE=$(curl -s -X POST http://localhost:8003/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/splice_sites_enhanced.tsv",
    "question": "Show top 20 genes",
    "model": "gpt-4o-mini"
  }' | jq -r '.code')

# Execute it
curl -X POST http://localhost:8003/execute \
  -H "Content-Type: application/json" \
  -d "{
    \"code\": $(echo "$CODE" | jq -Rs .),
    \"dataset_path\": \"data/splice_sites_enhanced.tsv\",
    \"output_format\": \"pdf\"
  }"
```

**Response:**
```json
{
  "success": true,
  "image_path": "/charts/chart_1234.pdf",
  "logs": "Chart generated successfully"
}
```

### 5. Download Generated Chart

```bash
# Get the image path from execute response
IMAGE_PATH=$(curl -s -X POST http://localhost:8003/execute \
  -H "Content-Type: application/json" \
  -d '...' | jq -r '.image_path')

# Download the chart
curl http://localhost:8003${IMAGE_PATH} -o my_chart.pdf
```

### 6. Critique Code

```bash
curl -X POST http://localhost:8003/critique \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import matplotlib.pyplot as plt\n...",
    "domain_context": "Genomics research on splice sites",
    "model": "gpt-4o-mini"
  }'
```

## Complete Workflow Script

Create `generate_chart.sh`:

```bash
#!/bin/bash

# Configuration
API_URL="http://localhost:8003"
DATASET="data/splice_sites_enhanced.tsv"
QUESTION="Show the top 20 genes with the most splice sites"
CONTEXT="Focus on standard chromosomes only. Use publication-ready styling."
MODEL="gpt-4o-mini"
OUTPUT_FILE="chart.pdf"

echo "🎨 Chart Agent - Automated Workflow"
echo "===================================="

# Step 1: Generate code
echo ""
echo "📝 Step 1: Generating chart code..."
RESPONSE=$(curl -s -X POST ${API_URL}/analyze \
  -H "Content-Type: application/json" \
  -d "{
    \"dataset_path\": \"${DATASET}\",
    \"question\": \"${QUESTION}\",
    \"context\": \"${CONTEXT}\",
    \"model\": \"${MODEL}\"
  }")

# Check for errors
if echo "$RESPONSE" | jq -e '.code' > /dev/null 2>&1; then
  CODE=$(echo "$RESPONSE" | jq -r '.code')
  EXPLANATION=$(echo "$RESPONSE" | jq -r '.explanation')
  echo "✅ Code generated: $EXPLANATION"
else
  echo "❌ Generation failed:"
  echo "$RESPONSE" | jq .
  exit 1
fi

# Step 2: Execute code
echo ""
echo "🎨 Step 2: Executing code..."
EXEC_RESPONSE=$(curl -s -X POST ${API_URL}/execute \
  -H "Content-Type: application/json" \
  -d "{
    \"code\": $(echo "$CODE" | jq -Rs .),
    \"dataset_path\": \"${DATASET}\",
    \"output_format\": \"pdf\"
  }")

# Check execution success
if echo "$EXEC_RESPONSE" | jq -e '.success' | grep -q true; then
  IMAGE_PATH=$(echo "$EXEC_RESPONSE" | jq -r '.image_path')
  echo "✅ Chart generated: $IMAGE_PATH"
else
  echo "❌ Execution failed:"
  echo "$EXEC_RESPONSE" | jq .
  exit 1
fi

# Step 3: Download chart
echo ""
echo "📥 Step 3: Downloading chart..."
curl -s ${API_URL}${IMAGE_PATH} -o ${OUTPUT_FILE}

if [ -f "${OUTPUT_FILE}" ]; then
  SIZE=$(ls -lh ${OUTPUT_FILE} | awk '{print $5}')
  echo "✅ Chart saved: ${OUTPUT_FILE} (${SIZE})"
  
  # Open the chart (macOS)
  if command -v open &> /dev/null; then
    open ${OUTPUT_FILE}
    echo "✅ Chart opened in default viewer"
  fi
else
  echo "❌ Download failed"
  exit 1
fi

echo ""
echo "===================================="
echo "✅ Workflow complete!"
```

Make it executable and run:

```bash
chmod +x generate_chart.sh
./generate_chart.sh
```

## Advanced Usage

### Pretty Print JSON

```bash
# Install jq if not available
brew install jq  # macOS
apt-get install jq  # Linux

# Use with curl
curl http://localhost:8003/datasets | jq .
```

### Save Response to File

```bash
curl http://localhost:8003/analyze \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"dataset_path": "...", "question": "..."}' \
  -o response.json
```

### Show Request/Response Headers

```bash
curl -v http://localhost:8003/health
```

### Timeout and Retry

```bash
# Timeout after 30 seconds
curl --max-time 30 http://localhost:8003/analyze ...

# Retry 3 times on failure
curl --retry 3 http://localhost:8003/analyze ...
```

### Authentication (Future)

```bash
# With API key
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:8003/analyze ...

# With basic auth
curl -u username:password \
  http://localhost:8003/analyze ...
```

### Batch Processing

```bash
# Process multiple questions
QUESTIONS=(
  "Show top 20 genes"
  "Distribution by chromosome"
  "Splice site types breakdown"
)

for Q in "${QUESTIONS[@]}"; do
  echo "Processing: $Q"
  curl -X POST http://localhost:8003/analyze \
    -H "Content-Type: application/json" \
    -d "{
      \"dataset_path\": \"data/splice_sites_enhanced.tsv\",
      \"question\": \"$Q\",
      \"model\": \"gpt-4o-mini\"
    }" | jq -r '.code' > "code_$(echo $Q | tr ' ' '_').py"
done
```

## Error Handling

### Check HTTP Status Code

```bash
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8003/health)

if [ "$STATUS" -eq 200 ]; then
  echo "✅ API is healthy"
else
  echo "❌ API returned status: $STATUS"
fi
```

### Handle Validation Errors (422)

```bash
RESPONSE=$(curl -s -X POST http://localhost:8003/analyze \
  -H "Content-Type: application/json" \
  -d '{"dataset_path": "invalid", "question": "test"}')

if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
  echo "❌ Validation error:"
  echo "$RESPONSE" | jq -r '.details[] | "  - \(.field): \(.message)"'
else
  echo "✅ Request successful"
fi
```

## Integration Examples

### CI/CD Pipeline (GitHub Actions)

```yaml
name: Generate Charts

on: [push]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Start Chart Agent API
        run: |
          cd chart_agent/server
          python manage.py start &
          sleep 10
      
      - name: Generate Chart
        run: |
          curl -X POST http://localhost:8003/analyze \
            -H "Content-Type: application/json" \
            -d '{"dataset_path": "data/splice_sites_enhanced.tsv", "question": "Show top genes"}' \
            -o chart_code.json
      
      - name: Upload Artifact
        uses: actions/upload-artifact@v2
        with:
          name: chart-code
          path: chart_code.json
```

### Cron Job (Daily Charts)

```bash
# Add to crontab: crontab -e
0 9 * * * /path/to/generate_chart.sh >> /var/log/chart_agent.log 2>&1
```

### Slack Integration

```bash
#!/bin/bash

# Generate chart
./generate_chart.sh

# Upload to Slack
curl -F file=@chart.pdf \
  -F "initial_comment=Daily chart generated!" \
  -F channels=C1234567890 \
  -H "Authorization: Bearer xoxb-your-token" \
  https://slack.com/api/files.upload
```

## Debugging Tips

### 1. Verbose Output

```bash
curl -v http://localhost:8003/analyze ...
```

Shows:
- Request headers
- Response headers
- SSL handshake
- Timing information

### 2. Save Request/Response

```bash
# Save request
curl -X POST http://localhost:8003/analyze \
  --trace-ascii request.txt \
  -H "Content-Type: application/json" \
  -d '...'
```

### 3. Test Connectivity

```bash
# Check if API is reachable
curl -I http://localhost:8003/health

# Check specific endpoint
curl -X OPTIONS http://localhost:8003/analyze
```

### 4. Validate JSON

```bash
# Check if JSON is valid before sending
echo '{"dataset_path": "..."}' | jq .

# If valid, send it
curl -X POST http://localhost:8003/analyze \
  -H "Content-Type: application/json" \
  -d "$(echo '{"dataset_path": "..."}' | jq -c .)"
```

## Performance Testing

### Measure Response Time

```bash
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8003/analyze ...
```

Create `curl-format.txt`:
```
    time_namelookup:  %{time_namelookup}s\n
       time_connect:  %{time_connect}s\n
    time_appconnect:  %{time_appconnect}s\n
   time_pretransfer:  %{time_pretransfer}s\n
      time_redirect:  %{time_redirect}s\n
 time_starttransfer:  %{time_starttransfer}s\n
                    ----------\n
         time_total:  %{time_total}s\n
```

### Load Testing

```bash
# Simple load test - 10 concurrent requests
for i in {1..10}; do
  curl -X POST http://localhost:8003/analyze \
    -H "Content-Type: application/json" \
    -d '...' &
done
wait
```

## Comparison with Other Tools

| Feature | cURL | Postman | HTTPie | Python requests |
|---------|------|---------|--------|-----------------|
| CLI | ✅ | ❌ | ✅ | ❌ |
| Scripting | ✅ | ⚠️ | ✅ | ✅ |
| Pre-installed | ✅ | ❌ | ❌ | ❌ |
| Syntax | Complex | GUI | Simple | Simple |
| Automation | ✅ | ⚠️ | ✅ | ✅ |

## Resources

- **cURL Docs**: https://curl.se/docs/
- **jq Manual**: https://stedolan.github.io/jq/manual/
- **HTTP Status Codes**: https://httpstatuses.com/
- **Chart Agent API**: [../../server/QUICKSTART.md](../../server/QUICKSTART.md)
