# Chelle Knowledge Management System

A comprehensive system for managing organizational knowledge through concepts, relationships, and operational elements.

## Overview

Chelle Knowledge Management System is a web-based application that helps organizations structure, visualize, and maintain their knowledge base. The system is built with Python/FastAPI backend and Streamlit frontend, offering three main components:

1. **Concepts Management**

   - Define and organize organizational knowledge
   - Track definitions, citations, and understanding levels
   - Manage synonyms and related terms

2. **Relationships Management**

   - Create and visualize connections between concepts
   - Support different relationship types and strengths
   - Interactive network visualization
   - Track relationship evolution over time

3. **Operational Elements**
   - Implement concepts in practical contexts
   - Manage procedures, tools, and validations
   - Track operational status and coverage

## Technology Stack

- **Backend**: FastAPI + Anthropic Claude API
- **Frontend**: Streamlit
- **Database**: MongoDB
- **Visualization**: Plotly, NetworkX
- **Containerization**: Docker

## Installation

1. Clone the repository:

```bash
git clone [repository-url]
cd chelle-knowledge-management
```

2. Build and run with Docker:

```bash
docker-compose up --build
```

3. Access the application:
   - Frontend: http://localhost:8501
   - API: http://localhost:8000

## Project Structure

```
.
├── api/
│   ├── main.py
│   └── routers/
│       └── chat.py
├── docker/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── Home.py
│   ├── utils/
│   │   └── session_state.py
│   └── pages/
│       ├── 1_Concepts.py
│       ├── 2_Relationships.py
│       └── 3_Operational_Elements.py
└── prompts/
    ├── concept_definer.py
    ├── concept_identifier.py
    └── concept_researcher.py
```

## Features

### Concepts Management

- Create and edit concept definitions
- Track citations and sources
- Manage synonyms and understanding levels
- View concept history and evolution

### Relationships Management

- Create connections between concepts
- Multiple relationship types:
  - Equivalence (1.0)
  - Subsumption (0.8)
  - Overlap (0.6)
  - Related (0.4)
  - Disjoint (0.2)
- Connection types:
  - Causal
  - Temporal
  - Spatial
  - Functional
- Interactive network visualization
- Relationship strength metrics

### Operational Elements

- Implementations
  - Track practical applications of concepts
  - Manage implementation details and status
- Procedures
  - Define step-by-step processes
  - Link procedures to concepts
- Tools
  - Document tool usage and purpose
  - Connect tools to relevant concepts

## API Integration

The system integrates with Anthropic's Claude API for automated:

- Concept identification
- Definition synthesis
- Relationship suggestions

API endpoints are available at:

- `/api/chat`: Handle chat interactions
- Root endpoint (`/`): Health check

## Development

### Prerequisites

- Python 3.8+
- Docker
- AWS credentials (for Anthropic Bedrock)

### Local Development

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

2. Install dependencies:

```bash
pip install -r docker/requirements.txt
```

3. Run the development server:

```bash
streamlit run frontend/Home.py
```

### Environment Variables

Required environment variables:

- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION`: AWS region (default: us-east-1)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[License details to be added]

## Support

For support, please [contact information to be added]
