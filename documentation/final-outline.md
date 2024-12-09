# Title: Augmented Knowledge Base Creation and Curation using Large Language Models: A Proof-of-Concept Implementation

## I. Introduction

### General Problem Statement.

- Organizations struggle to efficiently extract, organize, and utilize knowledge from their unstructured textual data. This challenge encompasses:
  - Information Overload
    - the volume of documents and data within organizations is growing exponentially. (Taylor, P, 2023, Gartner, 2023)
  - Knowledge Silos
    - important information is often scattered across different departments, systems, versions, documents (Deloitte, 2020)
  - Manual Curation
    - traditional methods of knowledge organization rely heavily on manual effort (Chui, M. et al., 2012)
  - Lack of Standardization
    - challenging to integrate information from diverse sources (AIIM, 2023)
  - Rapid Obsolescence
    - knowledge can quickly become outdated, requiring constant updates (Tamayo, et al., 2023)
  - Domain Specificity
    - each organization or industry has its own specialized vocabulary and concepts solutions (Otero, et al., 2015)
  - Accessibility
    - even when knowledge is properly organized, it may not be easily accessible (Cross, et al., 2004)
  - Scalability
    - knowledge management systems often struggle to keep pace with growth (Heisig, et al., 2016)

### Background on LLMs and Knowledge Management

- Evolution and challenges of knowledge management systems
  - Historical reliance on manual curation
    - From Assignment 1: "Manual curation has been expensive and time-consuming. According to Karp (2016), the high costs associated with manual curation of knowledge bases make alternative strategies necessary, though these may result in lower quality knowledge."
  - Growing inefficiencies in traditional approaches
    - From Assignment 3: "Workers spend 19% of their time searching for and gathering information" (Chui et al., 2012)
    - "55% of organizations report that knowledge silos are a significant barrier to effective decision-making" (Deloitte, 2020)
  - Scale and complexity challenges
    - From Assignment 3: "A study of 179 multinational corporations found that as organizations grew in size and complexity, the effectiveness of their knowledge management systems decreased. Specifically, companies with over 10,000 employees reported a 23% lower satisfaction rate with their knowledge management systems compared to smaller firms" (Heisig et al., 2016)
- Emergence of LLMs as powerful text processing tools
  - From Assignment 2: "Pre-LLM era research predominantly pointed towards transformer-based BERT models for knowledge extraction tasks. What I'm seeing in this research is that the future lies in leveraging existing LLMs, especially those provided by major providers such as OpenAI, Anthropic, and Google."
  - Can cite: Caufield et al. (2024) "SPIRES: A method for populating knowledge bases using zero-shot learning"
- Current approaches to LLM-based knowledge extraction
  - From Assignment 1: "The integration of large language models (LLMs) into natural language processing techniques has revolutionized knowledge extraction and ontology development."
  - Can cite: Babaei Giglou et al. (2023) "LLMs4OL: Large language models for ontology learning"
  - Can cite: Wan et al. (2023) regarding in-context learning for relation extraction
- Challenges in leveraging LLMs effectively
  - From Assignment 3: "The challenge lies in developing efficient, accurate, and scalable methods to extract knowledge from diverse document sources, map this knowledge to existing ontologies, and present it in a form that is useful for non-expert users."
- Context limitations
  - Can cite: Wang et al. (2023) "GPT-NER: Named Entity Recognition via Large Language Models"
- Hallucination issues
  -Can cite: Bikeyev (2023) "Synthetic ontologies: A hypothesis"

### Overview of Proposed Solution

- Introduction to the Chelle Knowledge Model (CKM)

  - Mission Statement: "Chelle streamlines internal training, leading to field engineers who are continually up-to-date with company technicals, managers that are freed from creating training curricula and curating documentation, and teams that are empowered with a unified, easily accessible source of truth."
  - Foundation: "As both a working engineer and student and teacher of applied mathematics, I have a particular interest in the development of best practices and rigor in software engineering. This is especially important working with extremely complicated systems, such as are required to deploy machine learning and artificial intelligence applications." (Matentzoglu et al., 2023)

- System Architecture for Knowledge Processing

  - Core Components:
    - Knowledge Extractor Application
    - Document Processing Models:
      - Document Entity Extractor
      - Document Relation Extractor
      - Document Ontology Mapper
  - Relevant Papers:
    - "SPIRES: A method for populating knowledge bases using zero-shot learning" (Caufield et al., 2024)
    - "MapperGPT: Large language models for linking and mapping entities" (Matentzoglu et al., 2023)

- Integration of LLMs with Structured Knowledge Models

  - Core Approach: "Our current research and development efforts center on leveraging large language models and advanced natural language processing techniques to efficiently extract, organize, and utilize knowledge from unstructured textual data, with the goal of augmenting the creation of knowledge bases for internal training and information management."
  - Relevant Papers:
    - "LLMs4OL: Large language models for ontology learning" (Babaei Giglou et al., 2023)
    - "ChatIE: Zero-Shot Information Extraction via Chatting with ChatGPT" (Wei et al., 2024)

- Human-in-the-Loop Validation Approach

  - Trust Building: "If we are going to create robust, self-updating knowledge bases... if we are going to take this out of the hands of our users or at a minimum significantly augment their workflows, then we will need to engender trust."
  - Relevant Paper: "Curating a domain ontology for rework in construction: challenges and learnings from practice" (Matthews et al., 2023)

- Scalable Processing Pipeline

  - Foundation: "Based this research analysis and internal discussions, it seems as though establishing an ontology is a fundamental first step... This ontology provides a structured framework for organizing and concepts extracted from raw source documents."
  - Relevant Papers:
    - "A Simple Standard for Sharing Ontological Mappings (SSSOM)" (Matentzoglu et al., 2022)
    - "Ontology Development Kit: a toolkit for building, maintaining and standardizing biomedical ontologies" (Matentzoglu et al., 2022)

### Contributions

- Novel approach to structuring LLM interactions using CKM

  - From Assignment 1: "My research so far has led to three primary processes or AI agents that are critical to knowledge extraction: entity extraction, entity relation, and ontology mapping. These components will work together to create ontologies for each of our customer organizations."
  - Could cite: Matentzoglu et al. (2023) "MapperGPT: Large language models for linking and mapping entities"

- Proof-of-concept implementation demonstrating feasibility

  - From Assignment 3: "I believe the system I will be developing here in addition to the product that I am working on with my startup, that we can tackle these: Rapid skill obsolescence, Domain-specific knowledge and vocabulary, Manual curation"
  - Could cite: Caufield et al. (2024) "SPIRES: A method for populating knowledge bases using zero-shot learning"

- Insights into practical challenges of LLM-based knowledge processing

  - From Assignment 2: "My takeaway: The more I read about Bert the more I think we should stick to the approach of not using transformers, we are a small team we should focus on delivering value which can be done most efficiently using prompting"
  - From Assignment 3: "While it is easy to get carried away with excitement, it is also critical that we develop evaluation methodologies to assess the accuracy and reliability of these techniques."

- Framework for context-aware knowledge extraction

  - From Assignment 1: "We will also maintain a set of public ontologies that can be broadly leveraged."
  - Could cite: Qiang et al. (2025) "Agent-OM: Leveraging LLM Agents for Ontology Matching"

- Architectural patterns for scalable knowledge processing
  - From Assignment 2: "All of the modern research (last two years), Sees a paradigm shift from traditional NLP to Large Language Model (LLM) based approaches."
  - From Assignment 3: "The IEF combines quantitative metrics with qualitative insights, especially human-in-the-loop user input, and measurement of this input."
  - Could cite: Wei et al. (2024) "ChatIE: Zero-Shot Information Extraction via Chatting with ChatGPT"

## II. The Chelle Knowledge Model (CKM)

### Overview and Motivation

- **Limitations of Traditional Knowledge Bases**  
  Traditional knowledge bases often fail to manage and preserve context effectively, leading to inefficiencies in knowledge extraction and application.

  - **Knowledge Silos**: Important information is scattered across different systems and departments.
    - Example: "Important information is often scattered across different departments, systems, versions, documents" (Assignment 2).
  - **Disconnected Systems**: According to AIIM (2023), "74% of content systems are not connected to other business systems."

- **Dynamic Nature of Knowledge**  
  The meaning of knowledge and its relationships evolve with context, necessitating a formal framework for preserving semantic integrity.

  - "The rapid growth of scientific literature outpaces manual curation efforts" (Caufield et al., 2024).
  - Chelle addresses this by combining ontological mapping with knowledge extraction from raw documents.

- **Role of LLMs**  
  LLMs provide context-sensitive processing but require structured frameworks for reliability and semantic consistency.
  - "LLMs have revolutionized knowledge extraction and ontology development" (Assignment 3).

### Comparison with Existing Approaches

- **Traditional Retrieval-Augmented Generation (RAG) Approaches**  
  RAG methods prioritize source grounding for reliability but may lack robust ontological mapping.

  - "Source grounding is important, but ontological mapping should take precedence for foundational structure" (Assignment 1).

- **Direct KM-LLM Integration**  
  Emerging methods like SPIRES leverage LLMs for zero-shot learning, enabling schema-driven knowledge base population.

  - "LLMs for zero-shot learning automatically populate knowledge bases using predefined schemas" (Caufield et al., 2024).

- **Unique Differentiators in CKM**  
  CKM distinguishes itself by integrating high-recall methods with LLM-driven refinement.
  - Example: MapperGPT combines "existing high-recall methods for candidate mappings with LLMs to refine these mappings" (Matentzoglu et al., 2023).

### Design Principles

Core principles for CKM include:

1. **Explicit Context Tracking and Versioning**

   - CKM adopts robust tracking mechanisms inspired by frameworks like **LinkML**, which simplifies the production of FAIR ontology-ready data (Moxon et al., 2021).

2. **Preservation of Core Concept Definitions**

   - Tools like the **Ontology Development Kit (ODK)** provide standardized workflows for maintaining concept integrity (Matentzoglu et al., 2022).

3. **Formal Relationship Modeling Across Contexts**

   - CKM aligns with SSSOM standards for sharing ontological mappings and ensuring semantic integrity (Matentzoglu et al., 2022).

4. **Trust Building through Human-in-the-Loop Validation**
   - As CKM automates workflows, trust is engendered through transparency and user collaboration.
     - "To create robust, self-updating knowledge bases, trust is essential" (Assignment 3).

### Core Components

1. **Knowledge Representation**  
   CKM structures knowledge into assets, assessments, and instructional frameworks, as highlighted in your differentiation:

   - "Assets, Knowledge, Assessment, Instruction" (Assignment 1).

2. **Context Framework**  
   The model addresses the exponential growth in organizational knowledge systems and repositories.

   - "Organizations using multiple information systems have seen 100% growth every five years" (Assignment 2).

3. **Integration Layer**  
   CKM integrates advanced LLM-NLP techniques for seamless processing, leveraging:
   - **ChatIE Framework** (Wei et al., 2024).
   - **SPIRES Method** (Caufield et al., 2024).
   - **MapperGPT Approach** (Matentzoglu et al., 2023).

### Case Study: "Basis" in Linear Algebra

Demonstrates how CKM manages evolving concept understanding:

1. Base Definition:

   - Mathematical definition: linearly independent vectors spanning vector space
   - Core properties: independence, spanning, uniqueness

2. Context Evolution:

   - Week 5: Building intuition via random vectors
   - Week 7: Application to Central Limit Theorem
   - Context inheritance: maintains core definition while adding domain relevance

3. Validation Mechanisms:
   - Core property preservation
   - Context-specific relationship validation
   - Dependency tracking across context changes

This case study shows CKM's ability to:

- Maintain semantic consistency
- Support natural knowledge evolution
- Preserve relationships across contexts
- Guide LLM interactions systematically

## III. Knowledge Processing Pipeline

**Note: detailed description of system architecture is in the README.md file**

## Document Processing Pipeline for Knowledge Model Implementation

The following describes a technical implementation of the knowledge model based on the provided diagram and document content. Each phase of the implementation integrates principles from the document, aligning processes with the outlined layers (conceptual, operational, and relationship layers).

---

### 1. Document Processing

This phase processes the raw input documents, identifying and classifying context to support downstream operations. The operations align with the **"Raw Asset"** and **"Refined Asset"** concepts from the knowledge model.

#### Initial Context Classification

- **Domain Identification**: Categorize the document domain using predefined lexemes, as described in the **"Lexeme"** and **"Asset Metadata"** sections.
- **Audience Level Detection**: Identify the audience's level of expertise (basic, intermediate, mastery) as defined in the **"Understanding Levels"**.
- **Prerequisite Mapping**: Map necessary prior knowledge using **"Knowledge Dependencies"** and **"Definitional Dependencies"**.
- **Teaching Sequence Position**: Determine the document’s position within the learning path using the **"Learning Path"** concept.

---

### 2. Knowledge Extraction

This phase extracts meaningful knowledge elements from the document, leveraging **"Knowledge Structure"** and **"Concept"** principles.

#### Context-Aware Lexeme Identification

- Extract lexemes and classify them as **"Primitive Terms"** or **"Composite Terms"**, ensuring all lexemes are computably verifiable.

#### Relationship Detection Within Context

- Detect relationships between extracted lexemes, adhering to the **"Relationship Uniqueness Rule"**, ensuring one explicit relationship between any two concepts.

#### Cross-Context Relationship Mapping

- Map relationships across different document contexts using **"Cross-Reference Rules"** and validate with **"Relationship Strength Calculations"**.

#### Context Transition Detection

- Identify transitions between contexts, such as from **"Definitional Dependency"** to **"Knowledge Dependency"**, maintaining consistency.

#### Validation Against CKM Rules

- Validate extracted knowledge and relationships against the **"Completeness Rule"**, ensuring no circular dependencies.

---

### 3. Context Management

This phase organizes and manages the context extracted from documents.

#### Context Hierarchy Construction

- Construct a hierarchy of contexts using **"Subsumption"** and **"Relationship Hierarchy"** principles.
  - Define **inheritance relationships** to track properties passed between contexts.
  - Manage **context transitions** and track **dependencies** across contexts.

#### Version Management

- Implement version control for context elements, ensuring compliance with the **"Versioning Rules"** of the knowledge model.

---

### 4. Storage Architecture

This phase involves designing a storage system that preserves contextual integrity.

#### Context-Preserving Schema Design

- Design schemas for storing **"Concepts"**, **"Relationships"**, and **"Mentions"**, ensuring **referential integrity**.

#### Context-Based Indexing

- Create indices for efficient retrieval of knowledge by context, leveraging **"Context Transition Rules"**.

#### Relationship Preservation

- Preserve the **"Relationship Types"** (e.g., overlap, subsumption) within the storage layer, ensuring hierarchy consistency.

#### Change Tracking Across Contexts

- Track changes across contexts using **"Operational Layer Validation"** processes.

#### Version Control Implementation

- Implement version control for all stored elements to maintain provenance, as detailed in **"Refined Asset"** validation rules.

---

### 5. Human-in-the-Loop Validation

This phase ensures accuracy and quality through human oversight, complementing automated processes.

#### Context Appropriateness Verification

- Validate the appropriateness of extracted contexts against predefined **"Knowledge Structure"** requirements.

#### Relationship Validation

- Confirm all relationships adhere to **"Validation Rules"**, ensuring mutual exclusivity and logical consistency.

#### Context Transition Review

- Review transitions between contexts to ensure **"Dependency Validation"** rules are followed.

#### Knowledge Evolution Approval

- Approve changes in knowledge elements based on the **"Validation Phase"** requirements.

#### Quality Metrics by Context

- Assess quality metrics for each context using the **"Relationship Strength Calculations"**.

---

### Visual Representation

The following `mermaid` diagram provides a visual representation of the processing pipeline:

```mermaid
graph TD
    subgraph Input
        Doc[Document Upload]
        Meta[Metadata Extraction]
    end

    subgraph Lexeme
        LE[Lexeme Extraction]
        LC[Lexeme Classification]
        LV[Lexeme Validation]
    end

    subgraph Concept
        CD[Concept Definition]
        CR[Concept Relations]
        CC[Citation Creation]
    end

    subgraph Storage
        KB[(Knowledge Base)]
        Cache[(Cache Layer)]
    end

    subgraph Validation
        VQ[Validation Queue]
        UI[User Interface]
        FB[Feedback Loop]
    end

    Doc --> Meta
    Meta --> LE
    LE --> LC --> LV
    LV --> CD --> CR --> CC
    CC --> KB
    KB <--> Cache
    KB --> VQ --> UI --> FB
    FB --> KB

    classDef process fill:#f9f,stroke:#333,stroke-width:2px
    classDef storage fill:#bbf,stroke:#333,stroke-width:2px
    classDef validation fill:#bfb,stroke:#333,stroke-width:2px
    class LE,LC,LV,CD,CR,CC process
    class KB,Cache storage
    class VQ,UI,FB validation
```

## V. Discussion

The implementation of the knowledge processing pipeline demonstrated both promising results and revealed important technical challenges that impact system scalability. While core functionality was successfully implemented and performed well, several key insights emerged during development.

### Implementation Progress and Challenges

The core system functionality was successfully implemented and demonstrated effective performance. However, a significant scalability challenge emerged when processing rich documents containing numerous concepts. This bottleneck led to exploring two distinct solution paths:

1. Initial attempts focused on load balancing the API server to better utilize system resources
2. Subsequently, attention shifted to worker load balancing, which proved to be the correct approach but required substantial code refactoring

This technical challenge and the resulting implementation iterations consumed significant development time, limiting the scope of implemented features. While concept extraction was successfully implemented, relationship extraction functionality remained unimplemented due to time constraints.

### Preliminary Results

Initial results from concept extraction and definition were promising, based on ad hoc analysis of system logs. The LLM-based approach demonstrated effectiveness in identifying and defining concepts from input documents. However, it should be noted that due to development focusing on core functionality, the system's output capture mechanisms were not implemented in a way that would support rigorous research validation and presentation.

### Time Constraints and Future Work

The primary limiting factor in this implementation was time rather than fundamental issues with the system architecture or approach. The underlying architectural decisions appear sound based on the implemented components' performance. Development of the system will continue, with particular focus on:

1. Completing the relationship extraction functionality
2. Implementing robust output capture for proper evaluation
3. Leveraging the refactored worker load balancing system for improved scalability

The successful implementation of core functionality, despite scalability challenges, supports the viability of the overall architectural approach. Future work will build upon these foundations to realize the full potential of the system.

## VI.Conclusion

### Transformative Potential of Automated Ontology Creation

The most significant insight from this research is not merely the automation of ontology creation through LLMs, but rather how this automation fundamentally transforms the role of ontologies in knowledge management. When ontology creation shifts from a months-long expert endeavor to a rapid, iterative process, it enables ontologies to be deployed for previously impractical use cases - much like how the accessibility of databases or notebooks has enabled their widespread adoption in diverse contexts.

### Implementation Insights

While the proof-of-concept implementation faced expected challenges in scaling complex machine learning systems, these challenges proved to be primarily engineering hurdles rather than fundamental limitations. The core functionality demonstrated the viability of the architectural approach, particularly in concept extraction and definition, though full relationship extraction capabilities remain to be implemented.

### Practical Applications

The immediate practical application of this work focuses on educational contexts, specifically facilitating connections between students, teachers, and knowledge resources. This narrow but concrete focus provides a clear path for validating the approach while avoiding overextension of the system's capabilities.

### Future Work

Two critical areas require attention for advancing this work:

1. Development of robust validation methodologies to empirically demonstrate the effectiveness of automatically generated ontologies
2. Continued refinement of the engineering infrastructure to support scalable deployment of these systems

The successful implementation of core functionality, despite various technical challenges, supports the fundamental viability of using LLMs to transform knowledge management through rapid ontology creation and deployment. While significant work remains, particularly in validation and scaling, the potential to fundamentally change how organizations approach knowledge structuring and management appears promising.

## Appendix

Association for Intelligent Information Management (AIIM). (2023, April 20). _2023 State of the Intelligent Information Management Industry_. AIIM. https://www.aiim.org/industrywatch2023
Chui, M., Manyika, J., Bughin, J., Dobbs, R., Roxburgh, C., Sarrazin, H., Sands, G., & Westergren, M. (2012, July 1). _The social economy: Unlocking value and productivity through social technologies_. McKinsey Global Institute. https://www.mckinsey.com
Cross, R., & Sproull, L. (2004). More than an answer: Information relationships for actionable knowledge. Organization science, 15(4), 446-462.
Deloitte. (2020). _2020 Deloitte Global Human Capital Trends: The social enterprise at work: Paradox as a path forward_. Deloitte Development LLC. https://www2.deloitte.com/content/dam/Deloitte/us/Documents/human-capital/us-2020-deloitte-global-human-capital-trends.pdf
Gartner, Inc. (2023, May 10). _Gartner survey reveals 47% of digital workers struggle to find the information needed to effectively perform their jobs_. https://www.gartner.com/en/newsroom/press-releases/2023-05-10-gartner-survey-reveals-47-percent-of-digital-workers-struggle-to-find-the-information-needed-to-effectively-perform-their-jobs
Heisig, P., Suraj, O. A., Kianto, A., Kemboi, C., Perez Arrau, G., & Fathi Easa, N. (2016). Knowledge management and business performance: global experts’ views on future research needs. Journal of Knowledge Management, 20(6), 1169-1198.
Otero-Cerdeira, L., Rodríguez-Martínez, F. J., & Gómez-Rodríguez, A. (2015). Ontology matching: A literature review. Expert Systems with Applications, 42(2), 949-971.
Tamayo, J., Doumi, L., Goel, S., Kovács-Ondrejkovic, O., & Sadun, R. (2023). Reskilling in the age of AI: Five new paradigms for leaders—and employees. _Harvard Business Review_, 101(5), 86–95. https://hbr.org/2023/09/reskilling-in-the-age-of-ai
Taylor, P. (2023, November 16). _Volume of data/information created, captured, copied, and consumed worldwide from 2010 to 2020, with forecasts from 2021 to 2025 (in zettabytes)_. Statista. https://www.statista.com/statistics/871513/worldwide-data-created/
