"""
Knowledge Graph Engine for AdaptLab.

Parses the Obsidian-style curriculum vault (Markdown files with YAML frontmatter)
into a NetworkX DAG. Provides query methods for traversal, prerequisite lookup,
and topological ordering.
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

import frontmatter
import networkx as nx

logger = logging.getLogger(__name__)


class KnowledgeGraphError(Exception):
    """Raised when the knowledge graph fails to build or validate."""
    pass


class KnowledgeGraph:
    """
    In-memory directed acyclic graph (DAG) of C programming concepts.

    Built from Markdown files with YAML frontmatter in the curriculum directory.
    Each node is a concept with attributes: title, level, description.
    Edges represent prerequisite relationships (prerequisite → concept).
    """

    def __init__(self, curriculum_path: str):
        """
        Initialize the knowledge graph from a curriculum directory.

        Args:
            curriculum_path: Absolute or relative path to the directory
                             containing curriculum .md files.

        Raises:
            KnowledgeGraphError: If the directory is empty, files are invalid,
                                 or the graph contains cycles.
        """
        self.curriculum_path = Path(curriculum_path)
        self.graph = nx.DiGraph()
        self._build_graph()

    def _build_graph(self) -> None:
        """Parse all .md files and construct the DAG."""
        if not self.curriculum_path.exists():
            raise KnowledgeGraphError(
                f"Curriculum directory not found: {self.curriculum_path}"
            )

        md_files = list(self.curriculum_path.glob("*.md"))
        if not md_files:
            raise KnowledgeGraphError(
                f"No .md files found in {self.curriculum_path}"
            )

        logger.info(f"Loading curriculum from {self.curriculum_path} ({len(md_files)} files)")

        # First pass: create all nodes
        concepts = {}
        for md_file in md_files:
            try:
                post = frontmatter.load(str(md_file))
            except Exception as e:
                raise KnowledgeGraphError(
                    f"Failed to parse {md_file.name}: {e}"
                )

            # Validate required frontmatter fields
            required_fields = ["id", "title", "level", "prerequisites", "unlocks"]
            for field in required_fields:
                if field not in post.metadata:
                    raise KnowledgeGraphError(
                        f"Missing required field '{field}' in {md_file.name}"
                    )

            concept_id = post.metadata["id"]
            if concept_id in concepts:
                raise KnowledgeGraphError(
                    f"Duplicate concept ID '{concept_id}' found in {md_file.name}"
                )

            concepts[concept_id] = {
                "title": post.metadata["title"],
                "level": int(post.metadata["level"]),
                "prerequisites": post.metadata.get("prerequisites", []) or [],
                "unlocks": post.metadata.get("unlocks", []) or [],
                "description": post.content.strip(),
                "file": md_file.name,
            }

        # Add nodes to graph
        for concept_id, attrs in concepts.items():
            self.graph.add_node(
                concept_id,
                title=attrs["title"],
                level=attrs["level"],
                description=attrs["description"],
                file=attrs["file"],
            )

        # Second pass: add edges (prerequisite → concept)
        for concept_id, attrs in concepts.items():
            for prereq_id in attrs["prerequisites"]:
                if prereq_id not in concepts:
                    logger.warning(
                        f"Concept '{concept_id}' lists unknown prerequisite "
                        f"'{prereq_id}' — skipping edge"
                    )
                    continue
                self.graph.add_edge(prereq_id, concept_id)

        # Validate DAG
        if not nx.is_directed_acyclic_graph(self.graph):
            cycles = list(nx.simple_cycles(self.graph))
            raise KnowledgeGraphError(
                f"Knowledge graph contains cycles: {cycles}. "
                "The curriculum must form a valid DAG."
            )

        logger.info(
            f"Knowledge graph loaded: {self.graph.number_of_nodes()} concepts, "
            f"{self.graph.number_of_edges()} prerequisite edges, DAG valid ✓"
        )

    def get_concept(self, concept_id: str) -> Dict[str, Any]:
        """
        Return node attributes for a concept.

        Args:
            concept_id: The unique concept identifier.

        Returns:
            Dict with keys: title, level, description, file.

        Raises:
            KeyError: If concept_id is not found in the graph.
        """
        if concept_id not in self.graph:
            raise KeyError(f"Concept '{concept_id}' not found in knowledge graph")
        attrs = dict(self.graph.nodes[concept_id])
        attrs["id"] = concept_id
        return attrs

    def get_prerequisites(self, concept_id: str) -> List[str]:
        """Return immediate predecessor concept IDs (prerequisites)."""
        if concept_id not in self.graph:
            raise KeyError(f"Concept '{concept_id}' not found in knowledge graph")
        return list(self.graph.predecessors(concept_id))

    def get_unlocks(self, concept_id: str) -> List[str]:
        """Return immediate successor concept IDs (concepts this unlocks)."""
        if concept_id not in self.graph:
            raise KeyError(f"Concept '{concept_id}' not found in knowledge graph")
        return list(self.graph.successors(concept_id))

    def get_all_concepts(self) -> List[Dict[str, Any]]:
        """Return all concepts sorted by level, then alphabetically by id."""
        concepts = []
        for node_id in self.graph.nodes:
            concept = dict(self.graph.nodes[node_id])
            concept["id"] = node_id
            concepts.append(concept)
        concepts.sort(key=lambda c: (c["level"], c["id"]))
        return concepts

    def get_concepts_at_level(self, level: int) -> List[Dict[str, Any]]:
        """Return all concepts at a given difficulty level."""
        return [
            c for c in self.get_all_concepts()
            if c["level"] == level
        ]

    def find_backtrack_target(
        self,
        concept_id: str,
        capability_matrix: dict,
    ) -> Optional[str]:
        """
        Find the weakest prerequisite to backtrack to.

        Returns the prerequisite with the lowest mastery_level that is
        below the mastery threshold (3). Returns None if all prerequisites
        are sufficiently mastered.

        Args:
            concept_id: The concept the student is struggling with.
            capability_matrix: The student's full capability matrix.

        Returns:
            The concept_id of the weakest prerequisite, or None.
        """
        prereqs = self.get_prerequisites(concept_id)
        if not prereqs:
            return None

        weakest = None
        lowest_mastery = float("inf")

        for prereq_id in prereqs:
            cap = capability_matrix.get(prereq_id, {})
            mastery = cap.get("mastery_level", 0)
            if mastery < 3 and mastery < lowest_mastery:
                lowest_mastery = mastery
                weakest = prereq_id

        return weakest

    def topological_order(self) -> List[str]:
        """Return concept IDs in topological sort order."""
        return list(nx.topological_sort(self.graph))

    def get_graph_summary(self) -> Dict[str, List[str]]:
        """
        Return a dict mapping each concept_id to its list of prerequisite IDs.
        Used as input for the Teacher Agent.
        """
        summary = {}
        for node_id in self.graph.nodes:
            summary[node_id] = list(self.graph.predecessors(node_id))
        return summary

    def get_all_concept_ids(self) -> List[str]:
        """Return all concept IDs."""
        return list(self.graph.nodes)
