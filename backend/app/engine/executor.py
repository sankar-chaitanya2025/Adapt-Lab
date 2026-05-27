"""
Code Execution Engine — Judge0 CE Integration.

Provides sandboxed GCC compilation and execution via a self-hosted Judge0 CE instance.
"""

import logging
from typing import Dict, Any, List, Optional

import httpx

logger = logging.getLogger(__name__)

# Judge0 language ID for C (GCC)
C_LANGUAGE_ID = 50


class ExecutorError(Exception):
    """Raised when the code execution service encounters an error."""
    pass


class CodeExecutor:
    """
    Executes C code in a sandboxed Judge0 CE environment.

    Submits source code with stdin/expected_output to Judge0,
    waits for results, and returns structured execution output.
    """

    def __init__(self, judge0_url: str = "http://judge0:2358"):
        """
        Args:
            judge0_url: Base URL of the Judge0 CE instance.
        """
        self.base_url = judge0_url.rstrip("/")
        self.submit_url = f"{self.base_url}/submissions"

    async def execute(
        self,
        source_code: str,
        stdin: str = "",
        expected_output: str = "",
    ) -> Dict[str, Any]:
        """
        Execute C source code with given stdin and compare against expected output.

        Args:
            source_code: Complete C source code to compile and run.
            stdin: Standard input to feed to the program.
            expected_output: Expected stdout for comparison.

        Returns:
            Dict with keys: status, stdout, stderr, compile_output, time, memory.
        """
        payload = {
            "source_code": source_code,
            "language_id": C_LANGUAGE_ID,
            "stdin": stdin,
            "expected_output": expected_output,
            "cpu_time_limit": 5,
            "memory_limit": 128000,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Submit with ?wait=true to block until result is ready
                response = await client.post(
                    f"{self.submit_url}?base64_encoded=false&wait=true",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()

        except httpx.ConnectError:
            raise ExecutorError(
                "Code execution service is temporarily unavailable. "
                "Please try again in a moment."
            )
        except httpx.TimeoutException:
            raise ExecutorError(
                "Code execution timed out. Please try again."
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Judge0 HTTP error: {e.response.status_code} — {e.response.text}")
            raise ExecutorError(
                "Code execution service returned an error. Please try again."
            )

        # Map Judge0 status to simplified status string
        status_id = result.get("status", {}).get("id", 0)
        status_map = {
            3: "accepted",          # Accepted
            4: "wrong_answer",      # Wrong Answer
            5: "time_limit_exceeded",
            6: "compilation_error",
            7: "runtime_error",     # Runtime Error (SIGSEGV)
            8: "runtime_error",     # Runtime Error (SIGXFSZ)
            9: "runtime_error",     # Runtime Error (SIGFPE)
            10: "runtime_error",    # Runtime Error (SIGABRT)
            11: "runtime_error",    # Runtime Error (NZEC)
            12: "runtime_error",    # Runtime Error (Other)
            13: "internal_error",   # Internal Error
            14: "compilation_error",
        }
        status_str = status_map.get(status_id, "unknown")

        return {
            "status": status_str,
            "stdout": result.get("stdout"),
            "stderr": result.get("stderr"),
            "compile_output": result.get("compile_output"),
            "time": result.get("time"),
            "memory": result.get("memory"),
        }

    async def run_all_tests(
        self,
        source_code: str,
        test_cases: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Run source code against all test cases and aggregate results.

        Args:
            source_code: Complete C source code.
            test_cases: List of dicts with keys: input, expected_output, is_hidden.

        Returns:
            Dict with keys: passed, total, all_passed, results, first_error.
        """
        results = []
        passed = 0
        first_error: Optional[str] = None

        for i, tc in enumerate(test_cases):
            try:
                result = await self.execute(
                    source_code=source_code,
                    stdin=tc.get("input", ""),
                    expected_output=tc.get("expected_output", ""),
                )
            except ExecutorError as e:
                # If Judge0 is down, report it for all remaining tests
                result = {
                    "status": "internal_error",
                    "stdout": None,
                    "stderr": str(e),
                    "compile_output": None,
                    "time": None,
                    "memory": None,
                }

            is_passed = result["status"] == "accepted"
            if is_passed:
                passed += 1

            # Capture first error details
            if not is_passed and first_error is None:
                if result.get("compile_output"):
                    first_error = result["compile_output"]
                elif result.get("stderr"):
                    first_error = result["stderr"]
                elif result.get("stdout"):
                    first_error = (
                        f"Expected: {tc.get('expected_output', '')}\n"
                        f"Got: {result['stdout']}"
                    )
                else:
                    first_error = f"Test failed with status: {result['status']}"

            results.append({
                "test_index": i,
                "input": tc.get("input", ""),
                "expected": tc.get("expected_output", ""),
                "actual": result.get("stdout") or "",
                "status": result["status"],
                "is_hidden": tc.get("is_hidden", False),
            })

        return {
            "passed": passed,
            "total": len(test_cases),
            "all_passed": passed == len(test_cases),
            "results": results,
            "first_error": first_error,
        }
