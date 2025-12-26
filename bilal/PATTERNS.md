# Architectural Patterns

Bilal's preferred architectural patterns and approaches.

---

## Overall Architecture

**Prefer:**
- Layered architecture (Controller → Service → Repository → Model)
- Separation of concerns
- Dependency injection
- Single Responsibility Principle

**Avoid:**
- God objects (classes that do everything)
- Tight coupling
- Business logic in controllers
- Direct database access from controllers

---

## Backend Patterns

### Controller-Service-Repository

```typescript
// Controller: Handle HTTP, validate, delegate
class UserController {
  constructor(private userService: UserService) {}

  async createUser(req: Request, res: Response) {
    // Validate request
    const validated = validateUserInput(req.body);

    // Delegate to service
    const user = await this.userService.createUser(validated);

    // Return response
    return res.json(user);
  }
}

// Service: Business logic
class UserService {
  constructor(private userRepo: UserRepository) {}

  async createUser(data: CreateUserDto): Promise<User> {
    // Business logic here
    if (await this.userRepo.existsByEmail(data.email)) {
      throw new ConflictError('Email already exists');
    }

    // Delegate to repository
    return this.userRepo.create(data);
  }
}

// Repository: Data access
class UserRepository {
  async create(data: CreateUserDto): Promise<User> {
    // Database operations only
    return User.create(data);
  }

  async existsByEmail(email: string): Promise<boolean> {
    return User.exists({ email });
  }
}
```

### Dependency Injection

```typescript
// ✅ Good: Inject dependencies
class UserService {
  constructor(
    private userRepo: UserRepository,
    private emailService: EmailService
  ) {}
}

// ❌ Bad: Create dependencies internally
class UserService {
  private userRepo = new UserRepository();
  private emailService = new EmailService();
}
```

---

## Frontend Patterns

### Component Structure

```typescript
// Presentational Component: Just UI
function UserCard({ user, onEdit }: UserCardProps) {
  return (
    <div className="user-card">
      <h3>{user.name}</h3>
      <button onClick={() => onEdit(user.id)}>Edit</button>
    </div>
  );
}

// Container Component: Logic + data
function UserCardContainer({ userId }: { userId: string }) {
  const { data: user, isLoading } = useUser(userId);
  const { mutate: updateUser } = useUpdateUser();

  const handleEdit = (id: string) => {
    // Handle edit logic
  };

  if (isLoading) return <Spinner />;

  return <UserCard user={user} onEdit={handleEdit} />;
}
```

### Custom Hooks

```typescript
// ✅ Good: Extract reusable logic
function useUser(userId: string) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchUser(userId).then(setUser).finally(() => setIsLoading(false));
  }, [userId]);

  return { user, isLoading };
}

// Usage
function UserProfile({ userId }: Props) {
  const { user, isLoading } = useUser(userId);
  // ...
}
```

---

## Database Patterns

### Migrations

```php
// ✅ Good: Descriptive, reversible migrations
Schema::create('users', function (Blueprint $table) {
    $table->id();
    $table->string('email')->unique();
    $table->string('name');
    $table->timestamp('email_verified_at')->nullable();
    $table->timestamps();
    $table->softDeletes();
});

// Always implement down() method
Schema::dropIfExists('users');
```

### Query Optimization

```typescript
// ✅ Good: Eager loading
const users = await User.find({
  relations: ['profile', 'posts']
});

// ❌ Bad: N+1 query
const users = await User.find();
for (const user of users) {
  const profile = await Profile.findOne({ userId: user.id });
}
```

### Transactions

```typescript
// ✅ Good: Use transactions for related operations
await db.transaction(async (trx) => {
  const user = await User.create(userData, { transaction: trx });
  await Profile.create({ userId: user.id, ...profileData }, { transaction: trx });
  await sendWelcomeEmail(user.email);
});
```

---

## Error Handling

### Custom Errors

```typescript
// Define specific error types
class ValidationError extends Error {
  constructor(message: string, public field: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

class NotFoundError extends Error {
  constructor(resource: string, id: string) {
    super(`${resource} with ID ${id} not found`);
    this.name = 'NotFoundError';
  }
}

// Use them
if (!user) {
  throw new NotFoundError('User', userId);
}
```

### Error Middleware

```typescript
// Centralized error handling
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  if (err instanceof ValidationError) {
    return res.status(400).json({ error: err.message, field: err.field });
  }

  if (err instanceof NotFoundError) {
    return res.status(404).json({ error: err.message });
  }

  // Log unexpected errors
  logger.error('Unexpected error', { error: err });
  return res.status(500).json({ error: 'Internal server error' });
});
```

---

## API Design

### RESTful Endpoints

```
GET    /api/users           - List users
GET    /api/users/:id       - Get user
POST   /api/users           - Create user
PUT    /api/users/:id       - Update user (full)
PATCH  /api/users/:id       - Update user (partial)
DELETE /api/users/:id       - Delete user
```

### Response Format

```typescript
// Success response
{
  "data": { ... },
  "meta": {
    "page": 1,
    "perPage": 20,
    "total": 100
  }
}

// Error response
{
  "error": "Validation failed",
  "details": [
    { "field": "email", "message": "Invalid email format" }
  ]
}
```

---

## Validation

### Input Validation

```typescript
// Define schemas
const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2).max(100),
  age: z.number().int().min(18).optional()
});

// Validate
function createUser(input: unknown) {
  const validated = CreateUserSchema.parse(input);
  // Now validated has correct types
}
```

---

## Testing Patterns

### Unit Tests

```typescript
describe('UserService', () => {
  let service: UserService;
  let mockRepo: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockRepo = {
      create: jest.fn(),
      existsByEmail: jest.fn()
    } as any;

    service = new UserService(mockRepo);
  });

  it('should create user when email is unique', async () => {
    // Arrange
    mockRepo.existsByEmail.mockResolvedValue(false);
    mockRepo.create.mockResolvedValue({ id: '1', email: 'test@example.com' });

    // Act
    const result = await service.createUser({ email: 'test@example.com' });

    // Assert
    expect(result).toEqual({ id: '1', email: 'test@example.com' });
    expect(mockRepo.create).toHaveBeenCalledWith({ email: 'test@example.com' });
  });
});
```

---

## Configuration

### Environment Variables

```typescript
// ✅ Good: Centralized config
export const config = {
  port: process.env.PORT || 3000,
  database: {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432'),
  },
  jwt: {
    secret: process.env.JWT_SECRET || 'dev-secret',
    expiresIn: process.env.JWT_EXPIRES || '1d',
  }
};

// ❌ Bad: Scattered process.env calls
const port = process.env.PORT;
// ... later in code
const secret = process.env.JWT_SECRET;
```

---

## Summary

| Pattern | Use For |
|---------|---------|
| Controller-Service-Repository | Backend structure |
| Dependency Injection | Loose coupling |
| Custom Hooks | Reusable React logic |
| Error Classes | Type-safe error handling |
| Eager Loading | Avoid N+1 queries |
| Transactions | Related database operations |
| Validation Schemas | Input validation |
| Centralized Config | Environment management |
