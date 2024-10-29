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