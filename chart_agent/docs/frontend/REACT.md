# React Integration Tutorial - Chart Agent API

## What is React?

**React** is a JavaScript library for building user interfaces, particularly single-page applications. It's component-based and uses a virtual DOM for efficient updates.

**Key Concepts:**
- **Components** - Reusable UI pieces
- **State** - Data that changes over time
- **Props** - Data passed between components
- **Hooks** - Functions to use state and lifecycle features
- **JSX** - JavaScript syntax extension that looks like HTML

## Why React for Chart Agent?

- **Interactive UI** - Real-time chart generation and preview
- **Component reusability** - Build once, use everywhere
- **Rich ecosystem** - Many charting and UI libraries
- **Modern development** - Fast, maintainable, scalable

## Prerequisites

```bash
# Install Node.js (includes npm)
# Download from: https://nodejs.org/

# Verify installation
node --version  # Should be v18 or higher
npm --version   # Should be v9 or higher
```

## Quick Start: Create React App

### Step 1: Create New React App

```bash
npx create-react-app chart-agent-ui
cd chart-agent-ui
```

### Step 2: Install Dependencies

```bash
# HTTP client for API calls
npm install axios

# UI components (optional but recommended)
npm install @mui/material @emotion/react @emotion/styled

# Code syntax highlighting
npm install react-syntax-highlighter
npm install @types/react-syntax-highlighter
```

### Step 3: Start Development Server

```bash
npm start
# Opens http://localhost:3000
```

## Building the Chart Agent UI

### Project Structure

```
chart-agent-ui/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── ChartGenerator.jsx    # Main component
│   │   ├── DatasetSelector.jsx   # Dataset picker
│   │   ├── CodePreview.jsx       # Code display
│   │   └── ChartViewer.jsx       # Chart display
│   ├── services/
│   │   └── chartAgentAPI.js      # API client
│   ├── App.js                     # Root component
│   ├── App.css                    # Styles
│   └── index.js                   # Entry point
└── package.json
```

### Component 1: API Service

Create `src/services/chartAgentAPI.js`:

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8003';

class ChartAgentAPI {
  constructor(baseURL = API_BASE_URL) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Get available datasets
  async getDatasets() {
    const response = await this.client.get('/datasets');
    return response.data;
  }

  // Generate chart code
  async analyzeData(datasetPath, question, context = null, model = 'gpt-4o-mini') {
    const response = await this.client.post('/analyze', {
      dataset_path: datasetPath,
      question,
      context,
      model,
    });
    return response.data;
  }

  // Execute chart code
  async executeCode(code, datasetPath, outputFormat = 'pdf') {
    const response = await this.client.post('/execute', {
      code,
      dataset_path: datasetPath,
      output_format: outputFormat,
    });
    return response.data;
  }

  // Critique code
  async critiqueCode(code, domainContext, model = 'gpt-4o-mini') {
    const response = await this.client.post('/critique', {
      code,
      domain_context: domainContext,
      model,
    });
    return response.data;
  }

  // Generate insight
  async generateInsight(title, description, dataSummary, model = 'gpt-4o-mini') {
    const response = await this.client.post('/insight', {
      analysis_title: title,
      chart_description: description,
      data_summary: dataSummary,
      model,
    });
    return response.data;
  }

  // Get chart URL
  getChartURL(imagePath) {
    // imagePath is like "/charts/chart_1234.pdf"
    return `${API_BASE_URL}${imagePath}`;
  }
}

export default new ChartAgentAPI();
```

### Component 2: Main Chart Generator

Create `src/components/ChartGenerator.jsx`:

```javascript
import React, { useState, useEffect } from 'react';
import {
  Container,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Box,
} from '@mui/material';
import chartAgentAPI from '../services/chartAgentAPI';
import CodePreview from './CodePreview';
import ChartViewer from './ChartViewer';

function ChartGenerator() {
  // State management
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState('');
  const [question, setQuestion] = useState('');
  const [context, setContext] = useState('');
  const [model, setModel] = useState('gpt-4o-mini');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [generatedCode, setGeneratedCode] = useState(null);
  const [chartURL, setChartURL] = useState(null);

  // Load datasets on mount
  useEffect(() => {
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    try {
      const data = await chartAgentAPI.getDatasets();
      setDatasets(data.datasets || []);
    } catch (err) {
      setError('Failed to load datasets: ' + err.message);
    }
  };

  const handleGenerate = async () => {
    if (!selectedDataset || !question) {
      setError('Please select a dataset and enter a question');
      return;
    }

    setLoading(true);
    setError(null);
    setGeneratedCode(null);
    setChartURL(null);

    try {
      // Step 1: Generate code
      const result = await chartAgentAPI.analyzeData(
        selectedDataset,
        question,
        context || null,
        model
      );

      setGeneratedCode(result);
    } catch (err) {
      setError('Generation failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async () => {
    if (!generatedCode) return;

    setLoading(true);
    setError(null);

    try {
      const result = await chartAgentAPI.executeCode(
        generatedCode.code,
        selectedDataset,
        'pdf'
      );

      if (result.success) {
        const url = chartAgentAPI.getChartURL(result.image_path);
        setChartURL(url);
      } else {
        setError('Execution failed: ' + result.error);
      }
    } catch (err) {
      setError('Execution failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h3" gutterBottom>
        Chart Agent - AI-Powered Visualization
      </Typography>

      {/* Input Form */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Generate Chart
        </Typography>

        {/* Dataset Selector */}
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Dataset</InputLabel>
          <Select
            value={selectedDataset}
            onChange={(e) => setSelectedDataset(e.target.value)}
            label="Dataset"
          >
            {datasets.map((ds) => (
              <MenuItem key={ds.path} value={ds.path}>
                {ds.name} ({(ds.size_mb).toFixed(2)} MB)
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Question Input */}
        <TextField
          fullWidth
          label="What chart do you want to create?"
          placeholder="e.g., Show the top 20 genes with the most splice sites"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          sx={{ mb: 2 }}
        />

        {/* Context Input */}
        <TextField
          fullWidth
          label="Additional Context (optional)"
          placeholder="e.g., Focus on standard chromosomes only"
          value={context}
          onChange={(e) => setContext(e.target.value)}
          multiline
          rows={2}
          sx={{ mb: 2 }}
        />

        {/* Model Selector */}
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Model</InputLabel>
          <Select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            label="Model"
          >
            <MenuItem value="gpt-4o-mini">GPT-4o Mini (Fast)</MenuItem>
            <MenuItem value="gpt-4o">GPT-4o (Capable)</MenuItem>
            <MenuItem value="gpt-5-mini">GPT-5 Mini</MenuItem>
            <MenuItem value="gpt-5">GPT-5</MenuItem>
            <MenuItem value="gpt-5.1-codex-mini">GPT-5.1 Codex Mini</MenuItem>
          </Select>
        </FormControl>

        {/* Generate Button */}
        <Button
          variant="contained"
          size="large"
          onClick={handleGenerate}
          disabled={loading || !selectedDataset || !question}
          fullWidth
        >
          {loading ? <CircularProgress size={24} /> : 'Generate Code'}
        </Button>
      </Paper>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Generated Code */}
      {generatedCode && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Generated Code
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {generatedCode.explanation}
          </Typography>
          <Typography variant="caption" color="text.secondary" gutterBottom>
            Libraries: {generatedCode.libraries_used.join(', ')}
          </Typography>

          <CodePreview code={generatedCode.code} />

          <Box sx={{ mt: 2 }}>
            <Button
              variant="contained"
              color="success"
              onClick={handleExecute}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Execute & Generate Chart'}
            </Button>
          </Box>
        </Paper>
      )}

      {/* Chart Display */}
      {chartURL && <ChartViewer url={chartURL} />}
    </Container>
  );
}

export default ChartGenerator;
```

### Component 3: Code Preview

Create `src/components/CodePreview.jsx`:

```javascript
import React, { useState } from 'react';
import { Box, IconButton, Tooltip } from '@mui/material';
import { ContentCopy as CopyIcon } from '@mui/icons-material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

function CodePreview({ code }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Box sx={{ position: 'relative', mt: 2 }}>
      <Tooltip title={copied ? 'Copied!' : 'Copy code'}>
        <IconButton
          onClick={handleCopy}
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            zIndex: 1,
            bgcolor: 'background.paper',
          }}
        >
          <CopyIcon />
        </IconButton>
      </Tooltip>

      <SyntaxHighlighter
        language="python"
        style={vscDarkPlus}
        customStyle={{
          borderRadius: '8px',
          fontSize: '14px',
          maxHeight: '400px',
        }}
      >
        {code}
      </SyntaxHighlighter>
    </Box>
  );
}

export default CodePreview;
```

### Component 4: Chart Viewer

Create `src/components/ChartViewer.jsx`:

```javascript
import React from 'react';
import { Paper, Typography, Button, Box } from '@mui/material';
import { Download as DownloadIcon } from '@mui/icons-material';

function ChartViewer({ url }) {
  const handleDownload = () => {
    window.open(url, '_blank');
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">Generated Chart</Typography>
        <Button
          variant="outlined"
          startIcon={<DownloadIcon />}
          onClick={handleDownload}
        >
          Download
        </Button>
      </Box>

      <Box
        sx={{
          width: '100%',
          height: '600px',
          border: '1px solid #ddd',
          borderRadius: '8px',
          overflow: 'hidden',
        }}
      >
        <iframe
          src={url}
          title="Generated Chart"
          style={{
            width: '100%',
            height: '100%',
            border: 'none',
          }}
        />
      </Box>
    </Paper>
  );
}

export default ChartViewer;
```

### Update App.js

Replace `src/App.js`:

```javascript
import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import ChartGenerator from './components/ChartGenerator';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ChartGenerator />
    </ThemeProvider>
  );
}

export default App;
```

## Running the Application

### Step 1: Start the Chart Agent API

```bash
cd chart_agent/server
mamba run -n agentic-ai python manage.py start
```

### Step 2: Start React App

```bash
cd chart-agent-ui
npm start
```

### Step 3: Use the App

1. Select a dataset from the dropdown
2. Enter your question (e.g., "Show top 20 genes")
3. Optionally add context
4. Click "Generate Code"
5. Review the generated code
6. Click "Execute & Generate Chart"
7. View and download the chart!

## Advanced Features

### Add Critique Workflow

```javascript
const [critique, setCritique] = useState(null);

const handleCritique = async () => {
  try {
    const result = await chartAgentAPI.critiqueCode(
      generatedCode.code,
      'Genomics research on splice sites',
      model
    );
    setCritique(result);
  } catch (err) {
    setError('Critique failed: ' + err.message);
  }
};
```

### Add Loading States

```javascript
const [loadingStates, setLoadingStates] = useState({
  generating: false,
  executing: false,
  critiquing: false,
});
```

### Add Error Boundaries

```javascript
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <h1>Something went wrong.</h1>;
    }
    return this.props.children;
  }
}
```

## Deployment

### Build for Production

```bash
npm run build
```

Creates optimized production build in `build/` directory.

### Deploy to Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=build
```

### Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### Environment Variables

Create `.env` file:

```bash
REACT_APP_API_BASE_URL=http://localhost:8003
```

Update API service:

```javascript
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8003';
```

## Best Practices

1. **Error Handling** - Always wrap API calls in try-catch
2. **Loading States** - Show spinners during async operations
3. **Validation** - Validate inputs before sending to API
4. **Debouncing** - Debounce search/input fields
5. **Caching** - Cache datasets list to reduce API calls
6. **Accessibility** - Use semantic HTML and ARIA labels
7. **Responsive Design** - Test on mobile, tablet, desktop
8. **Code Splitting** - Use React.lazy() for large components

## Troubleshooting

### CORS Errors

The API already enables CORS. If you still see errors:

```javascript
// In chartAgentAPI.js
this.client = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // Add this
});
```

### API Connection Issues

Check if API is running:

```bash
curl http://localhost:8003/health
```

### Build Errors

Clear cache and reinstall:

```bash
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

1. **Add authentication** - Protect API with tokens
2. **Add chart history** - Store generated charts
3. **Add collaboration** - Share charts with team
4. **Add export options** - PNG, SVG, PDF downloads
5. **Add chart editing** - Modify generated code inline

## Resources

- **React Docs**: https://react.dev/
- **Material-UI**: https://mui.com/
- **Axios**: https://axios-http.com/
- **Chart Agent API**: [../../server/QUICKSTART.md](../../server/QUICKSTART.md)
