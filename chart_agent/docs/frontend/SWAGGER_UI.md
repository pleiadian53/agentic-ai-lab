# Swagger UI Tutorial - Chart Agent API

## What is Swagger UI?

**Swagger UI** is an interactive API documentation tool that automatically generates a web interface for testing REST APIs. It's built into FastAPI and provides:

- **Interactive testing** - Try API endpoints directly in your browser
- **Auto-generated docs** - Documentation from your code
- **Request/response examples** - See what data to send and expect
- **Schema validation** - Ensures requests match the API specification

## Accessing Swagger UI

Once the Chart Agent API is running:

```bash
cd chart_agent/server
mamba run -n agentic-ai python manage.py start
```

Open your browser to: **http://localhost:8003/docs**

## Understanding the Interface

### Main Components

1. **Endpoint List** - All available API endpoints grouped by category
2. **Try it out** - Button to enable interactive testing
3. **Request Body** - JSON input for POST requests
4. **Execute** - Send the request
5. **Responses** - See actual server responses

### Color Coding

- **Green (GET)** - Retrieve data (read-only)
- **Blue (POST)** - Create or process data
- **Orange (PUT)** - Update existing data
- **Red (DELETE)** - Remove data

## Step-by-Step: Testing the `/analyze` Endpoint

### Step 1: Expand the Endpoint

Click on **POST /analyze** to expand it. You'll see:
- Description: "Generate chart code from natural language question"
- Parameters: Request body schema
- Responses: 200 (success) and 422 (validation error) examples

### Step 2: Click "Try it out"

A blue button in the top-right of the endpoint section. This enables editing.

### Step 3: Edit the Request Body

You'll see a JSON editor with example values:

```json
{
  "dataset_path": "data/splice_sites_enhanced.tsv",
  "question": "Show the top 20 genes with the most splice sites",
  "context": "Focus on standard chromosomes only. Use publication-ready styling.",
  "model": "gpt-4o-mini"
}
```

**Important**: Replace placeholder values like `"string"` with actual data!

### Step 4: Click "Execute"

The request is sent to the server. Scroll down to see:

**Request Details:**
- **Curl command** - Copy to use in terminal
- **Request URL** - The actual endpoint called
- **Request body** - What was sent

**Server Response:**
- **Status code** - 200 = success, 422 = validation error, 500 = server error
- **Response body** - The actual JSON response
- **Response headers** - Metadata about the response

### Step 5: Interpret the Response

**Success (200):**
```json
{
  "code": "import matplotlib.pyplot as plt\n...",
  "explanation": "Generated bar chart using matplotlib",
  "libraries_used": ["matplotlib", "pandas"]
}
```

**Validation Error (422):**
```json
{
  "error": "Validation Error",
  "message": "The request contains invalid data...",
  "details": [
    {
      "field": "body -> model",
      "message": "Invalid model name. Allowed values: ...",
      "provided": "gpt-5-codex-mini"
    }
  ]
}
```

## Common Workflows

### Workflow 1: Generate and Execute Chart

**1. Generate Code** (`POST /analyze`)
```json
{
  "dataset_path": "data/splice_sites_enhanced.tsv",
  "question": "Show distribution of splice sites by chromosome",
  "model": "gpt-4o-mini"
}
```

**2. Copy the `code` from response**

**3. Execute Code** (`POST /execute`)
```json
{
  "code": "<paste code here>",
  "dataset_path": "data/splice_sites_enhanced.tsv",
  "output_format": "pdf"
}
```

**4. Download the chart**
- Get `image_path` from response (e.g., `/charts/chart_1234.pdf`)
- Open: `http://localhost:8003/charts/chart_1234.pdf`

### Workflow 2: Critique and Refine

**1. Generate initial code** (`POST /analyze`)

**2. Critique the code** (`POST /critique`)
```json
{
  "code": "<generated code>",
  "domain_context": "Genomics research focusing on splice site patterns",
  "model": "gpt-4o-mini"
}
```

**3. Review critique** - Check `quality`, `issues`, `suggestions`

**4. Regenerate if needed** - Use suggestions in a new `/analyze` request

## Tips and Tricks

### 1. Use the Schema Tab

Click "Schema" next to "Example Value" to see:
- Required vs optional fields
- Data types
- Field descriptions
- Validation rules

### 2. Copy as cURL

After executing, copy the cURL command to:
- Use in scripts
- Share with teammates
- Debug in terminal

### 3. Check Available Datasets

Use `GET /datasets` to see what data is available:
```bash
# No request body needed for GET
```

Response shows all datasets in `data/` directory.

### 4. Health Check

Use `GET /health` to verify the service is running:
- Shows service status
- Lists available datasets
- Displays output directory

### 5. Model Selection

Valid model values (from `ModelType` enum):
- `"gpt-4o-mini"` - Default, fast and cost-effective
- `"gpt-4o"` - More capable
- `"gpt-5"` - Latest model
- `"gpt-5-mini"` - Fast GPT-5
- `"gpt-5.1-codex-mini"` - Optimized for code (note the `.1`)

## Troubleshooting

### Issue: "Try it out" button is grayed out

**Solution**: The endpoint might be disabled or you need to scroll up to find it.

### Issue: 422 Validation Error

**Causes**:
1. Invalid model name (check exact spelling)
2. Missing required fields
3. Wrong data type (e.g., string instead of number)
4. Dataset path doesn't exist

**Solution**: Check the error `details` field for specific issues.

### Issue: Response shows "string" placeholders

**This is normal!** These are just schema examples, not actual errors. Only worry if you see this AFTER clicking "Execute".

### Issue: 500 Internal Server Error

**Causes**:
1. Dataset not found
2. Code execution failed
3. LLM API error

**Solution**: Check server logs:
```bash
# If running with manage.py
tail -f chart_agent_api.log

# If running directly
# Check terminal output
```

### Issue: CORS errors in browser console

**Solution**: The API already has CORS enabled for `*`. If you still see errors:
1. Check if service is running
2. Verify URL is correct (http://localhost:8003)
3. Try in incognito mode

## Advanced Features

### Authentication (Future)

Currently, the API is open. For production:
1. Add API key authentication
2. Use OAuth2/JWT tokens
3. Configure in `config.py`

### Rate Limiting (Future)

To prevent abuse:
1. Add rate limiting middleware
2. Configure per-endpoint limits
3. Return 429 status when exceeded

### Custom Examples

You can add custom examples to schemas in `schemas.py`:

```python
class AnalysisRequest(BaseModel):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "dataset_path": "data/my_data.csv",
                    "question": "My custom question",
                    "model": "gpt-4o-mini"
                }
            ]
        }
    }
```

## Comparison with Other Tools

| Feature | Swagger UI | Postman | cURL | Python Client |
|---------|-----------|---------|------|---------------|
| Interactive | ✅ | ✅ | ❌ | ❌ |
| Auto-docs | ✅ | ❌ | ❌ | ❌ |
| No install | ✅ | ❌ | ✅ | ❌ |
| Scripting | ❌ | ✅ | ✅ | ✅ |
| Collections | ❌ | ✅ | ❌ | ✅ |

**When to use Swagger UI**:
- Quick testing during development
- Sharing API docs with team
- Exploring available endpoints
- Validating request/response formats

**When to use alternatives**:
- **Postman**: Complex workflows, team collaboration
- **cURL**: Automation, scripts, CI/CD
- **Python client**: Application integration, batch processing

## Next Steps

1. **Try the full workflow** - Generate → Execute → View chart
2. **Explore other endpoints** - `/critique`, `/insight`, `/datasets`
3. **Learn React integration** - See [REACT.md](REACT.md)
4. **Build a Streamlit app** - See [STREAMLIT.md](STREAMLIT.md)
5. **Automate with cURL** - See [CURL.md](CURL.md)

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **OpenAPI Spec**: https://swagger.io/specification/
- **Swagger UI**: https://swagger.io/tools/swagger-ui/
- **Chart Agent API Docs**: [../server/QUICKSTART.md](../../server/QUICKSTART.md)
