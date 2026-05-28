# /sql - SQL Query Optimization

Analyze and optimize SQL queries.

## Usage
```
/sql "SELECT * FROM users..."    # Analyze query
/sql --explain                   # Generate EXPLAIN plan
/sql --index                     # Suggest indexes
/sql --rewrite                   # Rewrite for performance
```

## What This Skill Does

1. **Analyze Query** - Parse and understand intent
2. **Identify Issues** - N+1, missing indexes, bad patterns
3. **Suggest Indexes** - Based on WHERE/JOIN/ORDER BY
4. **Rewrite Query** - Optimized version
5. **Explain Performance** - Why changes help

## Query Analysis Report

```markdown
# SQL Analysis

## Original Query
```sql
SELECT u.*, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id
ORDER BY order_count DESC
LIMIT 100;
```

## Issues Found

### 1. SELECT * Anti-pattern
**Problem**: Selects all columns, may fetch unnecessary data
**Impact**: More memory, slower network transfer
**Fix**: Specify only needed columns

### 2. Missing Index
**Problem**: No index on `users.created_at`
**Impact**: Full table scan for date filter
**Fix**: `CREATE INDEX idx_users_created_at ON users(created_at);`

### 3. Missing Index
**Problem**: No index on `orders.user_id`
**Impact**: Slow JOIN operation
**Fix**: `CREATE INDEX idx_orders_user_id ON orders(user_id);`

## Optimized Query
```sql
SELECT
    u.id,
    u.username,
    u.email,
    COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id, u.username, u.email
ORDER BY order_count DESC
LIMIT 100;
```

## Suggested Indexes
```sql
-- For WHERE clause filtering
CREATE INDEX idx_users_created_at ON users(created_at);

-- For JOIN performance
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Composite index for common query pattern
CREATE INDEX idx_users_created_at_id ON users(created_at, id);
```

## Expected Improvement
- Query time: ~500ms → ~50ms (10x faster)
- Rows scanned: 100,000 → 5,000
```

## Common Anti-Patterns

### SELECT *
```sql
-- Bad
SELECT * FROM users WHERE id = 1;

-- Good
SELECT id, username, email FROM users WHERE id = 1;
```

### N+1 Queries
```sql
-- Bad: N+1 (1 query + N queries)
SELECT * FROM users;
-- Then for each user:
SELECT * FROM orders WHERE user_id = ?;

-- Good: Single query with JOIN
SELECT u.*, o.*
FROM users u
LEFT JOIN orders o ON o.user_id = u.id;
```

### Missing LIMIT
```sql
-- Bad: May return millions of rows
SELECT * FROM logs WHERE level = 'ERROR';

-- Good: Bounded result set
SELECT * FROM logs WHERE level = 'ERROR' LIMIT 1000;
```

### Using OR with different columns
```sql
-- Bad: Can't use indexes efficiently
SELECT * FROM users WHERE email = 'x' OR username = 'y';

-- Good: Use UNION
SELECT * FROM users WHERE email = 'x'
UNION
SELECT * FROM users WHERE username = 'y';
```

### LIKE with leading wildcard
```sql
-- Bad: Can't use index
SELECT * FROM products WHERE name LIKE '%phone%';

-- Good: Use full-text search
SELECT * FROM products WHERE MATCH(name) AGAINST('phone');
```

## Index Guidelines

### When to Create Indexes
- Columns in WHERE clauses
- Columns in JOIN conditions
- Columns in ORDER BY
- Columns in GROUP BY
- Foreign key columns

### When NOT to Create Indexes
- Small tables (< 1000 rows)
- Columns with low cardinality (e.g., boolean)
- Columns rarely used in queries
- Tables with heavy writes

### Composite Index Order
```sql
-- Index on (a, b, c) can be used for:
WHERE a = ?
WHERE a = ? AND b = ?
WHERE a = ? AND b = ? AND c = ?

-- But NOT for:
WHERE b = ?
WHERE c = ?
WHERE b = ? AND c = ?
```

## EXPLAIN Analysis

```sql
EXPLAIN ANALYZE SELECT ...;
```

### Key Metrics
| Metric | Good | Bad |
|--------|------|-----|
| Seq Scan | Small tables | Large tables |
| Index Scan | Large tables | - |
| Rows | Low estimate | High estimate |
| Cost | Low | High |

## Instructions for Claude

When /sql is invoked:

1. **Parse query** - Understand structure and intent
2. **Identify tables** - What data is being accessed
3. **Check indexes** - Are WHERE/JOIN columns indexed?
4. **Find anti-patterns** - SELECT *, N+1, missing LIMIT
5. **Suggest indexes** - Based on query patterns
6. **Rewrite query** - Optimized version
7. **Explain changes** - Why each change helps
8. **Estimate improvement** - Expected performance gain
