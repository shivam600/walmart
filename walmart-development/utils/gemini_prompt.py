import os
import json

from dotenv import load_dotenv
from google import genai

load_dotenv()


def find_token(input_data, attributes, sop, response_text, prompt):

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "GEMINI_API_KEY not found in .env"

    analysis_prompt = f"""
You are a token usage analyzer.

Analyze the following API call components and estimate the token contribution of each section.

Return your answer as valid JSON only.

Input:

1. Prompt Template:
{prompt}

2. Input Data:
{input_data}

3. Attributes:
{attributes}

4. SOP:
{sop}

5. Model Response:
{response_text}

Output format:
{{
  "estimated_tokens": {{
    "prompt_template": 0,
    "input_data": 0,
    "attributes": 0,
    "sop": 0,
    "response": 0,
    "total_estimated": 0
  }},
  "largest_token_consumer": "",
  "optimization_suggestions": [
    ""
  ]
}}

Estimate tokens using the tokenizer behavior of Gemini 3.5 Flash Lite.
If exact token counts are unavailable, provide your best approximation.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=analysis_prompt,
    )

    return response

def gemini_prompt_validation(input_data, attributes, sop):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env")

    client = genai.Client(api_key=api_key)

    prompt = f"""
# ROLE
You are an expert E-Commerce Data Analyst, Multilingual Validation Engine, and Schema Curation Specialist. Your task is to predict, and validate product attributes against prefilled values, schema requirements, and an explicit Standard Operating Procedure (SOP) validation matrix.

---

# INPUT DATA SPECIFICATION
You will receive three input data structures:
1. `ITEM_DATA`: Contains product information keyed by `Product Type`. Core text fields include `Product Name`, `Product Short Description`, and `Product Long Description` (written in Spanish or English). Attribute fields begin at `Brand` and include prefilled values.
2. `PRODUCT_TYPE_SCHEMA`: Nested JSON keyed by attribute name. Defines data constraints (`data_type`, `closed_list`, `multiselect`, `acceptable_units`, `example_values`, `definition_es`, etc.).
3. `SOP_VALIDATION_RULES`: The reference document detailing validation scenarios (Table 1), error code assignments, and attribute-specific curation rules.

---

# CORE EXECUTION PIPELINE

### STEP 1: Language Parsing & Target Attribute Extraction
1. **Multilingual Processing:** Read `Product Name`, `Product Short Description`, and `Product Long Description`. Process Spanish/English text natively, translating terms where necessary to evaluate against English taxonomy schema definitions.
2. **Target Filtering:** 
   * Identify all attributes starting **from `Brand` onward** in the `ITEM_DATA`.
   * Ignore non-attribute metadata prior to `Brand` (e.g., `Submission ID`, `Product ID`, `Audit Template Version`).
   * Ignore attributes where the prefilled value is explicitly set to `"null"` or empty, UNLESS the SOP requires enriching missing values (Scenarios 11–13).
3. **Image Exclusions:** Image processing is currently disabled/out of scope. Ignore any image-related checks or instructions in the SOP and validate attributes using text sources only (`Product Name`, `Product Short Description`, `Product Long Description`).

### STEP 2: Schema Resolution & Spec-Wide Fallback
For each active target attribute:
1. Match the attribute name in `PRODUCT_TYPE_SCHEMA` where `level_4` or `product_type` aligns with the item's `Product Type`.
2. Extract rules: `data_type`, `closed_list` (`Yes`/`No`), `multiselect` (`Yes`/`No`), `acceptable_units`, and allowed value sets.
3. **Spec-Wide Fallback Rule:** If an attribute property (e.g., `acceptable_values`, `example_values`, `definition`) is blank or missing under the primary schema header, automatically retrieve and enforce the corresponding `spec_wide_*` header value (e.g., `spec_wide_example_values`).

### STEP 3: Post-Value Prediction (Curated Model Value)
1. Predict the true `post_filled_value` using facts derived **strictly** from `Product Name`, `Product Short Description`, and `Product Long Description`.
2. **Closed-List Enforcement:** If `closed_list` = `"Yes"`, the predicted value MUST strictly match an item from the allowed values list.
3. **Multi-Select Formatting:** If `multiselect` = `"Yes"` and multiple valid values exist, join them using a pipe separator (`|`) (e.g., `ValueA|ValueB`).

### STEP 4: SOP Table 1 Scenario Mapping & Error Code Assignment
Compare `prefilled_value` (Pre-Data) against predicted `post_filled_value` (Post-Data) and Base Text Data to assign the exact SOP comment and status:
*(Reference Mapping Table - actual execution relies on the user-provided runtime SOP text)*:
| Pre-Data | Post-Data | Base Text Data Condition | Validated? | Validation Comment |
| :--- | :--- | :--- | :--- | :--- |
| `A` | `A` | `A` present in Text without conflicts | `"Yes"` | `MODEL_MATCH_FROM_TEXT` |
| `A` | `B` | `B` present in Text (Model incorrect) | `"Yes"` | `INCORRECT_MODEL_VALUE_CURATED_FROM_TEXT` |
| `A` | `[Blank]` | `A` NOT present or conflicting in Text | `"No"` | `NOTFOUND_IN_BASEDATA` |
| `C` (Irrelevant) | `[Blank]` | Value irrelevant to attribute domain | `"No"` | `IRRELEVANT_MODEL_VALUE` |
| `C` (Irrelevant) | `A` | Irrelevant model value, but `A` in Text | `"Yes"` | `INCORRECT_MODEL_VALUE_CURATED_FROM_TEXT` |
| `NA/N/A/NULL` | `A` | Data missing in prefilled, but `A` in Text | `"Yes"` | `DATA_AVAILABLE_MODEL_MISSED_TO_CURATE_FROM_TEXT` |
| `A` | `A|B` | Model predicted 1+ correct values in multiselect | `"Yes"` | `PARTIAL_MODEL_MATCH_FROM_TEXT` |
| Invalid PT | `[Blank]` | Line item fails Product Type match | `"No"` | `INVALID_PT` |
| Marked SOP | `[Blank]` | SOP mandates "Do Not Validate" | `"No"` | `DO_NOT_VALIDATE_AS_PER_SOP` |

#### Error Code Rules:
* If the comment is `NOTFOUND_IN_BASEDATA` and prefilled data is missing/null, set `Error Code`: `"No value present"`.
* If text is in an unparseable or unsupported language (outside Spanish/English), set `Validated?`: `"No"`, `Validation Comment`: `"NOTFOUND_IN_BASEDATA"`, and `Error Code`: `"Other language"`.
* In all other valid matching or curated scenarios, set `Error Code`: `""` (empty string).

---

# ATTRIBUTE-SPECIFIC OVERRIDE RULES

1. **Brand:** If present in base text data, set `MODEL_MATCH_FROM_TEXT`.
2. **Color:** MUST be derived strictly from text. **NEVER** extract or guess color from images. If absent in text, mark as `NOTFOUND_IN_BASEDATA`.
3. **Piece Count / Count per Pack:** Must be explicitly stated in text (`Product Name`, `Short Description`, `Long Description`).
4. **Dimensions:** Match Length, Width, and Height (LWH) in standard units (in/cm) with UOMs attached. Do not use approximate or "about" values.
5. **Tire Attributes:**
   * *Radial (e.g., 205/55R17):* 205 = Tire Width (mm), 55 = Aspect Ratio, R = Radial, 17 = Wheel Diameter (in).
   * *Flotation (e.g., 25x8-12):* 25 = Tire Diameter (in), 8 = Tire Width (in), 12 = Wheel Diameter (in).
6. **Gender & Age Group:** 
   * Do NOT classify "Kids" as Unisex unless explicitly stated as both "boy" and "girl" or "Unisex".
   * Terms like "kids", "girl", or "boy" alone are too generic for Age Group -> `NOTFOUND_IN_BASEDATA`.
7. **Character:** Do not accept generic animal names (e.g., "Horse", "Cat", "Dog") as valid character attributes.
8. **Boolean Attributes ("Yes"/"No"):** If unable to verify strictly from text, set `NOTFOUND_IN_BASEDATA` even if a prefilled value exists.

---

# STRICT ANTI-HALLUCINATION GUARDRAILS
1. **Fact-Based Extraction Only:** Base all post-filled predictions strictly on facts explicitly present in the provided Spanish/English descriptions. Do not assume, extrapolate, or use general internet knowledge.
2. **Conflicting Data:** If descriptions contain contradictory statements for an attribute, reject the prediction, set `Validated?`: `"No"`, and set `Validation Comment`: `"NOTFOUND_IN_BASEDATA"`.
3. **Strict JSON Output:** Output ONLY valid JSON formatted as specified. No markdown narrative or extra text outside the JSON object.

---

# OUTPUT FORMAT SCHEMA

Return a nested JSON object where each root key is an `Item ID`. Inside each item, generate the three required output fields for every active attribute validated, it should contain all attributes starting from `Brand` onward, with the following structure:

```json
{{
  "<ITEM_ID>": {{
    "<ATTRIBUTE_NAME> Validated?": "Yes | No",
    "<ATTRIBUTE_NAME> Error Code": "<ERROR_CODE_STRING_OR_EMPTY>",
    "<ATTRIBUTE_NAME> Validation Comment": "<EXACT_SOP_VALIDATION_COMMENT>"
  }}
}}
FEW-SHOT EXAMPLE
INPUT:
ITEM_DATA:

JSON
{{
  "Speaker Mounts & Brackets": [
    {{
      "Item ID": "15015660979_2818f4a6d58b4431360481e9479dfc9b1dceba1e79f35f05ca2b59207dd87cd7",
      "Product Type": "Speaker Mounts & Brackets",
      "Product Name": "Soportes para Bocinas de Piso, Premium JBL JS120",
      "Product Short Description": "El accesorio JS-120 se coloca en el suelo para elevar e inclinar tus bocinas y obtener un rendimiento óptimo.",
      "Product Long Description": "Construcción de metal con acabado en negro. Ángulo de inclinación hacia atrás de 7 grados. Compatible con modelos JBL L100, L100A, y BOSE.",
      "Brand": "JBL",
      "Tilt Angle": "7",
      "Compatible Brands": "JBL",
      "Color": "Blue"
    }}
  ]
}}
PRODUCT_TYPE_SCHEMA:

JSON
{{
  "Tilt Angle": {{
    "product_type": "Speaker Mounts & Brackets",
    "attribute": "Tilt Angle",
    "data_type": "Integer",
    "acceptable_units": "º",
    "definition_es": "El ángulo al que se inclina el artículo, generalmente medido en grados."
  }},
  "Compatible Brands": {{
    "product_type": "Speaker Mounts & Brackets",
    "attribute": "Compatible Brands",
    "multiselect": "Yes",
    "example_values": "BOSE;JBL;Logitech;Sony"
  }},
  "Color": {{
    "product_type": "Speaker Mounts & Brackets",
    "attribute": "Color",
    "closed_list": "No"
  }}
}}
OUTPUT:
JSON
{{
  "15015660979_2818f4a6d58b4431360481e9479dfc9b1dceba1e79f35f05ca2b59207dd87cd7": {{
    "Brand Validated?": "Yes",
    "Brand Error Code": "",
    "Brand Validation Comment": "MODEL_MATCH_FROM_TEXT",
    "Tilt Angle Validated?": "Yes",
    "Tilt Angle Error Code": "",
    "Tilt Angle Validation Comment": "MODEL_MATCH_FROM_TEXT",
    "Compatible Brands Validated?": "Yes",
    "Compatible Brands Error Code": "",
    "Compatible Brands Validation Comment": "PARTIAL_MODEL_MATCH_FROM_TEXT",
    "Color Validated?": "Yes",
    "Color Error Code": "",
    "Color Validation Comment": "INCORRECT_MODEL_VALUE_CURATED_FROM_TEXT"
  }}
}}

## INPUT_DATA

{input_data}

---

## PRODUCT_TYPE_SCHEMA

{attributes}

---

## SOP_VALIDATION_RULES

{sop}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )

    token = find_token(input_data , attributes, sop , response.text , prompt)
    print(response)

    return response