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
