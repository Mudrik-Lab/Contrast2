from collections import namedtuple
from typing import List, Dict

from studies.choices import InterpretationsChoices, AggregatedInterpretationsChoices

AggregatedInterpretationDTO = namedtuple("AggregatedInterpretationDTO", ["parent_theory_names", "type"])


class AggregatedInterpretationService:
    def __init__(self, interpretations: List[AggregatedInterpretationDTO]):
        self.interpretations = sorted(interpretations, key=lambda x:x.parent_theory_names)

    def resolve(self) -> List[AggregatedInterpretationDTO]:
        results = []
        # first pro
        pro_names = [x.parent_theory_names for x in self.interpretations if x.type == InterpretationsChoices.PRO]
        if len(pro_names):
            aggregated_name = " & ".join(pro_names)
            results.append(AggregatedInterpretationDTO(parent_theory_names=aggregated_name, type=AggregatedInterpretationsChoices.PRO))

        challenge_names = [x.parent_theory_names for x in self.interpretations if x.type == InterpretationsChoices.CHALLENGES]
        if len(challenge_names):
            aggregated_name = " & ".join(challenge_names)
            results.append(AggregatedInterpretationDTO(parent_theory_names=aggregated_name,
                                                       type=AggregatedInterpretationsChoices.CHALLENGES))

        return results
