# Golden Example: Security Audit Report

Demonstrates a complete audit report with calibrated severity, concrete
evidence, and actionable remediation.

## Input: Node.js Express API

```javascript
// server.js
const express = require('express');
const mysql = require('mysql');
const jwt = require('jsonwebtoken');
const app = express();

app.use(express.json());

const db = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: 'admin123',
  database: 'myapp'
});

const JWT_SECRET = 'supersecretkey123';

app.post('/login', (req, res) => {
  const { username, password } = req.body;
  const query = `SELECT * FROM users WHERE username='${username}' AND password='${password}'`;
  db.query(query, (err, results) => {
    if (results.length > 0) {
      const token = jwt.sign({ id: results[0].id, role: results[0].role }, JWT_SECRET);
      res.json({ token });
    } else {
      res.status(401).json({ error: 'Invalid credentials' });
    }
  });
});

app.get('/users/:id', (req, res) => {
  const query = `SELECT * FROM users WHERE id = ${req.params.id}`;
  db.query(query, (err, results) => {
    res.json(results[0]);
  });
});

app.delete('/users/:id', (req, res) => {
  const token = req.headers.authorization;
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    const query = `DELETE FROM users WHERE id = ${req.params.id}`;
    db.query(query, () => {
      res.json({ deleted: true });
    });
  } catch(e) {
    res.status(401).json({ error: 'Unauthorized' });
  }
});

app.listen(3000, () => console.log('Server on 3000'));
```

## Expected Audit Output

```markdown
# Security Audit Report: Express API

**Date:** 2025-05-14
**Auditor:** Claude Security Auditor
**Scope:** server.js — authentication, user management endpoints
**Risk Rating:** Critical

## Executive Summary
This API has multiple critical vulnerabilities that would allow an unauthenticated
attacker to read, modify, or delete all data in the database. SQL injection in
the login endpoint enables full database compromise. Hardcoded credentials and
JWT secret in source code compound the risk. This code must not be deployed to
any environment accessible from the internet.

## Findings

### CRITICAL — SQL Injection in Login Endpoint
- **Location:** `server.js:20`
- **Category:** OWASP A03 (Injection)
- **Description:** User-supplied `username` and `password` are interpolated
  directly into a SQL query string without parameterization or sanitization.
- **Impact:** An attacker can bypass authentication entirely, extract all data
  from the database, modify or delete records, and potentially execute OS
  commands via `INTO OUTFILE` or UDF injection depending on MySQL configuration.
- **Evidence:**
  ```javascript
  // Vulnerable — string interpolation in SQL
  const query = `SELECT * FROM users WHERE username='${username}' AND password='${password}'`;
  ```
  Exploit: `username: "admin' OR '1'='1' --"` logs in as any user.
- **Remediation:**
  ```javascript
  // Fixed — parameterized query
  const query = 'SELECT * FROM users WHERE username = ? AND password_hash = ?';
  db.query(query, [username, hashedPassword], (err, results) => { ... });
  ```
- **Effort:** Low

### CRITICAL — SQL Injection in User Lookup
- **Location:** `server.js:30`
- **Category:** OWASP A03 (Injection)
- **Description:** `req.params.id` is interpolated directly into SQL.
  No authentication is required to access this endpoint.
- **Impact:** Unauthenticated attacker can extract any data from the database
  via UNION-based injection.
- **Evidence:**
  ```javascript
  const query = `SELECT * FROM users WHERE id = ${req.params.id}`;
  ```
  Exploit: `GET /users/1 UNION SELECT * FROM users--`
- **Remediation:**
  ```javascript
  const query = 'SELECT id, username, email FROM users WHERE id = ?';
  db.query(query, [parseInt(req.params.id, 10)], (err, results) => { ... });
  ```
- **Effort:** Low

### CRITICAL — Hardcoded Database Credentials
- **Location:** `server.js:8-12`
- **Category:** OWASP A02 (Cryptographic Failures)
- **Description:** Database connection uses hardcoded `root` username with
  password `admin123` in source code.
- **Impact:** Anyone with read access to the repo (or a leaked git history)
  has full database access. Using `root` means no permission boundaries.
- **Remediation:**
  ```javascript
  const db = mysql.createConnection({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME
  });
  ```
- **Effort:** Low

### CRITICAL — Hardcoded JWT Secret
- **Location:** `server.js:15`
- **Category:** OWASP A02 (Cryptographic Failures)
- **Description:** JWT signing secret `supersecretkey123` is hardcoded and
  trivially guessable.
- **Impact:** Attacker can forge JWT tokens for any user, including admin
  roles, granting full API access.
- **Remediation:**
  ```javascript
  const JWT_SECRET = process.env.JWT_SECRET; // min 256-bit random value
  // Generate: node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
  ```
- **Effort:** Low

### HIGH — Plaintext Password Storage
- **Location:** `server.js:20`
- **Category:** OWASP A02 (Cryptographic Failures)
- **Description:** Passwords are compared as plaintext (`password='${password}'`),
  implying they're stored as plaintext in the database.
- **Impact:** Database breach exposes all user passwords. Users who reuse
  passwords (most users) are compromised across other services.
- **Remediation:**
  ```javascript
  const bcrypt = require('bcrypt');
  // On registration:
  const hash = await bcrypt.hash(password, 12);
  // On login:
  const match = await bcrypt.compare(password, user.password_hash);
  ```
- **Effort:** Medium (requires data migration)

### HIGH — Missing Authorization on Delete
- **Location:** `server.js:34-43`
- **Category:** OWASP A01 (Broken Access Control)
- **Description:** Any authenticated user can delete any other user. The
  endpoint verifies the JWT is valid but doesn't check if the authenticated
  user has permission to delete the target user.
- **Impact:** Any logged-in user can delete any other user's account.
- **Remediation:**
  ```javascript
  app.delete('/users/:id', authMiddleware, (req, res) => {
    if (req.user.id !== parseInt(req.params.id) && req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Forbidden' });
    }
    // ... proceed with parameterized delete
  });
  ```
- **Effort:** Low

### MEDIUM — No Authentication on User Lookup
- **Location:** `server.js:29`
- **Category:** OWASP A01 (Broken Access Control)
- **Description:** `GET /users/:id` requires no authentication. Combined
  with `SELECT *`, it exposes all user fields including password hashes.
- **Impact:** Enumeration of all user data by iterating IDs.
- **Remediation:** Add auth middleware and select only non-sensitive fields.
- **Effort:** Low

### LOW — JWT Token Never Expires
- **Location:** `server.js:22`
- **Category:** OWASP A07 (Auth & Identity Failures)
- **Description:** `jwt.sign()` is called without an `expiresIn` option.
  Tokens are valid forever once issued.
- **Impact:** Stolen tokens can never be revoked (unless the JWT secret is
  rotated, which invalidates ALL tokens).
- **Remediation:**
  ```javascript
  const token = jwt.sign({ id: user.id, role: user.role }, JWT_SECRET, {
    expiresIn: '1h'
  });
  ```
- **Effort:** Low

## Positive Observations
- Express JSON body parser is used (no manual body parsing)
- JWT is used for authentication (correct approach, just needs secure secret)
- Error responses don't leak stack traces

## Secrets Found
| Type | Location | Status |
|------|----------|--------|
| DB password (`admin123`) | server.js:10 | Active — rotate immediately |
| JWT secret (`supersecretkey123`) | server.js:15 | Active — rotate immediately |

## Recommendations (Priority Order)
1. **Immediate:** Parameterize ALL SQL queries — fixes 3 critical findings
2. **Immediate:** Move all secrets to environment variables
3. **Immediate:** Hash passwords with bcrypt (migrate existing users)
4. **This Sprint:** Add authorization checks to all endpoints
5. **This Sprint:** Add JWT expiration and refresh token flow
6. **This Quarter:** Add rate limiting, CORS, helmet middleware
7. **Ongoing:** Run `npm audit` in CI, add secret scanning to pre-commit

## Out of Scope
- Infrastructure and network security (not provided)
- Client-side code (not provided)
- Database configuration and access controls
```

## Why This Audit Is Good

1. **Severity is calibrated** — SQL injection is critical (easy to exploit,
   full compromise); missing expiry is low (requires token theft first)
2. **Evidence is exploitable** — shows actual payloads, not just "this could
   be injected"
3. **Remediation is copy-pasteable** — the developer can fix each issue
   immediately
4. **Effort estimates enable prioritization** — "Low" effort + "Critical"
   severity = fix today
5. **Positive observations exist** — even terrible code has something to
   acknowledge
6. **Recommendations are ordered** — clear priority for a developer who
   can only spend 2 hours on this
