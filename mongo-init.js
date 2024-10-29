// mongo-init.js
db = db.getSiblingDB('chelle');

// Drop existing collections to ensure clean state
db.concepts.drop();
db.relationships.drop();

// Insert test concepts
db.concepts.insertMany([
    {
        "name": "User",
        "definition": "A User is an individual person who is using the product via a logged in account.",
        "citations": [
            "Users are managed externally to the product, via Clerk.",
            "Users can be either Mentors or Learners."
        ],
        "synonyms": ["Account Holder", "System User"],
        "created_at": "2024-10-28",
        "understanding_level": "Practical"
    },
    {
        "name": "Organization",
        "definition": "An Organization is a group of Users that use the product in tandem.",
        "citations": [
            "Organizations are managed externally to the product, via Clerk.",
            "It is not possible to use Chelle and not belong to an Organization"
        ],
        "synonyms": ["Company", "Team"],
        "created_at": "2024-10-28",
        "understanding_level": "Proficient"
    },
    {
        "name": "Brand",
        "definition": "The visual and tonal identity that represents the product across all touchpoints.",
        "citations": [
            "Brand guidelines are maintained in Figma",
            "All customer-facing content must adhere to brand guidelines"
        ],
        "synonyms": ["Identity", "Corporate Image"],
        "created_at": "2024-10-28",
        "understanding_level": "Practical"
    },
    {
        "name": "Sales Process",
        "definition": "The standardized approach for converting prospects into customers.",
        "citations": [
            "Sales process stages are configured in Hubspot",
            "Each stage has specific exit criteria that must be met"
        ],
        "synonyms": ["Sales Pipeline", "Sales Methodology"],
        "created_at": "2024-10-28",
        "understanding_level": "Proficient"
    }
]);

// Create indexes for concepts
db.concepts.createIndex({ "name": 1 }, { unique: true });

// Insert test relationships
db.relationships.insertMany([
    {
        "source": "User",
        "target": "Organization",
        "type": "Subsumption",
        "strength": 0.8,
        "created_at": "2024-10-28"
    },
    {
        "source": "Brand",
        "target": "Sales Process",
        "type": "Related",
        "connection_type": "Functional",
        "strength": 0.4,
        "created_at": "2024-10-28"
    },
    {
        "source": "User",
        "target": "Brand",
        "type": "Related",
        "connection_type": "Temporal",
        "strength": 0.4,
        "created_at": "2024-10-28"
    },
    {
        "source": "Organization",
        "target": "Sales Process",
        "type": "Related",
        "connection_type": "Causal",
        "strength": 0.4,
        "created_at": "2024-10-28"
    }
]);

// Create indexes for relationships
db.relationships.createIndex({ "source": 1, "target": 1 }, { unique: true });
db.relationships.createIndex({ "source": 1 });
db.relationships.createIndex({ "target": 1 });
db.relationships.createIndex({ "type": 1 });
db.relationships.createIndex({ "created_at": -1 });

// Add validation rules for the relationships collection
db.runCommand({
    collMod: "relationships",
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["source", "target", "type", "strength", "created_at"],
            properties: {
                source: {
                    bsonType: "string",
                    description: "Source concept name - required"
                },
                target: {
                    bsonType: "string",
                    description: "Target concept name - required"
                },
                type: {
                    enum: ["Equivalence", "Subsumption", "Overlap", "Related", "Disjoint", "None"],
                    description: "Type of relationship - required"
                },
                connection_type: {
                    enum: ["Causal", "Temporal", "Spatial", "Functional", null],
                    description: "Specific type of connection for Related relationships"
                },
                strength: {
                    bsonType: "double",
                    minimum: 0.0,
                    maximum: 1.0,
                    description: "Relationship strength (0-1) - required"
                },
                created_at: {
                    bsonType: "string",
                    description: "Creation date - required"
                }
            }
        }
    }
});

// mongo-operations-init.js

// Switch to the chelle database
db = db.getSiblingDB('chelle');

// Drop existing operational collections to ensure clean state
db.implementations.drop();
db.procedures.drop();
db.tools.drop();

// Create indexes and validation rules for implementations
db.createCollection("implementations", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "type", "description", "details", "concept", "status", "created_at"],
      properties: {
        name: {
          bsonType: "string",
          description: "Name of the implementation - required"
        },
        type: {
          enum: ["Design", "Configuration", "Integration", "Process"],
          description: "Type of implementation - required"
        },
        description: {
          bsonType: "string",
          description: "Description of the implementation - required"
        },
        details: {
          bsonType: "object",
          description: "Key-value pairs of implementation details - required"
        },
        concept: {
          bsonType: "string",
          description: "Related concept name - required"
        },
        status: {
          enum: ["Active", "Draft", "Archived"],
          description: "Current status - required"
        },
        created_at: {
          bsonType: "string",
          description: "Creation date - required"
        }
      }
    }
  }
});

// Insert sample implementations
db.implementations.insertMany([
  {
    name: "Primary Brand Colors",
    type: "Design",
    description: "Core brand color palette implementation in design system",
    details: {
      "Slate Blue": "#5B7C99",
      "Apricot": "#ED820E",
      "Background": "#FFFFFF",
      "Text": "#1A1A1A"
    },
    concept: "Brand",
    status: "Active",
    created_at: "2024-10-28"
  },
  {
    name: "Sales Pipeline Configuration",
    type: "Configuration",
    description: "Hubspot deal stages and automation setup",
    details: {
      "Prospecting": "10% probability",
      "Qualification": "25% probability",
      "Proposal": "50% probability",
      "Negotiation": "75% probability",
      "Closed Won": "100% probability",
      "Closed Lost": "0% probability"
    },
    concept: "Sales Process",
    status: "Active",
    created_at: "2024-10-28"
  }
]);

// Create indexes and validation rules for procedures
db.createCollection("procedures", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "description", "steps", "concept", "status", "created_at"],
      properties: {
        name: {
          bsonType: "string",
          description: "Name of the procedure - required"
        },
        description: {
          bsonType: "string",
          description: "Description of the procedure - required"
        },
        steps: {
          bsonType: "array",
          description: "Ordered list of procedure steps - required",
          items: {
            bsonType: "object",
            required: ["order", "description", "expected_duration"],
            properties: {
              order: {
                bsonType: "int",
                description: "Step order number"
              },
              description: {
                bsonType: "string",
                description: "Step description"
              },
              expected_duration: {
                bsonType: "string",
                description: "Expected duration (e.g., '30m', '2h')"
              }
            }
          }
        },
        concept: {
          bsonType: "string",
          description: "Related concept name - required"
        },
        status: {
          enum: ["Active", "Draft", "Archived"],
          description: "Current status - required"
        },
        created_at: {
          bsonType: "string",
          description: "Creation date - required"
        }
      }
    }
  }
});

// Insert sample procedures
db.procedures.insertMany([
  {
    name: "Lead Qualification Process",
    description: "Standard process for qualifying new sales leads",
    steps: [
      {
        order: 1,
        description: "Check company size and industry match",
        expected_duration: "30m"
      },
      {
        order: 2,
        description: "Verify budget authority",
        expected_duration: "1h"
      },
      {
        order: 3,
        description: "Score against ideal customer profile",
        expected_duration: "45m"
      },
      {
        order: 4,
        description: "Route to appropriate sales team",
        expected_duration: "15m"
      }
    ],
    concept: "Sales Process",
    status: "Active",
    created_at: "2024-10-28"
  },
  {
    name: "Brand Asset Creation",
    description: "Process for creating new brand assets",
    steps: [
      {
        order: 1,
        description: "Review brand guidelines",
        expected_duration: "1h"
      },
      {
        order: 2,
        description: "Create initial designs",
        expected_duration: "4h"
      },
      {
        order: 3,
        description: "Internal review and feedback",
        expected_duration: "2h"
      },
      {
        order: 4,
        description: "Revisions and finalization",
        expected_duration: "2h"
      }
    ],
    concept: "Brand",
    status: "Active",
    created_at: "2024-10-28"
  }
]);

// Create indexes and validation rules for tools
db.createCollection("tools", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "purpose", "type", "concepts", "status", "created_at"],
      properties: {
        name: {
          bsonType: "string",
          description: "Name of the tool - required"
        },
        purpose: {
          bsonType: "string",
          description: "Purpose of the tool - required"
        },
        type: {
          enum: ["Software", "Framework", "Service", "Hardware"],
          description: "Type of tool - required"
        },
        concepts: {
          bsonType: "array",
          items: {
            bsonType: "string"
          },
          description: "Array of related concept names - required"
        },
        integration_details: {
          bsonType: "object",
          description: "Integration-specific details"
        },
        status: {
          enum: ["Active", "Evaluation", "Deprecated"],
          description: "Current status - required"
        },
        created_at: {
          bsonType: "string",
          description: "Creation date - required"
        }
      }
    }
  }
});

// Insert sample tools
db.tools.insertMany([
  {
    name: "Figma",
    purpose: "Design system and brand asset management",
    type: "Software",
    concepts: ["Brand"],
    integration_details: {
      "Access Level": "Organization",
      "Primary Use": "Design System Management",
      "Key Features": ["Component Library", "Design Templates", "Collaboration"]
    },
    status: "Active",
    created_at: "2024-10-28"
  },
  {
    name: "HubSpot",
    purpose: "CRM and sales process management",
    type: "Software",
    concepts: ["Sales Process", "Organization"],
    integration_details: {
      "Access Level": "Enterprise",
      "Primary Use": "Sales Pipeline Management",
      "Key Features": ["Deal Tracking", "Automation", "Reporting"]
    },
    status: "Active",
    created_at: "2024-10-28"
  },
  {
    name: "Clerk",
    purpose: "User authentication and organization management",
    type: "Service",
    concepts: ["User", "Organization"],
    integration_details: {
      "Access Level": "Team",
      "Primary Use": "Authentication",
      "Key Features": ["SSO", "User Management", "Organization Management"]
    },
    status: "Active",
    created_at: "2024-10-28"
  }
]);

// Create indexes for all collections
db.implementations.createIndex({ "name": 1 }, { unique: true });
db.implementations.createIndex({ "concept": 1 });
db.implementations.createIndex({ "status": 1 });
db.implementations.createIndex({ "created_at": -1 });

db.procedures.createIndex({ "name": 1 }, { unique: true });
db.procedures.createIndex({ "concept": 1 });
db.procedures.createIndex({ "status": 1 });
db.procedures.createIndex({ "created_at": -1 });

db.tools.createIndex({ "name": 1 }, { unique: true });
db.tools.createIndex({ "concepts": 1 });
db.tools.createIndex({ "status": 1 });
db.tools.createIndex({ "created_at": -1 });