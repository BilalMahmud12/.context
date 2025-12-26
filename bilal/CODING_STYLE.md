# Coding Style

Bilal's coding preferences and style guide.

---

## General Principles

**Clarity over cleverness:**
- Write code that's easy to understand
- Prefer explicit over implicit
- Comment when logic isn't obvious
- Name things descriptively

**Simplicity over complexity:**
- Don't over-engineer
- Solve the current problem
- Avoid premature abstraction
- YAGNI (You Aren't Gonna Need It)

**Consistency:**
- Follow existing patterns in the codebase
- Use project's linter/formatter
- Match the surrounding code style

---

## TypeScript / JavaScript

**Naming:**
```typescript
// Classes: PascalCase
class UserService {}

// Interfaces: PascalCase with 'I' prefix optional
interface UserData {}
interface IUserRepository {}

// Functions/Methods: camelCase
function getUserById(id: string) {}

// Variables: camelCase
const userName = 'Bilal';

// Constants: UPPER_SNAKE_CASE
const MAX_RETRIES = 3;

// Private members: prefix with underscore
private _internalState: string;
```

**Functions:**
```typescript
// Prefer arrow functions for short utilities
const add = (a: number, b: number) => a + b;

// Use function declarations for top-level functions
function processUser(user: User): ProcessedUser {
  // Implementation
}

// Always type parameters and return values
function calculate(x: number, y: number): number {
  return x + y;
}
```

**Error Handling:**
```typescript
// Prefer specific error types
throw new ValidationError('Invalid email format');

// Use try-catch for expected errors
try {
  await risky Operation();
} catch (error) {
  logger.error('Operation failed', { error });
  throw error;
}

// Validate inputs early
function processData(data: unknown) {
  if (!isValidData(data)) {
    throw new ValidationError('Invalid data format');
  }
  // Process
}
```

---

## PHP / Laravel

**Naming:**
```php
// Classes: PascalCase
class UserController {}

// Methods: camelCase
public function getUserById(string $id) {}

// Variables: camelCase
$userName = 'Bilal';

// Constants: UPPER_SNAKE_CASE
const MAX_RETRIES = 3;
```

**Laravel Conventions:**
```php
// Models: Singular
class User extends Model {}

// Tables: Plural snake_case
// users, portfolio_items

// Controllers: Resource style
class UserController {
    public function index() {}
    public function store(Request $request) {}
    public function show(User $user) {}
    public function update(Request $request, User $user) {}
    public function destroy(User $user) {}
}

// Routes: Resourceful
Route::resource('users', UserController::class);
```

**Type Declarations:**
```php
// Always use type hints
public function createUser(string $email, string $name): User
{
    return User::create([
        'email' => $email,
        'name' => $name,
    ]);
}

// Use return types
public function getTotal(): float
{
    return $this->items->sum('price');
}
```

---

## File Organization

**TypeScript/JavaScript:**
```
src/
├── controllers/
├── services/
├── models/
├── middleware/
├── utils/
├── types/
└── tests/
```

**Laravel:**
```
app/
├── Http/
│   ├── Controllers/
│   ├── Middleware/
│   └── Requests/
├── Models/
├── Services/
└── Exceptions/
```

---

## Comments

**When to comment:**
```typescript
// ✅ Explain WHY, not WHAT
// Using exponential backoff to handle rate limiting
await retryWithBackoff(apiCall);

// ✅ Document complex business logic
// Calculate pro-rated refund based on days remaining
const refund = (daysLeft / totalDays) * originalPrice;

// ✅ Mark TODOs with context
// TODO: Add caching after we implement Redis (Task #055)
```

**When NOT to comment:**
```typescript
// ❌ Obvious code doesn't need comments
// Get the user
const user = getUserById(id);

// ❌ Don't comment out code (delete it)
// const oldImplementation = () => { ... }

// ❌ Don't leave debug comments
// console.log('here')
```

---

## Testing

**Test file naming:**
```
UserService.ts       → UserService.test.ts
user.controller.php  → UserControllerTest.php
```

**Test structure:**
```typescript
describe('UserService', () => {
  describe('getUserById', () => {
    it('should return user when ID exists', async () => {
      // Arrange
      const userId = '123';
      const expectedUser = { id: '123', name: 'Test' };

      // Act
      const result = await service.getUserById(userId);

      // Assert
      expect(result).toEqual(expectedUser);
    });

    it('should throw error when ID not found', async () => {
      // Arrange
      const userId = 'nonexistent';

      // Act & Assert
      await expect(service.getUserById(userId)).rejects.toThrow();
    });
  });
});
```

---

## Security

**Always:**
- ✅ Sanitize user input
- ✅ Use parameterized queries
- ✅ Validate on both client and server
- ✅ Hash passwords (bcrypt)
- ✅ Use HTTPS
- ✅ Implement rate limiting
- ✅ Set proper CORS policies

**Never:**
- ❌ Trust user input
- ❌ Store passwords in plain text
- ❌ Use string concatenation for SQL
- ❌ Expose sensitive data in errors
- ❌ Commit secrets to git

---

## Performance

**Prefer:**
- ✅ Lazy loading for large datasets
- ✅ Database indexing for frequently queried fields
- ✅ Caching for expensive operations
- ✅ Pagination for lists
- ✅ Debouncing for user input

**Avoid:**
- ❌ N+1 queries (use eager loading)
- ❌ Blocking operations on main thread
- ❌ Loading all data upfront
- ❌ Unnecessary re-renders

---

## Code Review Checklist

Before marking task complete:

- [ ] Code follows project style
- [ ] All tests pass
- [ ] No console.log or debug code
- [ ] No commented-out code
- [ ] No hardcoded values (use config)
- [ ] No secrets or credentials
- [ ] Error handling implemented
- [ ] Input validation added
- [ ] Types/interfaces defined
- [ ] Comments explain complex logic

---

## Summary

| Aspect | Preference |
|--------|------------|
| Philosophy | Clarity, simplicity, consistency |
| Naming | camelCase functions, PascalCase classes |
| Comments | Explain WHY, not WHAT |
| Testing | Required for all new features |
| Security | Validate, sanitize, never trust input |
| Performance | Profile first, optimize what matters |
