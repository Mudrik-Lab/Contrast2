# Fix Plan: UnconTraSt Paradigm Breakdown Label Bug

## Problem Summary

In the UnconTraSt application's "Experiments Comparison with Paradigm Breakdown" feature, the pie charts display numeric labels (7, 22, 1, 2, 3, etc.) instead of paradigm names. This is a **backend data issue** in the Contrast2 repository.

## Root Cause

**Location:** `Contrast2/uncontrast_studies/processors/experiments_comparison.py:36-43`

The `process_paradigm()` method in the `ComparisonParametersDistributionPieGraphDataProcessor` class incorrectly queries the paradigm ForeignKey ID instead of the paradigm name:

```python
def process_paradigm(self, experiments: QuerySet[UnConExperiment]):
    subquery = (
        experiments.distinct()
        .values("paradigm")          # ❌ Returns FK ID (numeric: 7, 22, 1, etc.)
        .annotate(experiment_count=Count("id", distinct=True))
        .annotate(key=F("paradigm")) # ❌ key becomes the numeric ID
    )
    return subquery
```

**Data Model Context:**
- `UnConExperiment.paradigm` → ForeignKey to `UnConSpecificParadigm`
- `UnConSpecificParadigm.name` → CharField (the paradigm name we need)

## Solution

Follow the established pattern used by other working breakdown methods in the same file (like `process_task`, `process_outcome_type`, etc.):

### Step 1: Add Missing Import

Add `UnConSpecificParadigm` to the imports at the top of the file (around line 6-18):

```python
from uncontrast_studies.models import (
    UnConSample,
    UnConModalityType,
    UnConStimulusCategory,
    UnConStimulusSubCategory,
    UnConsciousnessMeasureType,
    UnConsciousnessMeasurePhase,
    UnConTaskType,
    UnConProcessingMainDomain,
    UnConSuppressedStimulus,
    UnConSuppressionMethodType,
    UnConOutcome,
    UnConSpecificParadigm,  # ← ADD THIS
)
```

### Step 2: Fix the `process_paradigm()` Method

Replace the current implementation (lines 36-43) with:

```python
def process_paradigm(self, experiments: QuerySet[UnConExperiment]):
    subquery = (
        UnConSpecificParadigm.objects.filter(experiments__in=experiments)
        .distinct()
        .values("name")
        .annotate(experiment_count=Count("experiments", distinct=True))
        .annotate(key=F("name"))
    )
    return subquery
```

**Why this works:**
- Queries `UnConSpecificParadigm` directly (the related model)
- Uses `.filter(experiments__in=experiments)` to get paradigms linked to the filtered experiments
- Extracts the `name` field via `.values("name")`
- Counts experiments via the reverse relationship `Count("experiments", ...)`
- Assigns the paradigm name to `key` instead of the numeric ID

## Verification Pattern

This solution follows the exact same pattern as other working breakdowns in the file:

**Example 1: `process_task` (lines 67-76)**
```python
UnConTaskType.objects.filter(tasks__experiment__in=experiments)
    .values("name")
    .annotate(key=F("name"))
```

**Example 2: `process_outcome_type` (lines 56-65)**
```python
UnConOutcome.objects.filter(findings__experiment__in=experiments)
    .values("name")
    .annotate(key=F("name"))
```

## Files to Modify

### Backend (Contrast2)
- **Primary:** `Contrast2/uncontrast_studies/processors/experiments_comparison.py`
  - Line ~12: Add `UnConSpecificParadigm` import
  - Lines 36-43: Replace `process_paradigm()` method implementation

### No Frontend Changes Required
The frontend (`ContrastFront/src/uncontrast/pages/ExperimentsComparison/ExperimentsComparison.jsx`) correctly renders whatever data it receives from the API. No changes needed.

## Automated Test

Add a new test method to verify the paradigm breakdown returns paradigm names instead of numeric IDs.

### Test File Location
`Contrast2/uncontrast_studies/tests/test_experiments_comparison.py`

### Test Implementation

Add the following test method to the `TestExperimentsComparisonGraphTestCase` class:

```python
def test_paradigm_breakdown_returns_paradigm_names(self):
    """Test that paradigm breakdown returns paradigm names, not numeric IDs"""
    self._setup_world()

    # Call the paradigm breakdown endpoint
    target_url = self.reverse_with_query_params(
        "uncontrast-experiments-graphs-parameters-distribution-experiments-comparison",
        breakdown="paradigm"
    )
    res = self.client.get(target_url)

    # Assert successful response
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertIsInstance(res.data, list)

    # Verify paradigm breakdown data structure
    for sub_graph in res.data:
        # Each sub-graph represents a significance level (Positive, Negative, Mixed)
        self.assertIn("series_name", sub_graph)
        self.assertIn(sub_graph["series_name"], SignificanceChoices.values)

        # Verify series data contains paradigm names, not numeric IDs
        series = sub_graph.get("series", [])
        if len(series) > 0:
            for data_point in series:
                self.assertIn("key", data_point)
                self.assertIn("value", data_point)

                # CRITICAL: Key should be a string (paradigm name), not an integer (ID)
                self.assertIsInstance(data_point["key"], str,
                    f"Expected paradigm name (string), got {type(data_point['key']).__name__}: {data_point['key']}")

                # Key should be the actual paradigm name from our test data
                self.assertEqual(data_point["key"], "specific_paradigm")

                # Value should be experiment count
                self.assertIsInstance(data_point["value"], int)
                self.assertGreater(data_point["value"], 0)
```

### Test Setup

The test uses the existing `_setup_world()` method which creates:
- A main paradigm: `"main_paradigm"`
- A specific paradigm: `"specific_paradigm"` (linked to main paradigm)
- 6 experiments with different significance levels, all using the same specific paradigm

### What the Test Validates

1. **API Response Structure:** Ensures the endpoint returns valid data
2. **Data Type Check:** Verifies that `key` is a string (paradigm name), not an integer (numeric ID)
3. **Correct Value:** Confirms the key matches the actual paradigm name from test data
4. **Experiment Counts:** Ensures values are positive integers

### Test Dependencies

The test relies on:
- `UnContrastBaseTestCase` helper methods for creating test data
- `SignificanceChoices` for validating significance categories
- Django REST Framework's `APITestCase` for HTTP testing

## Manual Testing Recommendations

After applying the fix and running automated tests:

1. **Manual UI Testing:**
   - Navigate to UnconTraSt → Experiments Comparison
   - Select "Paradigm" from the breakdown dropdown
   - Verify pie charts show paradigm names instead of numbers

2. **Manual API Testing:**
   - Test endpoint: `uncontrast_studies/experiments_graphs/parameters_distribution_experiments_comparison/?breakdown=paradigm`
   - Verify response contains `{"key": "Paradigm Name", "value": count}` instead of `{"key": 7, "value": count}`

3. **Regression Testing:**
   - Run full test suite: `python manage.py test uncontrast_studies.tests.test_experiments_comparison`
   - Verify other breakdowns (task, outcome_type, etc.) still work correctly
   - Check all three significance categories (Negative, Positive, Mixed)

## Expected Outcome

After implementation, the paradigm breakdown pie charts will display:
- **Before:** "7", "22", "1", "2", "3", "5", "14"
- **After:** Actual paradigm names like "Visual Search", "Priming", "Attentional Blink", etc.

**Automated Test Result:**
- ✅ Test passes: Paradigm breakdown returns paradigm names (strings)
- ❌ Test fails: Paradigm breakdown returns numeric IDs (integers)
