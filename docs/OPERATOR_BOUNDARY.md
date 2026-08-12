# FitzSight Operator Boundary

**Version:** v0.10.0  
**Policy date:** 2026-08-11

FitzSight's competition handoff separates **artifact preparation** from **external submission actions**.

## Default rule

Project scripts may build, validate, hash, package, render, and inspect local artifacts. They do **not** submit forms, upload files to competition portals, send email, search email, modify cloud services, or perform other external write actions.

Actual competition submission is **user-manual only** unless the user gives a separate, explicit instruction for a specific external action.

By default, FitzSight automation **does not submit** anything to the competition portal and does not access Gmail or any other email service for confirmation.

## Assistant / automation scope

Allowed by default:

- build and test FitzSight code;
- generate PPTX/PDF, offline HTML/video, manifests, checksums, and upload-ready ZIPs;
- run local preflight, benchmark, adversarial, runtime-doctor, and secret checks;
- prepare copy-ready portal text and manual checklists;
- identify which external steps still require human action.

Not allowed by default:

- submit or edit a GOAI portal entry;
- upload files to the GOAI portal;
- search, read, send, reply to, label, archive, or delete email for submission confirmation;
- use external accounts to confirm submission status;
- publish or modify GitHub content on the user's behalf;
- perform any other external write merely because an artifact is ready.

## Manual-only submission steps

The user performs:

1. open the official submission portal;
2. verify the portal's current fields and limits;
3. paste the prepared project copy;
4. upload the selected PPT/PDF/video assets;
5. enter the public repository link;
6. review the final portal state;
7. click the actual submission button;
8. save confirmation screenshot/email/receipt locally.

Repository evidence alone must never be treated as proof that these external steps occurred.

## External runtime validation

Streamlit and OpenAI live validation are also environment-dependent. FitzSight provides local validators, but a live result is marked complete only after the user runs them in an environment where the dependency/credential is genuinely available and provides the output as evidence.

## Handoff principle

The project should reach a state where the user can take the prepared handoff packet, follow a short manual checklist, and complete external submission without needing further code generation or analytical work.
