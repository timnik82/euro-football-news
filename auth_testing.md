# Auth Testing Playbook

## MongoDB verification
```bash
mongosh
use test_database
db.users.find({role: "admin"}).pretty()
db.users.findOne({role: "admin"}, {password_hash: 1})
```

Verify that the admin password hash starts with `$2b$` and that `users.email` has a unique index.

## API verification
```bash
curl -c cookies.txt -X POST "$REACT_APP_BACKEND_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

curl -b cookies.txt "$REACT_APP_BACKEND_URL/api/auth/me"
```

Login should return the admin user object and set `access_token` + `refresh_token` cookies. `/auth/me` should return the same user using those cookies.