import json, os, subprocess, tempfile, threading, unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
import git_ghost


class Fake(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers["Content-Length"]); body = json.loads(self.rfile.read(n))
        Fake.seen = body
        self.send_response(200); self.end_headers()
        for w in ["I ", "remember", "..."]:
            self.wfile.write((json.dumps({"message": {"content": w}, "done": False}) + "\n").encode())
        self.wfile.write((json.dumps({"message": {"content": ""}, "done": True}) + "\n").encode())

    def log_message(self, *a): pass


class T(unittest.TestCase):
    def test_flow(self):
        d = tempfile.mkdtemp()
        env = dict(os.environ, GIT_AUTHOR_NAME="a", GIT_AUTHOR_EMAIL="a@a",
                   GIT_COMMITTER_NAME="a", GIT_COMMITTER_EMAIL="a@a")
        subprocess.run(["git", "init", "-q", d], check=True)
        for i in range(5):
            subprocess.run(["git", "-C", d, "commit", "-q", "--allow-empty", "-m", f"c{i}"],
                           check=True, env=env)
        old, new, total = git_ghost.collect(d, 2, 2)
        self.assertEqual(total, 5)
        self.assertTrue(old[0].endswith("c0"))
        self.assertTrue(new[0].endswith("c4"))
        srv = HTTPServer(("127.0.0.1", 0), Fake)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        out = "".join(git_ghost.summon(
            "gemma3:4b", git_ghost.build_prompt(old, new, total),
            f"http://127.0.0.1:{srv.server_port}/api/chat"))
        self.assertEqual(out, "I remember...")
        self.assertEqual(Fake.seen["model"], "gemma3:4b")
        srv.shutdown()


unittest.main()
