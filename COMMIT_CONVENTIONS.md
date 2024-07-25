# Commit Message Writing Documentation

## Commit Message Format

Each commit message should follow a specific format to maintain clarity and consistency. Here’s how to structure your commit messages:

### 1. Header (Subject Line)

**Format:** `<type>: <short summary>`

**Example:** `feat: add Google authentication support`

**Requirements:**
- Use present tense: "add feature," not "added feature."
- Limit the header to 50 characters.
- Do not end the header with a period.
- Use lowercase for type and summary: e.g., `feat: add new feature`.

### 2. Body (Optional)

**Format:** Detailed explanation of the changes.

**Examples:**
```
* Implemented OAuth2 authentication through Google API.
* Updated interface to choose authentication method.
* Added new dependencies in `requirements.txt`.
```
or
```
Added `TaskManager` class, which interacts with an external
API to manage tasks. Implemented methods for creating, updating,
and deleting tasks, as well as for getting a list of tasks. Included
API error handling and result caching to improve performance. Added
token-based authentication support for secure API access.

These changes simplify task management for users, allowing them
to easily interact with the task system via an external API. API
integration ensures data accuracy and consistency.
```

**Requirements:**
- Use bullet points for multiple changes (optional).
- Wrap lines at 72 characters for better readability.
- Explain "why" behind changes, not just "what" was changed.

## Types of Commit Messages

Use the following types for commit messages:

- `feat`: New functionality.
- `fix`: Bug fixes.
- `docs`: Documentation changes.
- `style`: Code style changes that do not affect functionality (e.g., formatting fixes).
- `refactor`: Code changes that do not alter functionality.
- `test`: Adding or updating tests.
- `chore`: Changes to build process or auxiliary tools and libraries.

## Examples

### Feature
```
feat: add support for multiple logins

* Added new mechanism for supporting multiple simultaneous
  user logins.
* Implemented `SessionManager` class to manage sessions and
  ensure security.
* Updated login interface to handle various sessions.
* Added session conflict checks and improved error handling.

These changes enhance user experience by allowing multiple
sessions simultaneously without data loss or security issues.
```

### Fix
```
fix: resolve profile page loading error

Fixed issue where profile page information would not load
under certain conditions. The problem was due to an incorrect
API request. Updated `fetchProfileData` method for proper error
handling and data retrieval.

Users can now correctly load their profile information without
errors.
```
### Documentation
```
docs: update API documentation

* Added descriptions for new API endpoints.
* Updated examples of requests and responses.
* Reorganized documentation structure for clarity.

Documentation is now more complete and easier to understand,
helping developers integrate and use the API more effectively.
```

### Refactor
```
refactor: optimize product search algorithm

* Improved search performance by adding indexes.
* Refactored search code for better readability.

Optimizing the product search is necessary to improve search
speed and efficiency, which will positively impact the overall
user experience. The code was refactored to enhance maintainability
and readability.
```

### Chore
```
chore: add eslint for code style checking

* Installed eslint and added configuration file.
* Fixed all current eslint errors.
* Added script for automatic code checking before commit.

These changes will make our commits more structured and simplify
further development.
```

### Dependency Update
```
chore: update axios library to version 0.21.1

Updated axios to version 0.21.1 for security improvements.
Updated all API calls for compatibility with the new version.
Checked tests to ensure stability after the update.
```

### Removal
```
chore: remove unused components from components directory

Audited code and removed unused components.
Updated imports to remove references to deleted components.
Checked all tests to ensure stability after removal.

These changes remove unnecessary components, which helps keep
the codebase clean and efficient.
```

### Tests
```
test: add unit tests for authentication module

* Wrote unit tests for authentication methods.
* Added tests for error handling correctness.
* Updated existing tests to verify integration with new logic.

These tests will ensure that new and existing authentication
features work correctly and help identify possible data handling
errors.
```

### Style
```
style: fix code formatting in auth.js

* Updated code to match style standards.
* Fixed indentation and spacing for better readability.
* Removed unused variables and imports.

Changes improve code readability and maintainability, ensuring
consistency with accepted formatting standards.
```


### Issue Tracker Link
```
feat: add localization support (#123)

* Implemented support for English and Spanish languages.
* Updated interface to choose language.
* Added translations for all messages and texts.
```

### Bug Report Link
```
fix: fix server crash issue (#456)

* Fixed bug that caused server crashes with certain requests.
* Added tests to check server stability.
* Updated error handling documentation.

Fixing this issue prevents server crashes and ensures stable
system operation. Added tests will help avoid similar problems
in the future.
```

# Conclusion
This documentation includes all the necessary details and formatting to help maintain commit message standards in the project.