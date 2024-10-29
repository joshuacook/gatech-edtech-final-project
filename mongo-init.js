// mongo-init.js
db = db.getSiblingDB('chelle');

// Drop existing collections to ensure clean state
db.concepts.drop();

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

// Create indexes
db.concepts.createIndex({ "name": 1 }, { unique: true });