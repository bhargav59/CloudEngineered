# 🚀 Quick Start: Google Gemini AI

**Status:** ✅ Ready to Use  
**Cost:** 🎁 FREE (1,500 requests/day)

---

## 30-Second Test

```bash
cd /workspaces/CloudEngineered
python -c "
from apps.ai.gemini_service import get_gemini_service
service = get_gemini_service()
result = service.generate_content('Explain Docker in one sentence')
print(result['content'])
"
```

---

## Basic Usage

### In Django Shell

```bash
python manage.py shell
```

```python
from apps.ai.gemini_service import get_gemini_service

# Get service
gemini = get_gemini_service()

# Generate content
result = gemini.generate_content("Write about Kubernetes")
print(result['content'])
```

### In Django Views

```python
from apps.ai.gemini_service import get_gemini_service

def my_view(request):
    gemini = get_gemini_service()
    
    # Generate content
    result = gemini.generate_content(
        prompt="Explain this tool",
        temperature=0.7
    )
    
    content = result['content']
    tokens = result['tokens_used']
    cost = result['cost']  # Always $0.00
    
    return render(request, 'template.html', {'content': content})
```

---

## Advanced Usage

### Tool Review

```python
review = gemini.generate_tool_review(
    tool_name="Docker",
    tool_description="Container platform",
    tool_features=["Containers", "Images", "Networking"]
)
```

### Tool Comparison

```python
comparison = gemini.generate_tool_comparison(
    tool1_name="Docker",
    tool2_name="Podman",
    tool1_description="Container platform with daemon",
    tool2_description="Daemonless container engine"
)
```

### Blog Article

```python
article = gemini.generate_blog_article(
    title="Getting Started with Kubernetes",
    topic="Kubernetes basics for beginners",
    keywords=["kubernetes", "containers", "orchestration"]
)
```

---

## Configuration

### Current Setup (.env)

```env
GOOGLE_GEMINI_API_KEY=AIzaSyDiI33TKDrgp03fFEEiuBXgP48xi81_m9M
AI_PROVIDER=GEMINI
AI_MODEL=gemini-2.0-flash
USE_OPENROUTER=False
AI_MOCK_MODE=False
```

### Django Settings (config/settings/base.py)

```python
GOOGLE_GEMINI_API_KEY = config('GOOGLE_GEMINI_API_KEY', default='')
AI_PROVIDER = config('AI_PROVIDER', default='GEMINI')
AI_MODEL = config('AI_MODEL', default='gemini-2.0-flash')
USE_OPENROUTER = config('USE_OPENROUTER', default=False, cast=bool)
```

---

## Limits

| Metric | Value |
|--------|-------|
| Daily Requests | 1,500 |
| Rate Limit | 60/minute |
| Cost | $0.00 |

---

## Response Format

```python
{
    'content': 'Generated text...',
    'model': 'gemini-2.0-flash',
    'tokens_used': 52,
    'cost': 0.0,
    'provider': 'Google Gemini',
    'success': True
}
```

---

## Troubleshooting

### Module not found

```bash
pip install google-generativeai
```

### API key error

Check `.env` file:
```bash
grep GOOGLE_GEMINI_API_KEY .env
```

### Server not loading new config

Restart Django:
```bash
python manage.py runserver 0.0.0.0:8000
```

---

## More Info

- **Full Guide:** `GEMINI_SUCCESS_REPORT.md`
- **Integration Details:** `TEST_GEMINI_INTEGRATION.md`
- **API Documentation:** `WORKING_API_GEMINI.md`

---

**🎉 You're ready to generate FREE AI content!**
