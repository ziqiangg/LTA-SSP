---
id: PA-008
title: GOV.UK Service Manual — Check if you need to meet the Service Standard
source: https://www.gov.uk/service-manual/service-assessments/check-if-need-to-meet-service-standard
kind: gov-framework
retrieved: 2026-09-01
rq: [RQ-4]
relevance: high
---

## What it is
A live, deployed, government-published page whose entire job is the question our
`find-your-system-type` wizard is trying to answer: *does this standard apply to my thing,
and how much of it?* It is the closest functional analogue to our wizard in the wild, it
covers the same subject matter as our 9 Digital Service Standards domains, and it reaches its
answer without a decision tree, a form, or a single line of JavaScript.

## Mechanism
The page separates two questions that our wizard conflates, and answers each with different
machinery.

**Question 1 — must the standard be met?** Answered by a *definition*, not a questionnaire. A
service must meet the Service Standard if it is transactional, and "transactional" is defined
by what the user can do: exchange information, money, permission, goods or services; or
submit personal information that results in a change to a government record. The scope is
then widened by an explicit anti-exemption — this applies even to internal services used only
by civil servants — which pre-empts the most common attempt to argue out of scope.

**Question 2 — is a formal assessment needed?** Answered by *numeric and organisational
thresholds*, which is a different kind of test entirely: likely to handle more than 100,000
transactions a year, or civil servants from multiple organisations will use it. Below those,
a departmental panel assesses instead — so the answer is never "nothing applies", it is
"a lighter process applies". There is one carve-out with a hard number: services built on
assured form-building platforms expecting fewer than 10,000 transactions a year need no
assessment, with departments free to impose lighter-touch review anyway. Spend-control
approval can override everything and force an assessment regardless.

**Borderline cases are handled by degrading the standard, not by excluding the service.**
Non-transactional things — a website, a calculator — do not fall out of scope; the guidance
says to adapt the requirements. The worked example is precise: you will not need to publish
the mandatory KPI data, but you should still know what users are trying to do and collect
data on whether they can. Internal services adjust specific expectations, e.g. uptime scoped
to business hours rather than 24/7.

**Assessment scope is bounded but contextual**: the assessment covers the transaction being
built, plus the team's understanding of the wider user journey and what they did to integrate
into it. Explicitly, the whole journey need not work for a service to pass, provided the team
takes reasonable steps and fixes it in increments.

## Transfer to LTA-SSP
1. **Split the wizard's single question into "does it apply" and "how much process".** Our
   7 questions produce one system type, which bundles both. GOV.UK's split is cleaner and
   maps onto our data: *which* controls (a definitional test on what the system does) is a
   different question from *at what level* (a threshold test on scale and blast radius).
   Since our profiles nest, the level axis is genuinely ordinal and threshold-shaped — this
   is more evidence for the two-axis model argued in PA-006.
2. **Definitions beat decision trees for the applicability half.** A definition is auditable,
   quotable, and does not degrade when a system is two things at once — a system that is both
   an internal tool and a public service simply satisfies the definition. Our
   `find-your-system-type/index.html` could lead with a definitional statement per system type
   and offer the questionnaire as an aid rather than as the mechanism. That directly removes
   the "returns exactly one type" limitation without building anything.
3. **Numeric thresholds are the honest form of a risk tier, and we have none.** "More than
   100,000 transactions" and "fewer than 10,000" are checkable by the reader without a
   security background. Our low/medium/high risk distinction has no published operationalisa-
   tion at all. If the upstream SSP does not supply thresholds, that absence is itself a
   research finding worth filing against the standard — it is the difference between a wizard
   the user can verify and one they must trust.
4. **"Adapt, don't exclude" is the right default for our L2/optional controls.** GOV.UK never
   lets a service escape the standard; it lets it meet a weaker form. That is exactly what our
   level-2 controls are for, and it argues for presenting non-applicable controls as
   *downgraded* rather than *absent* — converging independently on the same conclusion as
   CAF (PA-002) and 800-53B's "every control is accounted for" (PA-005). Three independent
   frameworks reaching the same design suggests our filtered-list presentation is the
   outlier.
5. **Name the override.** Spend-control approval trumps the criteria. Our equivalent — an
   agency security officer or a contractual requirement mandating controls the wizard did not
   return — should be stated on the results page, or users will read the wizard output as
   exhaustive.

## Limits
This page scopes *one* standard with a small number of criteria; it does not select controls,
and there is nothing here about getting from a system description to a specific requirement
list. The thresholds are policy artefacts with no derivation given, so they transfer as a
*form* but not as values — we cannot borrow 100,000 transactions. It also leans on
institutions we lack: a departmental assessment panel absorbs every borderline case, which is
what lets the published criteria stay this short. A static site with no panel behind it cannot
push ambiguity anywhere, so copying the brevity without the escalation route would leave users
stranded. Finally, "adapt the requirements" is undefined for the non-transactional case beyond
one KPI example — the guidance tells you to tailor without saying to what.

## Quotes
- The applicability definition, a service is transactional if users can "exchange information,
  money, permission, goods or services" or "submit personal information that results in a
  change to a government record".
- Scope widening: all transactional services developed for central government must meet the
  Service Standard, and this applies even to internal services used only by civil servants.
- Assessment thresholds: a formal assessment is required if the service is "likely to handle
  more than 100,000 transactions annually" or if "civil servants from multiple organizations
  will use the service"; otherwise departmental panels conduct assessments.
- The carve-out: services using assured form-building platforms do not require assessment if
  they expect "fewer than 10,000 transactions per year".
- Override: if getting an assessment is a condition of spend control approval, the service must
  be assessed "even if it does not meet the usual criteria".
- Adapt rather than exclude: for something non-transactional "like a website or calculator...
  You won't need to publish data on the mandatory KPIs, but you should still know what your
  users are trying to do and collect data that helps you work out whether they're able to do
  that or not."
- Bounded assessment: the whole user journey need not work, provided teams take "reasonable
  steps to make things better and fix the journey in increments."
