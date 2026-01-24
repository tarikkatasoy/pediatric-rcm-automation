# Pediatric Associates - Master Billing Reference


## SECTION 1: Master Code Lookup Table
*Direct reference for high-precision automated coding.*


| Category | ICD-10 Code | Description |
| :--- | :--- | :--- |
| Ear Infection (Right) | **H66.001** | Acute suppurative otitis media, right ear |
| Ear Infection (Left) | **H66.002** | Acute suppurative otitis media, left ear |
| Ear Infection (Bilateral) | **H66.003** | Acute suppurative otitis media, bilateral |
| Asthma Exacerbation | **J45.51** | Severe persistent asthma with acute exacerbation |
| Strep Throat | **J02.0** | Streptococcal pharyngitis |
| Well-Child Exam | **Z00.129** | Routine child health exam without abnormal findings |
| Viral Conjunctivitis | **B30.9** | Viral conjunctivitis, unspecified |
| Acute Conjunctivitis | **H10.33** | Unspecified acute conjunctivitis, bilateral |
| Acute Bronchiolitis | **J21.0** | Acute bronchiolitis due to RSV |


| Service / Procedure | CPT Code | Description |
| :--- | :--- | :--- |
| Office Visit (Minimal) | **99212** | Straightforward/minimal complexity |
| Office Visit (Low-Mod) | **99213** | Low-to-moderate complexity |
| Office Visit (Mod-High) | **99214** | Moderate-to-high complexity |
| Nebulizer Treatment | **94640** | Inhalation treatment for airway obstruction |
| Rapid Strep Test | **87880** | Infectious agent antigen detection |
| Preventive (Age 1-4) | **99392** | Periodic preventive medicine (1-4 years) |
| Preventive (Age 5-11) | **99393** | Periodic preventive medicine (5-11 years) |


---


## SECTION 2: Clinical Decision Scenarios
*Contextual rules for Clinical Entity Extraction and confidence scoring.*


### Scenario 1: Acute Otitis Media (Ear Infection)
- **Clinical Indicators:** Ear pain, fever, red/bulging tympanic membrane, tugging at ear.
- **Decision Rule:** Must verify laterality (R/L/B) to select correct ICD-10. Map to CPT 99213.


### Scenario 2: Asthma Exacerbation (Asthma Attack)
- **Clinical Indicators:** Shortness of breath, wheezing, rescue inhaler, subcostal retractions.
- **Decision Rule:** Code J45.51. If nebulizer is administered, MUST bundle with CPT 94640. Map to CPT 99214.


### Scenario 3: Strep Throat (Bacterial Pharyngitis)
- **Clinical Indicators:** Sore throat, difficulty swallowing, white exudates, swollen lymph nodes.
- **Decision Rule:** Code J02.0. Map to CPT 99213. Include 87880 if antigen test performed.


### Scenario 4: Well-Child Visit (Preventive Care)
- **Clinical Indicators:** Routine exam, growth monitoring, developmental screening, no acute illness.
- **Decision Rule:** Use ICD-10 code Z00.129. CPT selection depends strictly on patient age:
 - Age 1-4: Map to CPT 99392.
 - Age 5-11: Map to CPT 99393.
- **Validation Rule:** Agent MUST verify patient age by comparing 'Date of Birth' with the 'Date of Service'. If age is exactly 5 years, the logic must default to 99393 to avoid insurance denials.


### Scenario 5: Viral Conjunctivitis (Pink Eye)
- **Clinical Indicators:** Redness, watery discharge, morning crusting, itching.
- **Decision Rule:** Use B30.9 or H10.33 (bilateral). Map to CPT 99212.


### Scenario 6: Acute Bronchiolitis (RSV)
- **Clinical Indicators:** Cough, wheezing, tachypnea in infants, positive RSV swab.
- **Decision Rule:** Use J21.0. Map to CPT 99214 due to high management complexity.

