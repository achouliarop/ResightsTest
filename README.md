# Ownership Structure Calculator

Algorithm to calculate real ownership percentages in complex corporate structures with range-based ownership shares.

## Problem Statement

Calculate the "real ownership" percentages (lower, average, upper) for entities in ownership structures where:

- Shares are expressed as ranges (e.g., "10-15%")
- Structures can be cyclical or hierarchical
- Entities can appear at multiple depths relative to the focus company (depth=0)
- Must handle both:
  - Entities _owning_ the focus company (depth > 0)
  - Entities _owned by_ the focus company (depth < 0)

## Key Assumptions

1. Single unique focus company exists (depth=0)
2. Share ranges are parsed as:
   - "X-Y%" → [X, (X+Y)/2, Y]
   - "<X%" → [0, X/2, X]
   - "X%" → [X, X, X]
3. Ownership propagates bidirectionally:
   - Upstream to focus company (depth > 0 → depth=0)
   - Downstream from focus company (depth=0 → depth < 0)
4. If an edge is `active=false`, it is ignored

## Solution Design

### Algorithm

1. **Graph Construction**

   - Nodes: Companies/entities
   - Edges: Ownership ranges (lower, avg, upper)
   - Direction: Source → Target ownership

2. **Iterative Convergence**

   - Initialize focus company with 100% ownership
   - Repeatedly update ownership values until changes < threshold:
     ```
     new_ownership[node] = Σ (edge_share * target_ownership)
     ```
   - Handles cycles through iterative relaxation

3. **Bidirectional Propagation**
   - Natural result of graph traversal:
     - Depth > 0: Ownership flows _to_ focus node
     - Depth < 0: Ownership flows _from_ focus node

## Various example usecases explained

1. **Simple ownership (no cycles)**
   If the structure is a simple chain, like Company C2 owns Company C1, and Company C1 owns the Focus Company FC ( C2 -> C1 -> FC ), the calculation is straightforward.

   - If C2 owns 70% of C1, and C1 owns 50% of FC (Focus Company).
   - C2's real ownership in FC is 70% \* 50% = 35% .
   - C1's real ownership in FC is 50% (its direct share).

2. **Complex ownership (with cycles)**
   If the structure is more complex, like Company C2 owns Company C1, and Company C1 owns Company C2 ( C2 -> C1 -> C2 ), the calculation becomes more complex.

   - Entities: C1, C2, FC (Focus Company).
   - Direct Shares:

     - C1 owns 100% of FC.
     - C1 owns 10% of C2.
     - C2 owns 50% of FC.
     - C2 owns 5% of C1.

   - Initialize: `RealStake_C1_in_FC = 0%`, `RealStake_C2_in_FC = 0%`.
   - **Iteration 1:**

   - For C1:
     - Direct from FC: 100%.
     - Indirect via C2: `10% RealStake_C2_in_FC_previous (0%) = 0%`.
     - `New_RealStake_C1_in_FC = 100% + 0% = 100%`. (Cap at 100% -> 100%)
   - For C2:
     - Direct from FC: 50%.
     - Indirect via C1: `5% RealStake_C1_in_FC_previous (0%) = 0%`.
     - `New_RealStake_C2_in_FC = 50% + 0% = 50%`. (Cap at 100% -> 50%)
   - After Iteration 1: `RealStake_C1_in_FC = 100%`, `RealStake_C2_in_FC = 50%`.

   - **Iteration 2:**

   - For C1:
     - Direct from FC: 100%.
     - Indirect via C2: `10% RealStake_C2_in_FC_iter1 (50%) = 5%`.
     - `New_RealStake_C1_in_FC = 100% + 5% = 105%`. (Cap at 100% -> 100%)
   - For C2:
     - Direct from FC: 50%.
     - Indirect via C1: `5% RealStake_C1_in_FC_iter1 (100%) = 5%`.
     - `New_RealStake_C2_in_FC = 50% + 5% = 55%`. (Cap at 100% -> 55%)
   - After Iteration 2: `RealStake_C1_in_FC = 100%`, `RealStake_C2_in_FC = 55%`.

   - **Iteration 3:**

   - For C1:
     - Direct from FC: 100%.
     - Indirect via C2: `10% RealStake_C2_in_FC_iter2 (55%) = 5.5%`.
     - `New_RealStake_C1_in_FC = 100% + 5.5% = 105.5%`. (Cap at 100% -> 100%)
   - For C2:
     - Direct from FC: 50%.
     - Indirect via C1: `5% RealStake_C1_in_FC_iter2 (100%) = 5%`.
     - `New_RealStake_C2_in_FC = 50% + 5% = 55%`. (Cap at 100% -> 55%)
   - After Iteration 3: `RealStake_C1_in_FC = 100%`, `RealStake_C2_in_FC = 55%`.

The values have converged: C1 effectively owns 100% of FC, and C2 effectively owns 55% of FC.
