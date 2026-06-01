# Project task ticketing system

This project is realization of my engineering thesis.</br> 
A browser application that allows to submit and manage tickets to a different 
extent depending on the role assigned in the system, the implementation 
was designed to work on a product that requires long-term operational improvement.
Implementation allows you to centralize communication with the client in the tasks 
and in a convenient way to filter the tickets that have entered the system. 
From the administration panel level it is possible to manage groups, users, 
start panels, types of tasks, processes in a given type of ticket, 
priorities and many other values that can be used to describe a task.</br>
In addition, it is possible to divide tickets by categorizing them into tenants, 
thanks to which it is possible to handle several projects from the level of the same 
application instance. The solution was prepared in Python using the Django framework.

## Docker

The app is containerized via the root [`Dockerfile`](Dockerfile) (Python 3.12 slim, gunicorn on port `8000`). Configuration is read entirely from environment variables (see [Environments](#environments)).

```bash
docker build -t service-desk --build-arg APP_VERSION=dev .
docker run --env-file .env.prod -p 8000:8000 service-desk
```

### Releasing an image

Pushing a `v*` tag triggers the [`Build and Push Docker Image`](.github/workflows/docker-publish.yml) GitHub Action, which builds for `linux/amd64` and `linux/arm64` and pushes to `registry.siedlaczek.com.pl/service-desk`.

```bash
git tag v1.2.3
git push origin v1.2.3
```

The image is tagged with the short commit SHA, `latest`, and the semver tags (`1.2.3` and `1.2`). The runner needs the `REGISTRY_USERNAME` and `REGISTRY_PASSWORD` repository secrets.

#### Re-running a build for an existing tag

The workflow checks out the commit the tag points at, so to rebuild after fixing something, move the tag to the new commit and force-push it (a force-push to an existing tag re-fires the `push: tags` event):

```bash
git tag -f v1.2.3          # move the tag to the current local commit
git push -f origin v1.2.3  # overwrite the remote tag and re-trigger the workflow
```

This overwrites the existing image under the same tag (`v1.2.3`, `1.2`, `latest`) in the registry.

## Environments
| Key                     | Type      | Required           | Default          | Description                                                                                    |
| ----------------------- | --------- | ------------------ | ---------------- | ---------------------------------------------------------------------------------------------- |
| `DJANGO_SECRET_KEY`     | `string`  | :x:                | auto-generated   | Secret key for Django. In production **must** be manually set — never rely on a generated one. |
| `DJANGO_SITE_NAME`      | `string`  | :x:                | `ServiceDeskApp` | Site name displayed across the UI.                                                             |
| `DJANGO_DEBUG`          | `boolean` | :x:                | `False`          | Enable Django debug mode. Keep `false` in production.                                          |
| `ALLOWED_HOSTS`         | `string`  | :x:                | `*`              | Comma-separated list of host/domain names the app may serve (e.g., `example.com,www.example.com`). |
| `CSRF_TRUSTED_ORIGINS`  | `string`  | :x:                | `http://localhost` | Comma-separated list of trusted origins for CSRF protection (e.g., `https://example.com`). Must be set in production. |
| `STATIC_ROOT`           | `string`  | :x:                | `staticfiles`    | Filesystem path where `collectstatic` gathers static files.                                    |
| `MEDIA_ROOT`            | `string`  | :x:                | `media`          | Filesystem path for uploaded media files.                                                      |
| `LANGUAGE_CODE`         | `string`  | :x:                | `en-us`          | Default language code used when the browser locale cannot be detected.                         |
| `TIME_ZONE`             | `string`  | :x:                | `Europe/Zagreb`  | Time zone the application runs in.                                                             |
| `USE_X_FORWARDED_HOST`  | `boolean` | :x:                | `True`           | Trust the `X-Forwarded-Host` header. Required when running behind a reverse proxy.             |
| `SECURE_SSL_REDIRECT`   | `boolean` | :x:                | `False`          | Redirect all HTTP requests to HTTPS.                                                           |
| `SESSION_COOKIE_SECURE` | `boolean` | :x:                | `True`           | Send the session cookie only over HTTPS.                                                       |
| `CSRF_COOKIE_SECURE`    | `boolean` | :x:                | `True`           | Send the CSRF cookie only over HTTPS.                                                          |
| `LOG_LEVEL`             | `string`  | :x:                | `INFO`           | Global logging level. Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.                |
| `CACHE_ENABLED`         | `boolean` | :x:                | `False`          | Enable Redis-backed page caching. When `true`, the `REDIS_*` settings are used; otherwise an in-memory cache is used. |
| `CACHE_TTL`             | `number`  | :x:                | `600`            | Page cache lifetime in seconds (used only when `CACHE_ENABLED` is `true`).                     |
| `DB_NAME`               | `string`  | :heavy_check_mark: | -                | PostgreSQL database name.                                                                      |
| `DB_USER`               | `string`  | :heavy_check_mark: | -                | Username for PostgreSQL authentication.                                                        |
| `DB_PASS`               | `string`  | :heavy_check_mark: | -                | Password for PostgreSQL authentication.                                                        |
| `DB_HOST`               | `string`  | :x:                | `127.0.0.1`      | Hostname or IP of the PostgreSQL server.                                                       |
| `DB_PORT`               | `number`  | :x:                | `5432`           | Port where PostgreSQL listens.                                                                 |
| `DB_CONN_MAX_AGE`       | `number`  | :x:                | `300`            | Maximum lifetime (in seconds) of a database connection.                                        |
| `SMTP_HOST`             | `string`  | :x:                | -                | SMTP server hostname. When set, the SMTP email backend is used; otherwise email is printed to the console. |
| `SMTP_USER`             | `string`  | :x:                | -                | SMTP username.                                                                                 |
| `SMTP_PASS`             | `string`  | :x:                | -                | SMTP user password.                                                                            |
| `SMTP_PORT`             | `number`  | :x:                | `465`            | SMTP port. Common values: `465` (SSL) or `587` (STARTTLS).                                     |
| `SMTP_USE_SSL`          | `boolean` | :x:                | `True`           | Use implicit SSL (`true`, port `465`) or STARTTLS (`false`, port `587`).                       |
| `SMTP_FROM`             | `string`  | :x:                | `SMTP_USER`      | Default `From` address for outgoing email.                                                     |
| `REDIS_USER`            | `string`  | :x:                | -                | Redis ACL username (Redis 6+). Leave unset to authenticate as the `default` user.              |
| `REDIS_PASS`            | `string`  | :x:                | -                | Redis password if authentication is enabled.                                                   |
| `REDIS_HOST`            | `string`  | :x:                | `127.0.0.1`      | Redis server hostname.                                                                         |
| `REDIS_PORT`            | `number`  | :x:                | `6379`           | Redis server port.                                                                             |
| `REDIS_DB`              | `number`  | :x:                | `0`              | Redis logical database index.                                                                  |
| `REDIS_SSL`             | `boolean` | :x:                | `False`          | Whether Redis should be accessed using SSL.                                                    |

## License

This application is licensed under terms of the BSD 3-clause license. See the LICENSE file for full licensing terms.

Note that this application is distributed with 3rd party products which have their own licenses.

## Author

- [@Karol Siedlaczek](https://github.com/karol-siedlaczek)
