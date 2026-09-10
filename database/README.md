# Database initialization

The application expects MySQL and the `news_app` database configured in `.env.example`.

Run the scripts in this order from the repository root:

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
```

On Windows PowerShell, run the same commands through `cmd` because PowerShell does not support this input-redirection syntax:

```powershell
cmd /c "mysql -u root -p < database\schema.sql"
cmd /c "mysql -u root -p < database\seed.sql"
```

`schema.sql` creates the database and all eight tables used by the current code. `seed.sql` is optional and adds eight categories plus four clearly marked demo articles. Both scripts can be run repeatedly. The seed script intentionally creates no default user or credential.

If the database was initialized before the role column was added, run the one-time migration:

```bash
mysql -u root -p < database/migrations/001_add_user_role.sql
```

If the bundled Chinese demo content was imported with mojibake, run the idempotent repair migration:

```bash
mysql -u root -p < database/migrations/002_repair_seed_utf8.sql
```

New accounts receive the `user` role. Promote an account only through a trusted database administration session when it needs access to user-management and news-writing endpoints.

```sql
UPDATE `user` SET role = 'admin' WHERE username = 'replace-with-your-username';
```

Accounts created by older versions with plaintext passwords are intentionally rejected after this security update. Recreate development accounts, or use a controlled password-reset process that writes a bcrypt hash before deploying the change to an existing environment.
