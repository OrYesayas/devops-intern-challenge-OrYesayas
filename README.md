# F5 DevOps Intern Challenge

You inherited a three-container service from a teammate who left. It doesn't
build, the containers can't talk to each other, the tests fail, and CI is
red. Fix it.

**Time budget**: ~4 hours. Submit what you have when it runs out.
**You need**: Git, Docker Engine, Docker Compose v2, a GitHub account.

```
[ test-runner ] --HTTP--> [ nginx proxy ] --HTTP--> [ backend API ]
                            (proxy:80)              (backend:8080)
```

- `backend` — Python HTTP API. Serves `/health` and `/api/info`.
- `proxy` — Nginx reverse proxy. Serves `/nginx-health`, forwards the rest.
- `test-runner` — Integration tests. Exits non-zero on failure.

## Getting started

Click **Use this template → Create a new repository** to get your own copy.
Private is fine — just add your reviewer as a collaborator when you submit.

Clone your new repository locally.

```bash
./scripts/run-tests.sh            # the command that must pass
docker compose logs <service>     # your main diagnostic tool
```

`run-tests.sh` builds, tests, tears down, and exits with the test suite's
exit code.

## Ground rules

- Don't weaken the tests to make them pass.
- Treat `backend/app.py` as a third-party service you cannot modify.

## Tasks

**1. The proxy image doesn't build.** Read the whole error, not just the last
line. The `apt-get` command isn't missing a package.

**2. The proxy can't reach the backend.** Once it builds, requests through
the proxy fail. Fix the routing.

**3. The tests still fail after task 2**, for a different reason. Find it,
and make the suite pass on every run.

**4. CI is red.** `.github/workflows/ci.yml` fails. Fix it so it stays fixed
for whoever clones the repo next.

## Deliverables

- `./scripts/run-tests.sh` exits `0`, and GitHub Actions is green.
- `RCA.md` — fill in the template. Symptom, the command that found it, root
  cause, fix. Bullet points. We care that you can explain *why*.
- `AI_PROMPTS.md` — AI tools are allowed and encouraged. Submitting code you
  can't explain is not. If you used AI, list your main prompts and describe
  one case where it was wrong and how you caught it. If you didn't, say so.

## Bonus questions (optional)

- Reduce the size of the proxy image by using a minimal base image and
  removing unnecessary packages. Write down what you changed and the image
  size before and after.
- Running apps as root in production is dangerous. Modify the proxy to run as
  a non-root user and document the changes.
- Document any additional security or performance improvements you make to
  the proxy image.

## Submitting

Work on a branch and open a Pull Request into `main` **in your own repo** —
not against the original repository. Make sure CI is green, then send us the
repo and PR link. If your repo is private, add your reviewer as a
collaborator so they can actually open it.

Good luck.
