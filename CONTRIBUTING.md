# Contributing to RarePath AI

Thank you for your interest in contributing to RarePath AI! This project aims to help patients with rare diseases navigate their diagnostic journey using AI-powered multi-agent systems.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Any relevant logs or error messages

### Suggesting Features

We welcome feature suggestions! Please open an issue with:
- A clear description of the feature
- Why it would be useful
- Any implementation ideas you have

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/rarepath-ai.git
   cd rarepath-ai
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the code style guidelines below
   - Add tests if applicable
   - Update documentation as needed

4. **Test your changes**
   ```bash
   python tests/test_quick.py
   python tests/test_agents.py
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```
   
   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `refactor:` for code refactoring
   - `test:` for adding tests

6. **Push and create a PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then open a pull request on GitHub.

## 📝 Code Style Guidelines

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and under 50 lines when possible
- Add type hints where appropriate

Example:
```python
def search_pubmed(query: str, max_results: int = 10) -> List[Dict]:
    """
    Search PubMed for medical literature.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of article dictionaries with title, abstract, etc.
    """
    # Implementation
    pass
```

## 🧪 Testing

- Add tests for new features
- Ensure existing tests pass
- Test with different symptom inputs
- Verify API integrations work correctly

## 📚 Documentation

When adding features, please update:
- README.md if it changes usage
- DEPLOYMENT.md if it affects deployment
- Code comments and docstrings
- Any relevant markdown documentation

## 🔒 Security

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Report security vulnerabilities privately via email (not public issues)

## ⚖️ Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Remember this project helps real patients

## 🎯 Priority Areas

We're especially interested in contributions for:
- Additional medical data sources
- Improved symptom aggregation algorithms
- Better specialist matching
- Multi-language support
- Accessibility improvements
- Performance optimizations

## ❓ Questions?

Feel free to open a discussion or issue if you have questions about contributing!

---

Thank you for helping make rare disease diagnosis more accessible! 🏥💙
