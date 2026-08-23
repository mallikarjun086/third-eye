# SECURITY AUDIT & MIGRATION PLAN

---

## 1. Current Authentication Behavior

* **Database File**: `login.sqlite`
* **Table Schema**: `CREATE TABLE login_data (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT)`
* **Authentication Method**: Plaintext string comparison via `Login_screenController.java` (`SELECT * FROM login_data WHERE email = ? AND password = ?`).

---

## 2. Risk Assessment

* **Severity**: MEDIUM
* **Risk**: If the `login.sqlite` file is accessed by an unauthorized local user, user passwords can be read directly in plain text.

---

## 3. Safe Migration Plan (Controlled Phase-In)

```text
[ Existing User Table ] ──> [ Add Column: password_hash ] ──> [ Hash Passwords on Next Login ] ──> [ Deprecate Plaintext Column ]
```

1. **Step 1**: Add `password_hash` column to `login_data` table.
2. **Step 2**: On user sign-in or account creation, compute `bcrypt.hashpw(password, bcrypt.gensalt())`.
3. **Step 3**: Verify credentials using `bcrypt.checkpw(password, stored_hash)` while retaining fallback for unmigrated legacy users.
4. **Step 4**: Nullify/drop the legacy `password` column once all active user records have migrated.
