# ACRIS Document Types Reference

This document describes all document types found in the ACRIS `document_control_codes` table, organized by class.

---

## 1. Deeds and Other Conveyances

These transfer ownership or rights to real property.

| Code | Name | What it means |
|------|------|---------------|
| DEED | Deed | The core document — transfers property ownership from seller to buyer |
| DEED, LE | Life Estate Deed | Transfers property but the grantor retains the right to live there until death |
| CONDEED | Confirmatory Deed | Corrects or confirms a prior deed — doesn't create a new transfer |
| CORRD | Correction Deed | Fixes errors (names, legal descriptions) in a previously recorded deed |
| DEEDP | Deed, Pre RPT Tax | Deed recorded before the Real Property Transfer Tax existed |
| DEED, TS | Timeshare Deed | Transfers timeshare interest in a property |
| DEED, RC | Deed with Restrictive Covenant | Deed that includes restrictions on how the property can be used |
| REIT | Real Estate Inv Trust Deed | Transfer involving a Real Estate Investment Trust |
| IDED | In Rem Deed | City sells a property seized for unpaid taxes via in rem foreclosure |
| TODD | Transfer on Death Deed | Property automatically transfers to a beneficiary when owner dies — avoids probate |
| RTOD | Revocation of TOD Deed | Revokes a Transfer on Death deed |
| CNTR | Contract of Sale | The purchase agreement between buyer and seller (before closing) |
| MCON | Memorandum of Contract | Public notice that a contract of sale exists — puts the world on notice |
| ACON | Assignment of Contract/Bid | One party transfers their rights under a sale contract to someone else |
| LEAS | Lease | Long-term lease recorded against the property (typically 10+ years or ground leases) |
| MLEA | Memorandum of Lease | Public notice that a lease exists, without recording the full lease |
| SUBL | Subordination of Lease | Lease agrees to be subordinate to a mortgage — lender gets priority |
| EASE | Easement | Grants someone the right to use part of the property (e.g., utility access, shared driveway) |
| AIRRIGHT | Air Rights | Transfer of air rights — the right to build above a property |
| DEVR | Development Rights | Transfer of unused development potential (related to zoning) |
| CDEC | Condo Declaration | Creates a condominium — divides a building into individually owned units |
| SCDEC | Declaration of Condo in Condo | Secondary condo declaration within an existing condo |
| ASTU | Unit Assignment | Assigns/transfers a specific condo unit |
| CODP | Condemnation Proceedings | Government takes private property for public use (eminent domain) |
| NAPP | Notice of Appropriation | Government notice that it intends to take the property |
| LTPA | Letters Patent | Historic — original grant of land from the government |
| TORREN | Torren | Property registered under the Torrens title system (rare in NYC) |
| VAC | Vacate Order | Court order vacating (nullifying) a prior recorded document |
| DECM | Declaration of Merger | Two adjacent lots or interests merge into one |
| DEEDO | Deed, Other | Catch-all for deeds that don't fit other categories |
| DEED COR | Correct Index/Deed (Office Use) | Office correction to deed index |
| CORR, LE | Correct Life Estate (Office Use) | Office correction to a life estate deed |
| SI CORR | SI Billing Update (Office Use) | Staten Island billing correction |

---

## 2. Mortgages & Instruments

These relate to loans secured by real property.

| Code | Name | What it means |
|------|------|---------------|
| MTGE | Mortgage | The core document — a loan secured by the property |
| ASST | Assignment of Mortgage | Lender sells/transfers the mortgage to a new lender |
| SAT | Satisfaction of Mortgage | Mortgage is fully paid off — lien is released |
| PSAT | Partial Satisfaction | Part of the mortgage debt is satisfied |
| ASPM | Assumption of Mortgage | New borrower takes over an existing mortgage |
| M&CON | Mortgage and Consolidation | New mortgage that consolidates multiple existing mortgages into one |
| CORRM | Correction Mortgage | Fixes errors in a previously recorded mortgage |
| CMTG | Collateral Mortgage | Mortgage used as collateral for another obligation |
| MMTG | Master Mortgage | Template mortgage for a development — individual units reference it |
| SMTG | Sundry Mortgage | Catch-all for mortgage-related documents that don't fit other categories |
| SUBM | Subordination of Mortgage | Mortgage agrees to be lower priority than another lien |
| SPRD | Mortgage Spreader Agreement | Extends an existing mortgage to cover additional properties |
| AL&R | Assignment of Leases and Rents | Lender gets rights to collect rents if borrower defaults |
| AALR | Assignment of Assignment of L&R | Assignment of an existing assignment of leases & rents |
| CERR | Certificate of Reduction | Certifies the remaining balance on a mortgage |
| PREL | Partial Release of Mortgage | Releases the mortgage lien from part of the property |
| REL | Release | General release of a lien or claim |
| DEMM | Declaration of Modification of Mortgage | Modifies mortgage terms (rate, maturity, etc.) without a new mortgage |
| AMTX | Additional Mortgage Tax | Payment of additional mortgage recording tax |
| WSAT | Withheld Satisfaction | Satisfaction is being withheld (dispute or administrative hold) |
| AGMT | Agreement | General agreement related to a mortgage |
| APPRT | Apportionment Order (Office Use) | Office use breakdown for apportioned mortgages |
| XXXX | Apportionment Breakdown (Office Use) | Office use only |

---

## 3. Other Documents

Miscellaneous recordings against property.

| Code | Name | What it means |
|------|------|---------------|
| RPTT | NYC Real Property Transfer Tax | NYC transfer tax filing on property sales |
| RETT | NYS Real Estate Transfer Tax | New York State transfer tax filing |
| RPTT&RET | Both RPTT and RETT | Combined NYC and NYS transfer tax filing |
| JUDG | Judgment | Court judgment recorded as a lien against the property |
| PAT | Power of Attorney | Authorizes someone to act on behalf of the property owner |
| RPAT | Revocation of Power of Attorney | Revokes a power of attorney |
| WILL | Certified Copy of Will | Certified copy of a will affecting the property |
| CTOR | Court Order | Court order affecting the property |
| MISC | Miscellaneous | Catch-all for documents that don't fit elsewhere |
| SMIS | Sundry Miscellaneous | Another catch-all category |
| SAGE | Sundry Agreement | General agreements recorded against the property |
| TLS | Tax Lien Sale Certificate | Property's tax debt was sold to a third party |
| ATL | Assignment of Tax Lien | Tax lien transferred to another party |
| AMTL | Amendment of Tax Lien | Amends an existing tax lien |
| DTL | Discharge of Tax Lien | Tax lien is discharged/released |
| LDMK | Landmark Designation | Property designated as a NYC landmark — restricts alterations |
| ZONE | Zoning Lot Description | Describes zoning lot boundaries (often for development) |
| MAPS | Maps | Survey or property maps |
| LOCC | Lien of Common Charges | Condo/co-op board files a lien for unpaid common charges |
| TOLCC | Termination of Lien of Common Charges | Releases a lien of common charges |
| ADEC | Amended Condo Declaration | Amendment to a condo declaration |
| TERDECL | Termination of Condo Declaration | Terminates a condo declaration |
| MERG | Merger | Merger of entities that hold property |
| CERT | Certificate | Various certificates recorded against property |
| DECL | Declaration | Various declarations recorded against property |
| CONS | Consent | Consent document (e.g., consent to mortgage) |
| RESO | Resolution | Corporate or board resolution affecting property |
| BOND | Bond | Debt instrument secured by property |
| LIC | License | License agreement affecting property |
| STP | Street Procedure | Related to street openings/closings |
| ASSTO | Assignment of Lease | Assignment of a lease to a new tenant |
| TERL | Termination of Lease or Memo | Terminates a lease or memorandum of lease |
| TERA | Termination of Agreement | Terminates a recorded agreement |
| TERT | Termination of Trust | Terminates a trust affecting property |
| TL&R | Termination of Assignment of L&R | Terminates an assignment of leases and rents |
| CALR | Cancel/Terminate Assignment L&R | Cancels an assignment of leases and rents |
| CORR | Correction Document (Office Use) | Office correction to a recorded document |
| ESRM | Estoppel Removal (Office Use) | Office use for removing estoppel notices |
| ESTL | Estoppel (Office Use) | Office use estoppel notice |
| RTXL | Release of Estate Tax Lien | Releases an estate tax lien |
| NTXL | Notice of Estate Tax Lien | Notice of an estate tax lien |

---

## 4. UCC and Federal Liens

Uniform Commercial Code filings (personal property/collateral) and federal tax liens.

| Code | Name | What it means |
|------|------|---------------|
| UCC1 | Uniform Commercial Code 1 | Initial UCC filing — creditor claims a security interest in personal property |
| INIT | Initial UCC1 | Same as UCC1 |
| INIC | Initial Coop UCC1 | UCC1 specifically for co-op share loans |
| UCC3 | Uniform Commercial Code 3 | Catch-all UCC amendment document |
| AMND | UCC3 Amendment | Amends an existing UCC filing |
| ASGN | UCC3 Assignment | Assigns a UCC filing to a new secured party |
| CONT | UCC3 Continuation | Extends a UCC filing (they expire after 5 years) |
| TERM | UCC3 Termination | Terminates a UCC filing — security interest released |
| RLSE | UCC3 Release/Amendment | Releases collateral from a UCC filing |
| PSGN | UCC3 Partial Assignment | Partially assigns a UCC filing |
| SUBO | UCC3 Subordination | UCC filing agrees to be lower priority |
| ASUM | UCC3 Assumption | New debtor assumes the UCC obligation |
| BRUP | UCC3 Bankruptcy | Bankruptcy-related UCC amendment |
| CORP | UCC5 Correction Statement | Debtor disputes a filed UCC — correction statement |
| UCC ADEN | UCC Cooperative Addendum | Addendum for co-op related UCC filings |
| FL | Federal Lien (IRS) | IRS files a lien for unpaid federal taxes |
| FTL | Federal Lien, Other | Non-IRS federal lien |
| RFL | Release of Federal Lien | Federal lien is released |
| RFTL | Release of Federal Tax Lien | Federal tax lien specifically released |
| CNFL | Continuation of Federal Lien | Extends a federal lien |
| AMFL | Amendment of Federal Lien | Amends a federal lien |
| PRFL | Partial Release of Federal Lien | Partially releases a federal lien |
| PWFL | Partial Withdrawal of Federal Lien | Partially withdraws a federal lien |
| WFL | Withdrawal of Federal Lien | Fully withdraws a federal lien |
| DPFTL | Discharge of Property from FTL | Removes a specific property from a federal tax lien |
| NAFTL | Certificate of Non-Attachment FTL | Certifies that a federal tax lien does not attach to this property |
| RCRFL | Revocation of Certificate of RFL | Revokes a certificate that released a federal lien |
| PRCFL | Partial Revocation of Cert RFL | Partially revokes a release certificate |
| NTXL | Notice of Estate Tax Lien | IRS notice of estate tax lien |
| RTXL | Release of Estate Tax Lien | Release of an estate tax lien |

---

## Most Common Documents

The documents you'll encounter most frequently are:

- **DEED** — property sales
- **MTGE** — new mortgages
- **ASST** — mortgage assignments (lender-to-lender transfers)
- **SAT** — mortgage payoffs
- **RPTT / RETT** — transfer tax filings (useful for sale price data)
- **UCC1 / INIT** — co-op and personal property financing

Together, these tell the story of a property: who bought it, how it was financed, when the mortgage was paid off or transferred, and what taxes were paid.
