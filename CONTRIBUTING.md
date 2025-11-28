# Contributing to Conditional Access Policy Manager

Thank you for considering contributing to this project! 🎉

## How to Contribute

### Reporting Bugs 🐛

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template** (if available)
3. **Include**:
   - Python version
   - Operating system
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages or logs
   - **Never include credentials or tenant data**

### Suggesting Features 💡

1. **Open a GitHub Issue** with the "Feature Request" label
2. **Describe**:
   - The problem you're trying to solve
   - Your proposed solution
   - Alternative approaches considered
   - Any relevant examples or mockups

### Submitting Pull Requests 🔧

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow existing code style
   - Add docstrings to new functions
   - Update documentation as needed
   - Test your changes

4. **Commit with clear messages**
   ```bash
   git commit -m "Add: Feature description"
   ```
   Use prefixes: `Add:`, `Fix:`, `Update:`, `Refactor:`, `Docs:`

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Describe what changed and why
   - Reference related issues
   - Include screenshots if UI changed

### Code Style Guidelines

#### Python
- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small
- Use type hints where helpful

```python
def create_policy(policy_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new Conditional Access policy.
    
    Args:
        policy_data: Dictionary containing policy configuration
        
    Returns:
        Dictionary with created policy details
        
    Raises:
        ValueError: If policy_data is invalid
    """
    pass
```

#### JavaScript
- Use modern ES6+ syntax
- Use `const` and `let` (not `var`)
- Add JSDoc comments for functions
- Keep functions pure when possible

```javascript
/**
 * Load and display named locations
 * @returns {Promise<void>}
 */
async function loadNamedLocations() {
    // Implementation
}
```

#### HTML/CSS
- Semantic HTML5 tags
- Accessible markup (ARIA labels)
- Responsive design
- Follow Bootstrap conventions
- Keep inline styles minimal

### Testing

Before submitting:
- Test on a clean environment
- Verify with both authentication methods
- Check browser console for errors
- Test with and without AI features enabled
- Ensure no credentials are exposed

### Documentation

Update documentation when you:
- Add new features
- Change configuration options
- Modify API endpoints
- Update dependencies
- Change setup procedures

Documentation files to consider:
- `README.md` - Main overview
- `QUICKSTART.md` - Quick start guide
- `AI_SETUP_GUIDE.md` - AI feature setup
- Inline code comments
- Docstrings

### Security Considerations ⚠️

**NEVER commit**:
- `.env` files with real credentials
- `config.json` with tenant IDs
- Access tokens or API keys
- User data or tenant information
- Log files with sensitive data

**ALWAYS**:
- Use environment variables for secrets
- Update `.env.example` with new variables
- Sanitize any screenshots or examples
- Review `git diff` before committing

See `SECURITY.md` for full security guidelines.

## Development Setup

### Prerequisites
- Python 3.11+
- pip and virtualenv
- Azure AD tenant (for testing)
- Git

### Local Development

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/conditional-access-policy-manager.git
cd conditional-access-policy-manager

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Install dependencies
cd CA_Policy_Manager_Web
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials

# Run development server
python app.py
```

### Project Structure

```
CA_Policy_Manager_Web/
├── app.py              # Main Flask application
├── config.py           # Configuration management
├── ca_policy_examples.py  # Policy templates
├── utils/              # Utility modules
│   └── ai_assistant.py
├── static/             # CSS, JS, images
├── templates/          # HTML templates
└── requirements.txt    # Python dependencies
```

## Code Review Process

1. All PRs require review before merging
2. CI/CD checks must pass (if configured)
3. Documentation must be updated
4. No merge conflicts
5. Security review for sensitive changes

## Community Guidelines

### Be Respectful
- Welcome newcomers
- Be patient with questions
- Provide constructive feedback
- Assume good intentions

### Be Collaborative
- Share knowledge
- Help others learn
- Review PRs thoughtfully
- Celebrate contributions

### Be Professional
- Stay on topic
- No harassment or discrimination
- Follow GitHub Community Guidelines
- Keep discussions productive

## Questions?

- **General questions**: Open a GitHub Discussion
- **Bug reports**: Open a GitHub Issue
- **Security concerns**: See `SECURITY.md`
- **Feature ideas**: Open a Feature Request issue

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing!** 🚀
