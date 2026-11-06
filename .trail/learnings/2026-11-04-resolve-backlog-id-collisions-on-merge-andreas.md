---
type: 'Learning'
title: Resolve backlog ID collisions on merge
author: Andreas
date: 2026-11-04
branch: main
---

## Decided
When independently maintained branches allocate the same open backlog ID, keep the already-published upstream ID and assign the local item the next unused ID; update its links and preserve all other rows.

## Tried and ruled out
Renumbering the upstream item or dropping either row would discard established history.

## Watch out
A docs README or kickoff file may link to the local backlog ID, so search and update all references when resolving the collision.
