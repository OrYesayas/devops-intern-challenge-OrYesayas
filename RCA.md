# Root Cause Analysis

Fill this in as you go. Bullet points are fine — be specific, not long.

---

## Defect 1: Proxy image fails to build

### Symptom / error output

- The proxy build failed at the `apt-get install` step with `exit code: 100`.

### How I diagnosed it

- The last line only says "exit code 100", so I saved the whole output with `./scripts/run-tests.sh 2>&1 | tee first-run.log` and read it from the top.
- About 50 lines higher it says `dpkg: error processing package nginx-common ... end of file on stdin at conffile prompt`.
- I ran `cat proxy/Dockerfile` and saw that `COPY nginx.conf` runs before `apt-get install nginx`.

### Root cause

- My `nginx.conf` was copied into the image first. Then the nginx install wanted to write its own file in the same place.
- The installer asked "keep yours or replace it?". A Docker build has nobody to answer, so the install failed.

### Fix

- I moved `COPY nginx.conf` to after the `apt-get install` line. The install now finds an empty place, and my file replaces the default afterwards.
- The next build passed.

---

## Defect 2: Proxy cannot reach the backend

### Symptom / error output

- `/nginx-health` passed, but `/api/info` failed with `502 Bad Gateway`.
- The proxy log said: `connect() failed (111: Connection refused) while connecting to upstream ... upstream: "http://127.0.0.1:8080/api/info"`.

### How I diagnosed it

- `/nginx-health` is answered by nginx itself, so it passing meant the proxy was alive and only the forwarding was broken.
- The log showed the upstream address `127.0.0.1`. I ran `cat proxy/nginx.conf` and found `server 127.0.0.1:8080;`.
- I ran `cat docker-compose.yml` and saw that the backend service is named `backend` and uses port 8080.

### Root cause

- `127.0.0.1` means "this same container". The proxy was looking for the backend inside itself, and nothing is listening on 8080 there.
- Each container has its own `localhost`. Containers must use the service name to reach each other.

### Fix

- I changed `server 127.0.0.1:8080;` to `server backend:8080;` in `proxy/nginx.conf`.
- In the next run the log showed the upstream as `172.18.0.2:8080`, so the name `backend` was resolved to the container's address.

---

## Defect 3: Tests still fail after fixing defect 2

### Symptom / error output

- `/api/info` still failed with `502 Bad Gateway`, but the proxy log now said `connect() failed (111: Connection refused) ... upstream: "http://172.18.0.2:8080/api/info"`.
- The address was now the backend container's, so the routing from defect 2 worked. The backend simply did not answer yet.

### How I diagnosed it

- I started only the backend (`docker compose up -d backend`) and sent a request to `/health` every second (`curl` in a loop). The first 3 seconds returned `000` (no connection), then `200`.
- `docker compose logs backend` showed `Backend listening on port 8080...` only after it finished loading its config keys.
- In the failed test runs, the backend log was cut off in the middle of loading, so the tests had started before the backend was ready.

### Root cause

- A race condition. `depends_on` only waits for the container to start, not for the app inside to be ready. The backend needs about 3 seconds to start listening, and the tests ran before that.
- It can fail depending on timing.

### Fix, and why I chose it over the alternatives

- I added a `healthcheck` to the backend (calls `/health` every 2 seconds) and to the proxy (calls `/nginx-health`). I changed `depends_on` to `condition: service_healthy`, so each service starts only after the one before it is ready.
- I chose this over `sleep 5` in the test runner, because a fixed sleep is a guess: too short and it still fails sometimes, too long and every run is slower. A healthcheck waits exactly as long as needed.
- I added the healthcheck to the proxy too, even though only the backend was proven slow, because the test runner can hit the same race there on a slower machine.
- After the fix, I ran the test script 20 times in a row, and all 20 exited with code 0.

---

## Defect 4: CI pipeline fails

### Symptom / error output

- The first CI run on `main` failed after 4 seconds at the step `Execute test suite`: `./scripts/run-tests.sh: Permission denied`, `Process completed with exit code 126`.
- The same error appeared on my computer when I first ran the script.

### How I diagnosed it

- I opened the log of the failed CI run (Actions, `integration-tests`, `Execute test suite`) and saw the `Permission denied` line.
- Locally I ran `ls -l scripts/` and saw `-rw-r--r--` (no `x`, so not executable). Then `git ls-files --stage scripts/` showed mode `100644`, so Git itself saved the file as not executable.

### Root cause

- `run-tests.sh` was stored in Git without the executable permission. The CI step runs `./scripts/run-tests.sh` directly, so Linux refused to run it. Anyone who clones the repo gets the same problem.

### Fix

- I ran `chmod +x scripts/run-tests.sh`, then `git add`, and committed. `git ls-tree HEAD scripts/` now shows `100755`.
- I did not change `ci.yml`. After the push, the CI run passed in 59 seconds. Anyone who clones the branch gets an executable script.

---

## Bonus questions

Optional. Answer only the ones you got to — number them, skip the rest.

1. Reduce the size of the proxy image
   - Before: 452MB. After: 102MB (about 77% smaller). I measured it with `docker images | grep proxy`.
   - I changed the base image from `ubuntu:24.04` to `nginx:alpine`, a small Linux that already has nginx and curl.
   - I removed the `apt-get install` line, so `htop`, `vim` and `git` are gone. A proxy does not need them.
   - I removed the `CMD` line, because the nginx image already starts nginx. The tests still pass.

2. Run the proxy as a non-root user
   - I added `USER nginx` (this user already exists in the image). `docker compose exec proxy whoami` prints `nginx`.
   - At first it failed: `mkdir() "/var/cache/nginx/client_temp" failed (13: Permission denied)`. Those folders belong to root.
   - Fix: `RUN chown -R nginx:nginx /var/cache/nginx /run`, placed before `USER nginx`.
   - I also tried giving ownership only to `/var/cache/nginx`. It failed with `open() "/run/nginx.pid" failed (13: Permission denied)`, so both folders are needed.
   - Port 80 worked for the non-root user, so I did not change the port.

---

## Anything you would do differently with more time

- The real error in defect 1 was about 50 lines above the end of the build log, hidden between many `debconf` warnings. I would try to reduce that noise (for example with `DEBIAN_FRONTEND=noninteractive`) so the cause is easier to find. I did not test this.
- The backend is killed (exit code 137) at the end of every run instead of stopping by itself. I did not investigate why. I could not change `backend/app.py`, so I would raise it with its owner.
