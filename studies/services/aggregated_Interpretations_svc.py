from collections import namedtuple
from typing import List

from studies.choices import InterpretationsChoices, AggregatedInterpretationsChoices

AggregatedInterpretationDTO = namedtuple(
    "AggregatedInterpretationDTO", ["parent_theory_names", "parent_theory_acronyms", "type"]
)


class AggregatedInterpretationService:
    def __init__(self, interpretations: List[AggregatedInterpretationDTO]):
        self.interpretations = sorted(interpretations, key=lambda x: x.parent_theory_names)

    def resolve(self) -> List[AggregatedInterpretationDTO]:
        results = []
        # first pro
        pro_names = [x.parent_theory_names for x in self.interpretations if x.type == InterpretationsChoices.PRO]
        if len(pro_names):
            pro_acronym_names = [
                x.parent_theory_acronyms for x in self.interpretations if x.type == InterpretationsChoices.PRO
            ]
            aggregated_name = " & ".join(pro_names)
            aggregated_acronyms = " & ".join(pro_acronym_names)
            results.append(
                AggregatedInterpretationDTO(
                    parent_theory_names=aggregated_name,
                    type=AggregatedInterpretationsChoices.PRO,
                    parent_theory_acronyms=aggregated_acronyms,
                )
            )

        challenge_names = [
            x.parent_theory_names for x in self.interpretations if x.type == InterpretationsChoices.CHALLENGES
        ]
        if len(challenge_names):
            challenges_acronym_names = [
                x.parent_theory_acronyms for x in self.interpretations if x.type == InterpretationsChoices.CHALLENGES
            ]

            aggregated_name = " & ".join(challenge_names)
            aggregated_acronyms = " & ".join(challenges_acronym_names)

            results.append(
                AggregatedInterpretationDTO(
                    parent_theory_names=aggregated_name,
                    type=AggregatedInterpretationsChoices.CHALLENGES,
                    parent_theory_acronyms=aggregated_acronyms,
                )
            )

        return results
