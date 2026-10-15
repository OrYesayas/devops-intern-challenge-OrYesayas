# Generative AI Disclosure

Using AI tools for this challenge is allowed. Be honest here — an accurate
"I used AI heavily" is worth more to us than an inaccurate "I did not".

**Did you use AI tools?** (yes / no): yes

**Which ones?** (e.g. ChatGPT, Claude, Copilot, Cursor): Claude (Anthropic), in a chat. I brought my experience from my NOC job, and used Claude to explain the tools I had not used before and to challenge my ideas.

> If you answered **no**, write "N/A" in sections 1 and 2 and skip to
> section 3. That is a perfectly good answer.

---

## 1. Key prompts

List the main prompts you used. Paraphrasing is fine.

1. `Here are long build and test logs. Help me cut through them to the lines that matter.`
2. `Here are nginx.conf and docker-compose.yml. Why does /api/info return 502 while /nginx-health passes?`
3. `The tests fail only after the routing fix. How can I check if the backend needs time to start?` (I ran a curl loop and pasted the result: 3 seconds with no connection.)
4. `Why add a healthcheck only to the backend? What about the proxy?` (I added it to both.)
5. `Is chown on /run the right fix? Can I change the default instead?` (I tested a narrower chown, it failed on /run/nginx.pid, and I decided to keep the working version.)

---

## 2. Where the AI got it wrong

Describe **one concrete case** where the AI's answer was wrong, outdated, or
sub-optimal. Cover: what it suggested, how you noticed it was wrong, and what
you did instead. 3–5 sentences.

> While explaining CI, the AI said that when a step fails, the steps after it are skipped. I pointed out that at my job a Jenkins pipeline can fail while the steps before the failure have already happened and are not undone. The AI agreed and corrected the explanation: skipping only affects the steps after the failure.

---

## 3. Anything in your submission you could not fully explain?

We would rather know. Write "nothing" if that is the case.

> Mostly nothing. One thing I did not investigate: the backend exits with code 137 at the end of every run. I understand it means it was killed, but I did not find out why it does not stop by itself. It is also written in `RCA.md`.
