"""
LocalClaw Gateway Orchestrator
===============================
Runs both the Email and GitHub gateways simultaneously.

  python gateway.py           ← start both
  python email_gateway.py     ← start email only  (port 5000)
  python github_gateway.py    ← start GitHub only (port 5001)
"""

import threading
import email_gateway
import github_gateway


def main():
    print("\n" + "═" * 60)
    print("  🦞  LocalClaw — Starting all gateways")
    print("═" * 60)
    print("     Email  → http://127.0.0.1:5000")
    print("     GitHub → http://127.0.0.1:5001")
    print()

    t_email  = threading.Thread(target=email_gateway.run,  daemon=True, name="email-gateway")
    t_github = threading.Thread(target=github_gateway.run, daemon=True, name="github-gateway")

    t_email.start()
    t_github.start()

    t_email.join()
    t_github.join()


if __name__ == "__main__":
    main()
