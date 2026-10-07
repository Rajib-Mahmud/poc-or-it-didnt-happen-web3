from __future__ import annotations

from .providers import LLMProvider

# Roles (the "committee", not a fallback chain): each plays a distinct part, then a judge decides.
RESEARCHER = "You are the RESEARCHER. Generate concrete, exploitable vulnerability hypotheses. Be thorough."
SKEPTIC = ("You are the SKEPTIC. For each candidate below, try hard to DISPROVE it — intended behavior, "
           "access control, reachability, existing mitigation, economic infeasibility, duplication. "
           "Keep only the ones that survive.")
JUDGE = ("You are the JUDGE. Given the research and the skeptic's rebuttals, decide the final findings. "
         "Prefer precision over recall. Output the final FINDINGS_JSON.")


class Committee:
    """Runs researcher -> skeptic -> judge. Providers may be the same model playing each
    role, or different models (true multi-model) when several are configured."""

    def __init__(self, researcher: LLMProvider, skeptic: LLMProvider | None = None, judge: LLMProvider | None = None):
        self.researcher = researcher
        self.skeptic = skeptic or researcher
        self.judge = judge or researcher

    def audit(self, system: str, user: str, max_tokens: int = 8000) -> str:
        research = self.researcher.complete(system + "\n\n" + RESEARCHER, user, max_tokens)
        skeptic_in = user + "\n\n## CANDIDATES FROM RESEARCHER\n" + research
        rebuttal = self.skeptic.complete(system + "\n\n" + SKEPTIC, skeptic_in, max_tokens)
        judge_in = (user + "\n\n## RESEARCH\n" + research + "\n\n## SKEPTIC REVIEW\n" + rebuttal)
        return self.judge.complete(system + "\n\n" + JUDGE, judge_in, max_tokens)
