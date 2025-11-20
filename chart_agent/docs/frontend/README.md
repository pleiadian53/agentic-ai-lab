# Frontend Integration Guides

Comprehensive tutorials for integrating the Chart Agent API with various frontend technologies.

## 📚 Available Tutorials

### [Swagger UI Guide](SWAGGER_UI.md)
**Interactive API testing and documentation**

- What is Swagger UI and why use it
- Step-by-step endpoint testing
- Common workflows (generate → execute → view)
- Troubleshooting validation errors
- Tips and best practices

**Best for:** Quick testing, API exploration, sharing docs with team

---

### [React Integration](REACT.md)
**Build a modern web application**

- Complete React app setup
- API service layer with Axios
- Reusable UI components
- Material-UI integration
- Code preview with syntax highlighting
- Chart viewer with PDF/PNG support
- Deployment to Netlify/Vercel

**Best for:** Production web applications, custom branding, complex UI

---

### [Streamlit Tutorial](STREAMLIT.md)
**Rapid prototyping with Python**

- Pure Python web app (no JavaScript)
- Built-in widgets and layouts
- Session state management
- Caching for performance
- One-click deployment to Streamlit Cloud
- Critique workflow integration

**Best for:** Data science teams, rapid prototypes, internal tools

---

### [cURL Guide](CURL.md)
**Command-line API usage**

- Basic cURL syntax and options
- Complete workflow automation
- Bash scripting examples
- CI/CD integration
- Error handling and debugging
- Performance testing

**Best for:** Automation, scripts, CI/CD pipelines, debugging

---

## 🚀 Quick Start

### 1. Start the Chart Agent API

```bash
cd chart_agent/server
mamba run -n agentic-ai python manage.py start
```

Verify it's running:
```bash
curl http://localhost:8003/health
```

### 2. Choose Your Frontend

| Technology | Setup Time | Complexity | Best Use Case |
|------------|------------|------------|---------------|
| **Swagger UI** | 0 min | None | Testing, documentation |
| **cURL** | 0 min | Low | Automation, scripts |
| **Streamlit** | 5 min | Low | Data apps, prototypes |
| **React** | 30 min | Medium | Production web apps |

### 3. Follow the Tutorial

Each tutorial includes:
- ✅ Prerequisites and installation
- ✅ Complete working code examples
- ✅ Step-by-step instructions
- ✅ Troubleshooting guide
- ✅ Best practices
- ✅ Deployment instructions

## 📖 Technology Overview

### Swagger UI
**Interactive API documentation built into FastAPI**

```
Access: http://localhost:8003/docs
```

**Pros:**
- Zero setup required
- Auto-generated from code
- Interactive testing
- Great for sharing API docs

**Cons:**
- Limited customization
- No application logic
- Browser-only

---

### React
**JavaScript library for building user interfaces**

**Pros:**
- Full control over UI/UX
- Rich ecosystem
- Production-ready
- Component reusability

**Cons:**
- Requires JavaScript knowledge
- More complex setup
- Separate deployment

**Key Libraries:**
- `axios` - HTTP client
- `@mui/material` - UI components
- `react-syntax-highlighter` - Code display

---

### Streamlit
**Python framework for data apps**

**Pros:**
- Pure Python (no JavaScript)
- Very fast development
- Built-in widgets
- Easy deployment

**Cons:**
- Less customization
- Python-only
- Limited UI flexibility

**Key Features:**
- Session state
- Caching decorators
- File uploads
- Chart display

---

### cURL
**Command-line tool for HTTP requests**

**Pros:**
- Pre-installed everywhere
- Perfect for automation
- Simple and fast
- Great for debugging

**Cons:**
- No UI
- Manual JSON handling
- Command-line only

**Use Cases:**
- CI/CD pipelines
- Cron jobs
- Shell scripts
- Quick testing

---

## 🎯 Choosing the Right Tool

### For Testing & Exploration
→ **Swagger UI** or **cURL**

### For Data Science Teams
→ **Streamlit**

### For Production Web Apps
→ **React**

### For Automation
→ **cURL** or **Python requests**

### For Internal Tools
→ **Streamlit** or **React**

### For Mobile Apps
→ **React Native** (use React tutorial as base)

---

## 🔧 Common Integration Patterns

### Pattern 1: Human-in-the-Loop

```
1. Generate code (/analyze)
2. User reviews code
3. User approves
4. Execute code (/execute)
5. Display chart
```

**Best with:** Swagger UI, React, Streamlit

---

### Pattern 2: Fully Automated

```
1. Generate code (/analyze)
2. Execute immediately (/execute)
3. Save/display chart
```

**Best with:** cURL, Python scripts

---

### Pattern 3: Iterative Refinement

```
1. Generate code (/analyze)
2. Critique code (/critique)
3. Review feedback
4. Regenerate if needed
5. Execute final version (/execute)
```

**Best with:** React, Streamlit

---

### Pattern 4: Batch Processing

```
For each question:
  1. Generate code
  2. Execute code
  3. Save chart
Generate report with all charts
```

**Best with:** cURL, Python scripts

---

## 📦 Additional Technologies

### Other Frontend Options

**Vue.js** - Similar to React, simpler learning curve
- Use React tutorial as reference
- Replace React components with Vue components
- Use `axios` for API calls

**Angular** - Full-featured framework
- More opinionated than React
- Built-in HTTP client
- TypeScript by default

**Svelte** - Compile-time framework
- Less boilerplate than React
- Excellent performance
- Growing ecosystem

**Vanilla JavaScript** - No framework
- Lightest weight
- Full control
- More manual work

### Backend Integration

**Flask/Django** - Python web frameworks
- Call Chart Agent API from backend
- Serve charts to frontend
- Add authentication/authorization

**FastAPI** - Python async framework
- Integrate directly with Chart Agent
- Share OpenAI client
- Unified service

**Node.js/Express** - JavaScript backend
- Proxy requests to Chart Agent
- Add caching layer
- Handle file uploads

### Mobile Apps

**React Native** - Mobile apps with React
- Reuse React components
- iOS and Android
- Native performance

**Flutter** - Google's mobile framework
- Dart language
- Beautiful UI
- Cross-platform

### Desktop Apps

**Electron** - Desktop apps with web tech
- Package React app
- Windows, Mac, Linux
- Full system access

**Tauri** - Lightweight Electron alternative
- Rust backend
- Smaller bundle size
- Better performance

---

## 🛠️ Development Tools

### API Testing
- **Postman** - GUI for API testing
- **Insomnia** - Alternative to Postman
- **HTTPie** - User-friendly cURL alternative

### Code Editors
- **VS Code** - Best for React/JavaScript
- **PyCharm** - Best for Python/Streamlit
- **Sublime Text** - Lightweight option

### Version Control
- **Git** - Source control
- **GitHub** - Code hosting
- **GitLab** - Alternative to GitHub

### Deployment
- **Netlify** - React apps
- **Vercel** - Next.js/React apps
- **Streamlit Cloud** - Streamlit apps
- **Heroku** - General purpose
- **AWS/GCP/Azure** - Enterprise

---

## 📚 Learning Resources

### React
- [Official React Docs](https://react.dev/)
- [React Tutorial](https://react.dev/learn)
- [Material-UI Docs](https://mui.com/)

### Streamlit
- [Streamlit Docs](https://docs.streamlit.io/)
- [Streamlit Gallery](https://streamlit.io/gallery)
- [Streamlit Cheat Sheet](https://docs.streamlit.io/library/cheatsheet)

### cURL
- [cURL Manual](https://curl.se/docs/manual.html)
- [cURL Tutorial](https://curl.se/docs/httpscripting.html)

### FastAPI/Swagger
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/)

---

## 🤝 Contributing

Have a tutorial for another technology? We'd love to add it!

**Potential additions:**
- Vue.js integration
- Angular integration
- Mobile app (React Native/Flutter)
- Desktop app (Electron/Tauri)
- Jupyter notebook integration
- VS Code extension

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

---

## 📞 Support

- **API Issues**: See [server/QUICKSTART.md](../../server/QUICKSTART.md)
- **Integration Help**: Open an issue on GitHub
- **Questions**: Check existing tutorials first

---

## 🎓 Next Steps

1. **Start with Swagger UI** - Get familiar with the API
2. **Try cURL** - Understand request/response format
3. **Build with Streamlit** - Quick prototype
4. **Scale with React** - Production application

Happy building! 🚀
