# Contributing to YOLO Object Detector

First off, thank you for considering contributing to YOLO Object Detector! 🎉

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)

---

## 📜 Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please be respectful and constructive in all interactions.

---

## 🤝 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**When submitting a bug report, include:**
- Clear and descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Screenshots (if applicable)
- Environment details:
  - OS and version
  - Flutter version
  - Python version
  - Cloud Run region

**Example:**
```
Title: Detection fails for images larger than 5MB

Description:
When uploading images larger than 5MB through the Flutter app,
the detection times out after 60 seconds.

Steps to reproduce:
1. Open Flutter app
2. Select image from gallery (6MB)
3. Wait for processing
4. Timeout error appears

Expected: Image should be processed
Actual: Timeout after 60 seconds

Environment:
- Flutter 3.16.0
- Android 13
- Cloud Run us-central1
```

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:
- Clear use case
- Expected benefits
- Possible implementation approach

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Test thoroughly
5. Commit with descriptive messages
6. Push to your fork
7. Open a Pull Request

---

## 🛠️ Development Setup

### Prerequisites

```bash
# Install Flutter
brew install flutter  # macOS
# or download from https://flutter.dev

# Install Python 3.11+
brew install python@3.11

# Install Docker
brew install --cask docker

# Install Firebase CLI
npm install -g firebase-tools

# Install gcloud CLI
brew install --cask google-cloud-sdk
```

### Local Setup

```bash
# 1. Clone your fork
git clone https://github.com/YOUR_USERNAME/yolo-object-detector.git
cd yolo-object-detector

# 2. Set up mobile
cd mobile
flutter pub get

# 3. Set up backend
cd ../backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Set up functions
cd ../functions
pip install -r requirements.txt
```

### Running Tests

```bash
# Flutter tests
cd mobile
flutter test
flutter analyze

# Python tests (if available)
cd backend
pytest

# Integration tests
# See test/ directory
```

---

## 💻 Coding Standards

### Flutter / Dart

- Follow [Effective Dart](https://dart.dev/guides/language/effective-dart)
- Use `flutter format` before committing
- Run `flutter analyze` and fix all issues
- Add documentation comments for public APIs

```dart
/// Processes an image and returns detection results.
///
/// The [imageFile] must be a valid image file (JPG, PNG).
/// Returns a [Future] that completes with detection results.
Future<DetectionResult> processImage(File imageFile) async {
  // Implementation
}
```

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints
- Add docstrings to functions
- Use `black` for formatting
- Use `pylint` or `flake8` for linting

```python
def run_inference(
    input_image: Image.Image, 
    confidence_threshold: float = 0.25
) -> Dict[str, Any]:
    """
    Run YOLO inference on an image.
    
    Args:
        input_image: PIL Image to process
        confidence_threshold: Minimum confidence (0.0-1.0)
    
    Returns:
        Dictionary with 'detections' and 'results'
    """
    # Implementation
```

### File Organization

- Keep files focused and single-purpose
- Use meaningful names
- Group related functionality
- Avoid large files (>500 lines)

---

## 📝 Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**

```
feat(mobile): add image compression before upload

Reduces upload time and bandwidth by compressing images
to 85% quality before uploading to Firebase Storage.

Closes #123
```

```
fix(backend): resolve timeout on large images

Increased Cloud Run timeout from 60s to 300s to handle
larger images. Also added retry logic.

Fixes #456
```

```
docs(readme): update deployment instructions

Added troubleshooting section and improved clarity
of Cloud Run deployment steps.
```

---

## 🔄 Pull Request Process

### Before Submitting

1. **Update your fork:**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run tests:**
   ```bash
   flutter test
   flutter analyze
   pytest  # if applicable
   ```

3. **Update documentation:**
   - Update README if needed
   - Add/update code comments
   - Update CHANGELOG if exists

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] I have tested these changes locally
- [ ] All existing tests pass
- [ ] I have added tests for new features

## Checklist
- [ ] My code follows the project's coding standards
- [ ] I have commented my code where necessary
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have checked for any TODO comments

## Screenshots (if applicable)
Add screenshots for UI changes

## Related Issues
Closes #123
Related to #456
```

### Review Process

1. At least one maintainer must approve
2. All CI checks must pass
3. No merge conflicts
4. Code review feedback addressed

### After Merging

- Delete your feature branch
- Update your fork
- Celebrate! 🎉

---

## 🏗️ Project Areas

### Mobile (Flutter)
- UI/UX improvements
- New features
- Performance optimization
- Platform-specific fixes

**Good first issues:**
- Add loading animations
- Improve error messages
- Add settings screen
- Support for more image formats

### Backend (Cloud Run)
- YOLO model updates
- API improvements
- Performance optimization
- New detection features

**Good first issues:**
- Add health check details
- Improve logging
- Optimize image processing
- Add batch detection endpoint

### Functions (Cloud Functions)
- Workflow improvements
- Error handling
- Monitoring
- Performance optimization

**Good first issues:**
- Add more detailed logging
- Improve retry logic
- Add metrics
- Better error messages

### Documentation
- README improvements
- Code comments
- Architecture diagrams
- Tutorials

**Good first issues:**
- Fix typos
- Add examples
- Improve setup instructions
- Add troubleshooting guides

---

## 🎯 Priority Labels

Issues are labeled to help contributors:

- `good first issue` - Perfect for newcomers
- `help wanted` - Maintainers need help
- `bug` - Something isn't working
- `enhancement` - New feature request
- `documentation` - Documentation improvements
- `priority: high` - Important issues

---

## ❓ Questions?

- Open an issue with the `question` label
- Check existing issues and discussions
- Read the documentation thoroughly

---

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

---

Happy coding! 💻✨
