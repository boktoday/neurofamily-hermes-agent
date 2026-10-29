# NDIS library (Australia)

A local, offline copy of the official NDIS documents the family agent uses to answer scheme questions with real sources, not model memory.

- **59 documents**, current to October 2026. Fetched from ndis.gov.au and legislation.gov.au on 15 October 2026.
- Every file opens with its source URL and fetch date. Nothing here is advice: the agent quotes the documents, names them, and tells the family where to confirm.
- Licence: material is (c) National Disability Insurance Agency (NDIA) or the Commonwealth of Australia as marked at each source. NDIS website material carries a Creative Commons Attribution-NonCommercial (CC BY-NC 3.0) licence; the legislation is reproduced under standard Commonwealth terms. This library is for noncommercial family support use only. Do not strip the attribution headers from the files.
- Logos and third-party material are excluded (text only).

## What is here

### Guidelines and scheme pages (16)
- `ndis-our-guidelines.md` (NDIS guidelines index (all topics))
- `ndis-what-is-the-ndis.md` (What is the NDIS)
- `ndis-how-the-ndis-works.md` (How the NDIS works)
- `ndis-guide-to-getting-started.md` (A guide to getting started)
- `ndis-what-is-a-nominee.md` (What is a nominee)
- `ndis-pricing-arrangements.md` (Pricing arrangements (how pricing works))
- `ndis-support-catalogue.md` (What is the support catalogue)
- `ndis-changes-overview.md` (Changes to the NDIS (overview))
- `ndis-new-way-of-planning.md` (The new way of planning)
- `ndis-laws.md` (NDIS laws hub)
- `ndis-changes-plan-management.md` (Changes to plan management)
- `ndis-law-getting-back-on-track.md` (NDIS laws: Getting the NDIS back on track (October 2024))
- `ndis-law-integrity-and-safeguarding.md` (NDIS laws: Integrity and safeguarding (2026))
- `ndis-law-securing-the-future.md` (NDIS laws: Securing the NDIS for future generations (August 2026))
- `ndis-review.md` (The NDIS Review)
- `ndis-supports-lists.md` (NDIS supports lists (what funding can and cannot cover))

### Operational guideline documents (41)
Each is the current official document for its topic, as published by the NDIA.

- `applying-to-the-ndis.md` (Applying to the NDIS (eligibility))
- `community-connections.md` (Community connections)
- `early-childhood-approach.md` (Early childhood approach)
- `early-connections.md` (Early connections)
- `principles-creating-your-plan.md` (Principles we follow to create your plan)
- `reasonable-and-necessary-supports.md` (Reasonable and necessary supports)
- `creating-your-plan.md` (Creating your plan)
- `your-plan.md` (Your plan)
- `plan-reassessments.md` (Plan reassessments)
- `plan-variations.md` (Plan variations)
- `reviewing-our-decisions.md` (Reviewing our decisions)
- `appointing-a-nominee.md` (Appointing a nominee)
- `child-representatives.md` (Child representatives)
- `behaviour-support.md` (Behaviour support)
- `therapy-supports.md` (Therapy supports)
- `including-specific-supports-in-plans.md` (Including specific types of supports in plans)
- `ndis-pricing-schedule-2026-27.md` (NDIS pricing schedule 2026-27 (maximum price limits))
- `leaving-the-ndis.md` (Leaving the NDIS)
- `justice-system.md` (Justice system)
- `mainstream-community-supports.md` (Mainstream and community supports)
- `your-privacy-and-information.md` (Your privacy and information)
- `compensation.md` (Compensation)
- `specialist-disability-accommodation.md` (Specialist disability accommodation (SDA))
- `short-term-accommodation.md` (Short term accommodation (STA))
- `medium-term-accommodation.md` (Medium term accommodation (MTA))
- `supported-independent-living.md` (Supported independent living (SIL))
- `individualised-living-options.md` (Individualised living options (ILO))
- `younger-people-residential-aged-care.md` (Younger people in residential aged care)
- `assistive-technology.md` (Assistive technology)
- `social-and-recreation-supports.md` (Social and recreation supports)
- `work-and-study-supports.md` (Work and study supports)
- `assistance-animals.md` (Assistance animals including dog guides)
- `vehicle-modifications.md` (Vehicle modifications and specialised driver training)
- `home-modifications.md` (Home modifications)
- `disability-related-health-supports.md` (Disability-related health supports)
- `dysphagia-supports.md` (Dysphagia supports)
- `nutrition-supports.md` (Nutrition supports including meal preparation)
- `diabetes-management-supports.md` (Diabetes management supports)
- `continence-supports.md` (Continence supports)
- `wound-and-pressure-care-supports.md` (Wound and pressure care supports)
- `podiatry-and-foot-care-supports.md` (Podiatry and foot care supports)

### Legislation (2)
- `ndis-act-2013.md` (National Disability Insurance Scheme Act 2013 (consolidated, as at 1 October 2026))
- `ndis-supports-for-participants-rules.md` (NDIS (Supports for Participants) Rules 2013 (current compilation))

## Refreshing

Run `python scripts/fetch-ndis-docs.py` from the repo root. The documents and legislation download directly; the guideline web pages sit behind a bot wall that refuses simple fetch tools, so the script explains how to refresh those with a real browser. Refresh monthly, and always after an NDIS announcement: the August 2026 laws ("Securing the NDIS for future generations") are the most recent package at the time of this copy.

## Using it

`skills/ndis-guide/SKILL.md` is the front door: it maps family questions to documents and sets the citation, currency and boundary rules.

## Keeping this current

The NDIS moves its rules, price limits and guidelines on its own timetable, and a family agent quoting a
superseded rule is worse than one that admits ignorance. Two scripts keep this honest:

- `python scripts/ndis_watch.py` hashes ten official sources (the consolidated Act, pricing arrangements and
  price limits, eligibility, what the NDIS is, reasonable and necessary, would we fund it, the early childhood
  approach guide and partner page, and the news feed) plus every file in this library. It prints nothing when
  nothing has changed and exits 0. When something has moved it writes a note in `changes/<date>.md` and exits 2.
- `python scripts/fetch-ndis-docs.py` downloads the latest documents and legislation. The sixteen
  guideline pages sit behind a bot wall, so `python scripts/fetch-ndis-pages.py --write` fetches those with
  a real browser. It refuses to overwrite a page with thinner text than the file already holds, because a
  fresher-but-poorer capture is a regression in a library that gets quoted. `ndis_watch.py --refresh`
  runs it for you after a change is detected.

The schedule in `schedules/ndis-watch.md` runs the check every 14 days and speaks only when something moved.
A blocked page is recorded as `blocked` and keeps its previous hash, so a bot wall can never overwrite a good
source with an error page.
