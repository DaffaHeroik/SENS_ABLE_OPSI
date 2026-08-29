# Key Findings for SENS-Able OPSI Stage 2 Recheck

## Shared ChatGPT Discussion

The shared discussion recommends treating the project as a staged data-collection and experimentation pipeline rather than claiming final AI accuracy too early. It explicitly suggests using `GlukosaRef` as the target for a regression workflow, comparing models such as linear regression, random forest, and gradient boosting, and evaluating them with cross-validation rather than a single train/test split when the dataset is still very small.

The discussion also emphasizes that early datasets such as 13 rows are useful for pipeline validation, not for final performance claims. It recommends incremental dataset growth, preserving old records unless measurement errors are confirmed, and retraining versions of the model as the dataset expands from 13 to 20, 30, 40, and beyond.

## Stage 1 OPSI PDF — Pages 1 to 5

Page 1 shows the project identity clearly: **SENS-Able: Smart Health Monitor Inklusif berbasis AI dengan Audio, Visual dan Vibrasi yang Ramah Bagi Pengguna Disabilitas**, by AntroOptic Team from MAN 2 Kota Bima, for the field of smart measurement and monitoring systems.

Pages 2 to 4 indicate the proposal structure: introduction, literature review, methods, budget and schedule, references, and appendices. This suggests Stage 2 materials will likely need a more complete research narrative rather than only code or hardware screenshots.

Page 5 states the background in terms of chronic disease monitoring, diabetes and cardiovascular risk, accessibility for users with visual/hearing impairments, and the role of AI/TinyML-assisted health monitoring. The framing is strong for a competition report, but it will require cautious wording so that the final report does not overclaim medical accuracy without sufficient calibration and validation evidence.

## Stage 1 OPSI PDF — Pages 6 to 10

Pages 6 to 8 confirm the formal Stage 1 research design. The proposal uses an experimental quantitative approach combined with user-centered design. It proposes calibration against a **glucometer, pulse oximeter, and digital thermometer**, followed by testing on **15 respondents** across disability groups, observation of use, and a Likert usability questionnaire. The original success indicators are very ambitious: **MAE heart rate < 3 bpm, temperature < 0.3°C, glucose < 15 mg/dL, questionnaire mean ≥ 4, and ≥ 80% independent usage after one demonstration**.

Pages 8 to 10 also show the original timeline and budget. The proposal expected data collection and analysis to finish much earlier in the year, which means the current Stage 2 plan must acknowledge schedule slippage and focus only on what can still be demonstrated credibly by 31 August.

The flowchart on page 10 aligns with the current project architecture: data acquisition from sensors, TinyML/analysis on ESP32, multimodal outputs, and local storage. However, the proposal text states that data processing uses Arduino IDE, which is too weak as a Stage 2 scientific analysis description; the updated plan should instead use a clearer pipeline with dataset preparation, cleaning, model validation, and explicit evaluation metrics in Python.

## Official OPSI SMA Sederajat 2026 Guide

Source: https://pusatprestasinasional.kemendikdasmen.go.id/uploads/lampiran_pengumuman/Panduan%20OPSI%20SMA%20Sederajat%202026.pdf, accessed 26 August 2026.

The official guide states that final assessment is based on the final report, exhibition, presentation/interview, and Research Idea Challenge. The weights are: report 30%, exhibition 10%, presentation and interview 50%, and Research Idea Challenge 10% (official guide lines 771–788 in the extracted text).

The exhibition requires a poster/infographic, source attribution for images, OPSI logo, participant code, title, researchers, and school information. A physical product must be brought if the research produces one (lines 791–811).

The presentation is in Indonesian, with 10 minutes for presentation and 15 minutes for questions. PPT must be uploaded no later than one day before the final, by 23:59 WIB, with a maximum capacity of 20 MB (lines 815–833).

The guide requires research ethics principles including honesty, integrity, privacy, confidentiality, transparency, respect, and justice. Research involving humans must obtain ethical eligibility/clearance before the research is conducted, with safety prioritized over benefit (lines 916–939).

The guide limits similarity to a maximum of 30% and states that AI may be used only in a limited way for references, understanding the topic, and brainstorming. The proposal/report text and substantive analysis/results must be the participants' own work, and AI use must be declared (lines 945–995).

The official report structure includes cover, abstract, contents, tables/figures, introduction, theory/literature, methods, results and discussion, budget and activities, conclusions/recommendations, and references (lines 1047–1074).

## Official OPSI 2026 Schedule and Stage 2 Requirements

The official guide confirms that research execution for approved proposals runs April–August 2026 and that the deadline for uploading the research report is **31 August 2026**. Report evaluation is scheduled for 3–11 September, finalists are announced 13 September, and the final event is scheduled for 24–30 September 2026 (official guide lines 536–561).

The Stage 2 upload consists of a research report of maximum 20 pages excluding appendices, the research logbook, and ethical clearance if required. The report PDF may be at most 8 MB (lines 692–701). Report scoring is weighted toward results and discussion (30%), methodology (20%), introduction (10%), conclusions/recommendations (10%), references (10%), novelty (10%), and usefulness/impact (10%) (lines 705–741).

Because the study involves human respondents and health measurements, the official guide requires ethical clearance or the appropriate written eligibility from an authorized ethics institution before research implementation, and it requires a school introduction letter plus respondent name/contact data for respondents used in the study (lines 592–612 and 671–686). The report must also be the students' own writing and analysis; AI use is limited and must be declared (lines 984–995).
