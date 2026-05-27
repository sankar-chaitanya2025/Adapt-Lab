"""
Capability Matrix Service.

Utilities for initializing, querying, and summarizing
the student's capability matrix.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


def initialize_capability_matrix(knowledge_graph) -> Dict[str, Any]:
    """
    Create a fresh capability matrix with all concepts from the knowledge graph.

    Each concept starts with zero mastery, zero attempts, and "not_started" status.

    Args:
        knowledge_graph: The loaded KnowledgeGraph instance.

    Returns:
        Dict mapping concept_id to capability stats.
    """
    matrix = {}
    for concept_id in knowledge_graph.get_all_concept_ids():
        matrix[concept_id] = {
            "mastery_level": 0,
            "attempts": 0,
            "successes": 0,
            "failures": 0,
            "current_difficulty": 1,
            "last_attempted": None,
            "status": "not_started",
        }
    return matrix


def get_recommended_concepts(
    capability_matrix: Dict[str, Any],
    knowledge_graph,
) -> List[str]:
    """
    Return concept IDs the student is ready to attempt.

    A concept is ready if ALL its prerequisites have mastery_level >= 3.

    Args:
        capability_matrix: The student's full capability matrix.
        knowledge_graph: The loaded KnowledgeGraph instance.

    Returns:
        List of concept_id strings the student can work on.
    """
    recommended = []

    for concept_id in knowledge_graph.get_all_concept_ids():
        cap = capability_matrix.get(concept_id, {})

        # Skip already mastered concepts
        if cap.get("mastery_level", 0) >= 3:
            continue

        # Check all prerequisites
        prereqs = knowledge_graph.get_prerequisites(concept_id)
        all_prereqs_mastered = all(
            capability_matrix.get(p, {}).get("mastery_level", 0) >= 3
            for p in prereqs
        )

        if all_prereqs_mastered:
            recommended.append(concept_id)

    return recommended


def get_progress_summary(capability_matrix: Dict[str, Any]) -> Dict[str, int]:
    """
    Return summary stats for the capability matrix.

    Returns:
        Dict with keys: total_concepts, mastered, in_progress, struggling, not_started.
    """
    total = len(capability_matrix)
    mastered = 0
    in_progress = 0
    struggling = 0
    not_started = 0

    for concept_id, stats in capability_matrix.items():
        status = stats.get("status", "not_started")
        if status == "mastered" or stats.get("mastery_level", 0) >= 3:
            mastered += 1
        elif status == "struggling":
            struggling += 1
        elif status == "in_progress":
            in_progress += 1
        else:
            not_started += 1

    return {
        "total_concepts": total,
        "mastered": mastered,
        "in_progress": in_progress,
        "struggling": struggling,
        "not_started": not_started,
    }


def update_capability_on_success(
    capability_matrix: Dict[str, Any],
    concept_id: str,
) -> Dict[str, Any]:
    """
    Update the capability matrix after a successful submission.

    Increments successes, attempts, mastery (cap 5), difficulty (cap 5),
    and updates status.
    """
    cap = capability_matrix.get(concept_id, {})
    cap["successes"] = cap.get("successes", 0) + 1
    cap["attempts"] = cap.get("attempts", 0) + 1
    cap["mastery_level"] = min(cap.get("mastery_level", 0) + 1, 5)
    cap["current_difficulty"] = min(cap.get("current_difficulty", 1) + 1, 5)
    cap["last_attempted"] = datetime.now(timezone.utc).isoformat()

    # Update status
    if cap["mastery_level"] >= 3:
        cap["status"] = "mastered"
    else:
        cap["status"] = "in_progress"

    capability_matrix[concept_id] = cap
    return capability_matrix


def update_capability_on_failure(
    capability_matrix: Dict[str, Any],
    concept_id: str,
) -> Dict[str, Any]:
    """
    Update the capability matrix after a failed submission.

    Increments failures, attempts, decreases mastery (floor 0),
    decreases difficulty (floor 1), and checks for struggling status.
    """
    cap = capability_matrix.get(concept_id, {})
    cap["failures"] = cap.get("failures", 0) + 1
    cap["attempts"] = cap.get("attempts", 0) + 1
    cap["mastery_level"] = max(cap.get("mastery_level", 0) - 1, 0)
    cap["current_difficulty"] = max(cap.get("current_difficulty", 1) - 1, 1)
    cap["last_attempted"] = datetime.now(timezone.utc).isoformat()

    # Check for struggling (2+ consecutive failures)
    if cap["failures"] >= 2:
        cap["status"] = "struggling"
    else:
        cap["status"] = "in_progress"

    capability_matrix[concept_id] = cap
    return capability_matrix
