## PROPOSED WORK

This project proposes an innovative approach to automated knowledge extraction and ontology mapping, leveraging the power of Large Language Models (LLMs) and building upon 20+ years of education and AI engineering expertise. The proposed system integrates advanced Named Entity Recognition (NER), entity relation extraction, and ontology mapping to generate organization-specific ontologies. The Chelle Ubiquitous Language (CUL, Appendix I) serves as the foundation for domain modeling and knowledge representation, providing a standardized vocabulary for organizational domain modeling. The proposed system features LLM-based knowledge extraction and augmentation, relationship mapping between entities, and ontological mapping for entity overlap. Simple interfaces for document upload and refinement review will be built for the purpose of interacting with the AI system. A flexible data model supporting iterative refinements will be part of the solution.

*Chelle Ubiquitous Language. *The CUL (Appendix I) is the domain modeling schema – a standardized vocabulary for knowledge representation. We propose to update CUL to reflect the latest application model, Assets-Knowledge-Assessment-Instruction (AKAI). The CUL structure will be incorporated into the knowledge base schema. As we progress, the CUL will serve as a framework for validation and quality control. The user interface should be built around the CUL.

\*System Architecture.**\* **The proposed system architecture consists of four primary components:

- Jupyter Notebook Server
  - an interactive environment for testing and refining various model and prompt combinations
- Fast API Server
  - will handle model-to-model+prompt requests
  - each endpoint supporting a specific model+prompt combination
  - store of results in MongoDB
- Streamlit Frontend
  - document upload interface
  - inbox interface
- MongoDB
  - primary data store

*User Flow. *The user flow in our proposed system begins with the input of well-structured markdown files. These files require no special formatting. The system processes the documents through a series of steps – the core research deliverables. These steps include named entity extraction, definition extraction from source documents, LLM-based definition augmentation, relationship mapping between entities, and ontological mapping for entity overlap. The extracted and processed information is then organized into four primary entities: **concepts**, **definitions**, **relationships**, and **ontologies**. To support iterative refinement and user validation, we store these as refinements (concept refinements, definition refinements, relationship refinements, and ontology refinements). Users can review, accept, or reject these refinements. The current version of any entity is dynamically constructed by applying accepted refinement diffs successively.

*User Interface and Experience. *The user interface is simple and is solely to support this particular work. The **Upload Page** provides a simple text upload interface. The **Inbox Page**, which will be designed as one project deliverable allows users to actively curate their knowledge base. This page presents refinements for user review and action, allowing them to interact directly with the extracted knowledge and proposed changes. Users can view, accept, reject, or modify refinements.

_Access and APIs._ For this proof of concept (POC) the API will be built locally with no security. The specific APIs will be determined based on our research outcomes. These APIs will likely include endpoints for document upload, knowledge extraction, refinement submission, and knowledge base querying.

\*Out of Scope.**\* **Several aspects have been deliberately placed out of scope for this POC. Security measures, while crucial for a production system, will not be implemented in this phase. Scalability considerations are also out of scope, as our primary goal is to demonstrate the effectiveness of our knowledge extraction and ontology mapping approach rather than its performance at scale. Data visualization features are not included in this POC.

\*Technologies Used.**\* **Our proposed system leverages a variety of technologies. At the core of our architecture is Docker Compose, which we use to orchestrate our POC system. The primary programming language for implementation is Python. We make extensive use of libraries such as Instructor for structured outputs from language models and Streamlit for building the user interface. For our language model needs, we primarily utilize Claude-sonnet-3.5. To facilitate rapid development and code generation, we employ Cursor and Anthropic Claude.

### Methodology

Our methodology centers around an LLM-based approach, exclusively using large language models and carefully crafted prompts for knowledge extraction and ontology mapping. We conceptualize each prompt+LLM pair as a distinct "model," allowing for modular design and easy experimentation. By chaining multiple such models, we build our pipelines for knowledge base creation and curation. We will first investigate best practices in atomic-level prompting (zero-shot learning, few-shot learning, chain-of-thought, etc.), then investigate several key LLM flows, including named entity extraction, entity definition generation, extraction strategies from source documents, LLM-based augmentation processes, relationship mapping between entities, and ontological mapping for entity overlap.

*LLM-based Approach and Prompt Design. *In our LLM-based approach, we prioritize simplicity and modularity in prompt design. Each model is tasked with one simple, well-defined task, allowing for better control and interpretability of the results. This "one model, one simple task" philosophy enables us to create complex workflows by chaining together these simpler components. Our prompt design process focuses on clarity and specificity, ensuring that each prompt elicits the desired information or action from the language model. We will iterate on these prompts based on performance metrics and user (in this work, the researcher) feedback, continuously refining the approach.

*Existing System Interation. *Our proposed system is designed with integration in mind, assuming the existence of pre-existing systems for extracted and structured markdown. This means that a successful proof of concept can be integrated into an existing production application ecosystem without too much tech debt and effort from the engineering team.

*User Curation System. *Central to the design is the user curation system, which we believe is crucial for maintaining the accuracy and relevance of the extracted knowledge. The system revolves around a user inbox containing entity, definition, relation, and mapping change data. This inbox serves as the primary interface for user interaction with the system's outputs. We implement a change data capture mechanism for our main data types, allowing us to track and version all modifications to the knowledge base. The current state of the knowledge base can be reconstructed at any point by applying the sequence of approved changes. This approach not only ensures data integrity but also provides a clear audit trail of how the knowledge base has evolved over time. Users can review proposed changes, approve them as-is, approve with alterations, or reject them entirely. This collaborative curation process helps to combine the efficiency of automated extraction with the nuanced understanding of human experts, resulting in a more accurate and contextually appropriate knowledge base.

### Evaluation Methods

To rigorously assess the effectiveness of our proposed system, we will employ a multi-faceted evaluation approach. Primarily, we will focus on user inbox metrics as a direct measure of the system's practical utility. These metrics will include the rate of user-approved (again, in this work, the research will be the user) changes, changes approved with alterations, user rejections, and a categorized analysis of rejection reasons. This granular feedback will provide invaluable insights into the accuracy and relevance of our automated extractions and suggestions. Beyond these user-centric metrics, we will also track and analyze several system performance indicators. These will include processing time metrics to evaluate efficiency, coverage metrics to assess the comprehensiveness of our knowledge extraction, and consistency metrics to ensure uniformity across different runs and document types.

## DELIVERABLES

Deliverables will be structured using milestones. Milestone 1 after three weeks, milestone 2 after six weeks, and final deliverable after eight weeks.

_Milestone 1. _ The theme of milestone 1 is prompt research and the primary deliverable will be a **detailed report** on prompts selected and their performance. Additional deliverables will be the **code repo** containing the defined system architecture, the revised **Chelle Ubiquitous Language**, and a **code repo** containing all of our prompts.

Deliverables:

- prompt research report (primary)
- code repo for system
- Chelle Ubiquitous Language (revised)
- code repo for prompts

Key tasks include:

- developing and running local system
- prompt research
- testing and analyzing prompts

*Milestone 2. *The theme of milestone 2 is end-to-end delivery. The primary deliverable will be the evolved **code repo** and a **report** on the application with a **demo video**. Additional deliverables will be ui mocks and the database schema.

Deliverables:

- evolved code repo for system (primary)
- report on the application
- demo video
- ui mocks
- database schemas

Key tasks include:

- database configuration
- api development
- ui design and development

*Final Deliverable. *The theme of the final deliverable is the final report. This **final report** is the primary deliverable and will document the complete project. Net new aspects of this relative to previous milestones is including analysis of the user input collected by the UI. This report will contain all of the metrics collected and analysis of these metrics. Additional deliverables will be detailed **documentation**.

Final Deliverables:

- final report (primary)
- documentation
