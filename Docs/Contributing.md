# Contributing to TinyRAG

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## Development Process

### 1. Setting Up Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/tiny-RAG.git
   cd tiny-RAG
   ```

2. **Set Up Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

3. **Set Up Node.js Environment**
   ```bash
   cd rag-memo-ui
   npm install
   ```

### 2. Code Style Guidelines

#### Python Code Style
- Follow PEP 8 guidelines
- Use Ruff for linting and formatting
- All functions must have type hints
- Use Google-style docstrings
- Maximum line length: 88 characters

Example:
```python
from typing import List, Optional

def process_document(
    file_path: str,
    chunk_size: int = 1000,
    overlap: Optional[int] = None
) -> List[str]:
    """Process a document and return chunks of text.

    Args:
        file_path: Path to the document file.
        chunk_size: Size of each text chunk in characters.
        overlap: Number of characters to overlap between chunks.

    Returns:
        List of text chunks.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If chunk_size is less than 1.
    """
    if chunk_size < 1:
        raise ValueError("chunk_size must be at least 1")
    # Implementation...
```

#### TypeScript/JavaScript Code Style
- Use ESLint and Prettier
- Follow Airbnb style guide
- Use TypeScript for type safety
- Use JSDoc comments

Example:
```typescript
/**
 * Processes a document and returns chunks of text.
 * @param {string} filePath - Path to the document file
 * @param {number} chunkSize - Size of each text chunk in characters
 * @param {number} [overlap] - Number of characters to overlap between chunks
 * @returns {string[]} List of text chunks
 * @throws {Error} If file doesn't exist or chunkSize is invalid
 */
function processDocument(
  filePath: string,
  chunkSize: number = 1000,
  overlap?: number
): string[] {
  // Implementation...
}
```

### 3. Git Workflow

1. **Branch Naming**
   - Feature: `feature/description`
   - Bugfix: `fix/description`
   - Documentation: `docs/description`
   - Refactor: `refactor/description`

2. **Commit Messages**
   ```
   type(scope): description

   [optional body]

   [optional footer]
   ```

   Types:
   - feat: New feature
   - fix: Bug fix
   - docs: Documentation
   - style: Formatting
   - refactor: Code restructuring
   - test: Adding tests
   - chore: Maintenance

3. **Pull Request Process**
   - Create PR from feature branch to main
   - Fill out PR template
   - Ensure CI passes
   - Get at least one review
   - Address review comments
   - Merge after approval

### 4. Testing Guidelines

#### Backend Testing
- Use pytest for unit tests
- Aim for 90%+ coverage
- Test both success and failure cases
- Mock external dependencies

Example:
```python
def test_process_document():
    # Arrange
    test_file = "test_doc.pdf"
    expected_chunks = ["chunk1", "chunk2"]
    
    # Act
    result = process_document(test_file)
    
    # Assert
    assert result == expected_chunks
```

#### Frontend Testing
- Use Jest and React Testing Library
- Test component rendering
- Test user interactions
- Mock API calls

Example:
```typescript
describe('DocumentUpload', () => {
  it('should handle file upload', async () => {
    // Arrange
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
    
    // Act
    render(<DocumentUpload />);
    fireEvent.change(screen.getByTestId('file-input'), { target: { files: [file] } });
    
    // Assert
    expect(await screen.findByText('Upload complete')).toBeInTheDocument();
  });
});
```

### 5. Documentation

- Update README.md for significant changes
- Document new features in docs/
- Keep API documentation up to date
- Add comments for complex logic

### 6. Review Process

1. **Code Review Checklist**
   - [ ] Code follows style guide
   - [ ] Tests are included
   - [ ] Documentation is updated
   - [ ] No security vulnerabilities
   - [ ] Performance is considered

2. **Review Guidelines**
   - Be constructive and respectful
   - Focus on code quality
   - Consider edge cases
   - Check for security issues

### 7. Release Process

1. **Version Bumping**
   - Follow semantic versioning
   - Update version in all relevant files
   - Update CHANGELOG.md

2. **Release Checklist**
   - [ ] All tests pass
   - [ ] Documentation is updated
   - [ ] Changelog is updated
   - [ ] Version is bumped
   - [ ] Release notes are prepared

## Getting Help

- Create an issue for bugs
- Use discussions for questions
- Join our community chat
- Check the FAQ

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License. 