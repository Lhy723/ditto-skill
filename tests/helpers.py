from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess


CommitFiles = dict[str, str | None]


@dataclass
class TempRepo:
    path: Path

    def run_git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self.path,
            check=True,
            text=True,
            capture_output=True,
        )
        return result.stdout.strip()


def make_git_repo(path: Path, commits: list[tuple[str, CommitFiles]]) -> TempRepo:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.name", "Ditto Skill Tests"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "ditto-tests@example.com"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )

    for message, files in commits:
        for relpath, content in files.items():
            file_path = path / relpath
            if content is None:
                if file_path.exists():
                    file_path.unlink()
                continue
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
        subprocess.run(["git", "add", "-A"], cwd=path, check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=path,
            check=True,
            capture_output=True,
            text=True,
        )

    return TempRepo(path=path)


def build_web_saas_repo(path: Path) -> TempRepo:
    return make_git_repo(
        path,
        [
            (
                "feat: bootstrap web app shell",
                {
                    "package.json": (
                        '{\n'
                        '  "name": "web-saas",\n'
                        '  "dependencies": {\n'
                        '    "next": "14.2.0",\n'
                        '    "react": "18.3.0"\n'
                        "  }\n"
                        "}\n"
                    ),
                    "app/page.tsx": "export default function Page() { return <main>home</main> }\n",
                    "app/layout.tsx": "export default function RootLayout({ children }) { return children }\n",
                },
            ),
            (
                "feat: add auth flow",
                {
                    "package.json": (
                        '{\n'
                        '  "name": "web-saas",\n'
                        '  "dependencies": {\n'
                        '    "next": "14.2.0",\n'
                        '    "react": "18.3.0",\n'
                        '    "next-auth": "5.0.0"\n'
                        "  }\n"
                        "}\n"
                    ),
                    "app/login/page.tsx": "export default function Login() { return <main>login</main> }\n",
                    "lib/auth.ts": "export function requireSession() { return true }\n",
                    "middleware.ts": "export default function middleware() { return Response.next() }\n",
                },
            ),
            (
                "feat: add billing workflow",
                {
                    "package.json": (
                        '{\n'
                        '  "name": "web-saas",\n'
                        '  "dependencies": {\n'
                        '    "next": "14.2.0",\n'
                        '    "react": "18.3.0",\n'
                        '    "next-auth": "5.0.0",\n'
                        '    "stripe": "17.1.0"\n'
                        "  }\n"
                        "}\n"
                    ),
                    "app/billing/page.tsx": "export default function Billing() { return <main>billing</main> }\n",
                    "lib/billing.ts": "export function createCheckoutSession() { return 'ok' }\n",
                },
            ),
            (
                "refactor: split services from routes",
                {
                    "lib/auth.ts": None,
                    "services/auth.ts": "export function requireSession() { return true }\n",
                    "services/billing.ts": "export function createCheckoutSession() { return 'ok' }\n",
                    "app/api/billing/route.ts": "export async function POST() { return Response.json({ ok: true }) }\n",
                },
            ),
            (
                "feat: add ci and regression coverage",
                {
                    ".github/workflows/ci.yml": "name: ci\non: [push]\n",
                    "tests/auth_redirect.test.ts": "it('keeps auth redirect stable', () => expect(true).toBe(true))\n",
                    "eslint.config.js": "export default []\n",
                    "tsconfig.json": '{ "compilerOptions": { "strict": true } }\n',
                },
            ),
            (
                "fix: prevent auth redirect loop",
                {
                    "middleware.ts": (
                        "export default function middleware(req) {\n"
                        "  if (req.nextUrl.pathname === '/login') return Response.next()\n"
                        "  return Response.next()\n"
                        "}\n"
                    ),
                    "tests/auth_redirect.test.ts": (
                        "it('avoids redirect loop', () => expect('/login').toBe('/login'))\n"
                    ),
                },
            ),
        ],
    )


def build_ai_agent_repo(path: Path) -> TempRepo:
    return make_git_repo(
        path,
        [
            (
                "feat: bootstrap agent runner",
                {
                    "pyproject.toml": (
                        "[project]\n"
                        "name = 'agent-repo'\n"
                        "version = '0.1.0'\n"
                        "dependencies = []\n"
                    ),
                    "src/runner.py": "def run_agent(prompt: str) -> str:\n    return prompt\n",
                },
            ),
            (
                "feat: add tool adapter layer",
                {
                    "pyproject.toml": (
                        "[project]\n"
                        "name = 'agent-repo'\n"
                        "version = '0.1.0'\n"
                        "dependencies = ['httpx>=0.27']\n"
                    ),
                    "src/tools.py": "TOOLS = {'search': lambda q: q}\n",
                    "src/runner.py": "from src.tools import TOOLS\n\ndef run_agent(prompt: str) -> str:\n    return TOOLS['search'](prompt)\n",
                },
            ),
            (
                "feat: add prompt orchestration workflow",
                {
                    "src/prompts.py": "SYSTEM_PROMPT = 'You are a workflow agent.'\n",
                    "src/workflow.py": "def plan_then_act(prompt: str) -> list[str]:\n    return ['plan', prompt]\n",
                    "src/runner.py": (
                        "from src.prompts import SYSTEM_PROMPT\n"
                        "from src.workflow import plan_then_act\n\n"
                        "def run_agent(prompt: str) -> list[str]:\n"
                        "    return [SYSTEM_PROMPT, *plan_then_act(prompt)]\n"
                    ),
                },
            ),
            (
                "refactor: separate orchestration from tool execution",
                {
                    "src/orchestrator.py": "def orchestrate(prompt: str) -> list[str]:\n    return ['plan', prompt]\n",
                    "src/workflow.py": None,
                    "src/runner.py": (
                        "from src.orchestrator import orchestrate\n"
                        "from src.tools import TOOLS\n\n"
                        "def run_agent(prompt: str) -> list[str]:\n"
                        "    return orchestrate(TOOLS['search'](prompt))\n"
                    ),
                },
            ),
            (
                "feat: add eval suite and typed interfaces",
                {
                    "tests/test_eval.py": "def test_eval_runs():\n    assert True\n",
                    "mypy.ini": "[mypy]\nstrict = True\n",
                    ".github/workflows/eval.yml": "name: eval\non: [push]\n",
                    "src/eval.py": "def score_run(output: list[str]) -> int:\n    return len(output)\n",
                },
            ),
            (
                "fix: avoid memory state leak across runs",
                {
                    "src/memory.py": "def reset_state() -> dict[str, str]:\n    return {}\n",
                    "src/runner.py": (
                        "from src.memory import reset_state\n"
                        "from src.orchestrator import orchestrate\n"
                        "from src.tools import TOOLS\n\n"
                        "def run_agent(prompt: str) -> list[str]:\n"
                        "    state = reset_state()\n"
                        "    _ = state\n"
                        "    return orchestrate(TOOLS['search'](prompt))\n"
                    ),
                    "tests/test_memory.py": "def test_memory_resets():\n    assert {} == {}\n",
                },
            ),
        ],
    )
